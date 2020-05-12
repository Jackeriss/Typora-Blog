## Elasticsearch 常见问题解决方案

2020-04-27 16:14:10

最近用 Elasticsearch 重构了 Club Factory 的评论存储模型，在实际使用过 Solr 和 Elasticsearch 之后不得不说还是 Elasticsearch 更胜一筹，使用更简单，功能更丰富。下面介绍两个在使用 ES 时几乎不可避免会遇到的几个问题，以及我采用的解决方案。

**Q：如何在写入 ES 时对数据进行一些处理？**

A：我们可以利用 Ingest 节点在索引建立前对文档进行预处理，首先我们需要在 Ingest 节点创建一个 pipeline，这个 pipeline 中包含了我们想要进行的处理流程：

> PUT  /_ingest/pipeline/order_comment_json

```json
{
  "description": "Parse JSON",
  "processors": [
    {
      "json": {
        "field": "ratings"
      }
    },
    {
      "json": {
        "field": "images"
      }
    }
  ]
}
```

在这个例子中，ratings 和 images 是以 JSON 字符串形式存在数据库中的，为了能对其中的内容建立索引，需要在建立索引前解析 JSON 并将结果存至对应的字段。这样在 mapping 中这两个字段就可以设为 JSON 解析后的结构而不是 keyword 了。ES 提供了非常多的 processor 任君选择：https://www.elastic.co/guide/en/elasticsearch/reference/7.6/ingest-processors.html

**Q：如何修改索引的 mapping 又不影响线上正常查询？**

A：修改还是不要想了，问就是重建。ES 中的字段类型在索引建立后就不支持修改了，你只能新增字段或者搞个新的 mapping 重建索引（reindex）。那么重建索引具体怎么做才能做到无缝迁移呢？

假设我们当前的索引叫 A，现在线上不断的有新的数据写入 A。如果我们直接从 A 新建 B，然后切换到 B 必然会丢失重建索引期间新增的数据。为了解决这个问题，我的方案如下：

首先我们使用 index template 来定义 mapping 时可以设置一个包含通配符（wildcard）的 Index pattern，以评论数据为例，我设置的 Index pattern 是`order_comment*`。这样我们第一次建立的索引可以叫`order_comment_1`，如果我们要进行 reindex 那新的索引叫`order_comment_2`就行了。

然后为了能够从旧 index 丝滑切换至新的 index，我们要为索引起一个别名，在查询的时候我们不直接指定真实的index 名，而要使用别名。例如，我为 `order_comment_1` 设置了别名为 `comment`。

做好这些准备工作后，reindex 就只需要简单的三步：

1. 切换写 index 为`order_comment_2`（这样新增的数据就写入了新的 index 中）

2. 执行 reindex 操作

   > POST  /_reindex?wait_for_completion=false

   ```json
   {
     "source": {
       "index": "order_comment_1"
     },
     "dest": {
       "index": "order_comment_2",
       "pipeline": "do_nothing"
     }
   }
   ```

   注1：加上 wait_for_completion=false 后你的任务会异步执行，它会返回一个 task_id，然后你可以通过

   > GET   /_tasks/<task_id>

   来查看任务的进度。你也可以通过请求

   > POST  /_tasks/<task_id>/cancel

   来终止任务。

   注2：这里指定的 pipeline `do_nothing` 是我创建的一个什么都不做的 pipline，不指定的话 reindex 的时候也会应用模板中设置的 pipline。

3. 将`order_comment_1`的别名`comment`去掉，同时给`order_comment_2`加上别名`comment`

   > POST  /_aliases

   ```json
   {
     "actions": [
       {"remove": {"index": "order_comment_1", "alias": "comment"}},
       {"add": {"index": "order_comment_2",  "alias": "comment"}}
     ]
   }
   ```
   
   至此，读和写就都迁到新的 index `order_comment_2`上了，旧索引`order_comment_1`就可以删掉了，而这个过程对于用户而言几乎是无感知的，唯一的不足是 reindex 的过程中无法查询到这期间新增的数据，而这点在评论的场景下完全是可以容忍的。如果 reindex 需要较长时间这个方案还可以进一步优化：即在将写入的index 切换为`order_comment_2` 之前先进行一次 reindex 并指定同步到一个最近的时间戳。在大部分历史数据都同步完之后再进行上面的三个步骤，只是第二次 reindex 的时候只同步之前同步的时间戳之后的数据即可。这样可以最大限度的减少 reindex 对查询的影响。

**Q：分页查询超过 10000 个文档后无结果怎么办？**

A：ES 通过 from + size 分页默认只能返回前 10000 个结果，因为 ES 分页的实现和数据库的 limit 类似，要取第10000 ~ 10010 条结果需要把前 10010 条结果都取出来再把前 10000 条去掉。不同的是 ES 的索引有可能有多个分片，那么则需要把每个分片的前 10010 条结果汇总再排序然后取 10000 ~ 10010 条，性能可想而知。不过如果觉得 10000 实在不够也可以稍微调整一下，修改索引的`index.max_result_window`配置即可。但是也不能调的太大，否则一次大分页的查询就有可能导致 OOM。实际上，一般分页场景用户往往都是关注前几页的数据，大分页在产品设计上完全可以屏蔽掉。不过 ES 还是提供了 [Scroll](https://www.elastic.co/guide/en/elasticsearch/reference/7.x/search-request-body.html#request-body-search-scroll) 和 [Search After](https://www.elastic.co/guide/en/elasticsearch/reference/7.x/search-request-body.html#request-body-search-search-after) 两种方式来专门解决深分页的问题。这几种方式各有优劣，使用哪种方式还需要根据需求和性能综合考虑。

注：和 mapping 一样，如果你的索引已经建好了就无法直接修改索引的配置了，要么先关闭索引，修改完再打开索引，要么修改索引模板的配置，然后重建索引。由于关闭索引需要占用大量的磁盘空间，可能会对现有环境造成问题，AWS 的 ES 服务将关闭索引的 API 禁用掉了。

