## Elasticsearch 常见问题解决方案

2020-04-27 16:14:10

最近用 Elasticsearch 重构了 Club Factory 的评论存储模型，在实际使用过 Solr 和 Elasticsearch 之后不得不说还是 Elasticsearch 更胜一筹，使用更简单，功能更丰富。下面介绍两个在使用 ES 时几乎不可避免会遇到的两个问题，以及我采用的解决方案。

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

   > POST  /_reindex

   ```json
   {
     "source": {
       "index": "order_comment_1"
     },
     "dest": {
       "index": "order_comment_2",
   		"pipeline": "xpack_monitoring_7"
     }
   }
   ```

   注：这里指定的 pipeline `xpack_monitoring_7` 是 ES 自带的一个 processer 为空的什么事情也不做的pipeline，如果不指定的话会使用 index template 中设置的 pipeline。因为我们的数据源已经是经过 JSON 解析后的结构了，如果再解析一遍的话会报错，当然如果在 redindex 的时候需要做一些数据处理也可以指定其他的 pipeline。（`GET /_ingest/pipeline`可以查看所有可用的 pipeline，我就是看到有个现成的 pipeline`xpack_monitoring_7`下面一个 processor 都没有就直接用它了，如果没有的话就自己建一个）

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