## 使用 Elasticsearch 前你需要知道的几件事

2020-06-01 09:33:06

#### Elasticsearch 真的有他们说的那么好吗？

![image.png](https://i.loli.net/2020/06/16/7D6ELQWuxspHelJ.png)

这件事我和鲁迅的看法一样。Elasticsearch 可以说是有口皆碑，尤其是近几年，几乎成为了搜索引擎数据库的代名词。作为新一代实时搜索分析引擎，它补足了许多传统搜索引擎和分析引擎的短板。这大大的拓宽了它的应用场景，在日志监控分析等新兴场景十分流行。

#### 何时需要 Elasticsearch？

![image.png](https://i.loli.net/2020/06/15/VL8hWPcjCnuTe7X.png)

|      | MySQL            | Redis          | HBase            | Elasticsearch          |
| ---- | ---------------- | -------------- | ---------------- | ---------------------- |
| 类型 | 关系型           | key-value      | 列式存储         | 搜索引擎               |
| 优点 | 事务支持         | 高性能读写     | 海量数据读写     | 支持复杂查询           |
| 缺点 | 复杂查询支持较差 | 不支持复杂查询 | 复杂查询支持较差 | 资源消耗高，不支持事务 |

每个数据库都是针对特定的使用场景来设计的。如果一个数据库很流行，那么它一定在某个场景下十分的优秀。而 Elasticsearch 就是实时搜索分析场景下的 NO.1。这些数据库之间并不是竞争关系，而是优势互补。比如，由于 ES 在事务和关联关系等方面的功能缺陷，就常常与传统的关系型数据库配合使用。

至于 ES 的资源消耗究竟有多恐怖，分享一组我们公司的数据：

| 集群 | 节点配置   | 数据节点数 | 可搜索文档数 | 每分钟请求数   | CPU 使用率 |
| ---- | ---------- | ---------- | ------------ | -------------- | ---------- |
| 搜索 | 36 核 72 G | 8          | 1 亿         | 2 万 ~ 18 万   | 0% ~ 20%   |
| 评论 | 16 核 64 G | 2          | 1700 万      | 2.5 万 ~ 35 万 | 4% ~ 45%   |

#### 如果不用 Elasticsearch 呢?

既然 ES 这么耗资源，除了 ES 还有哪些数据库可以帮我们处理复杂查询?

![image.png](https://i.loli.net/2020/06/16/zAQYOEXDmJs5lK3.png)

|          | MongoDB                                          | RediSearch | Solr                       | Elasticsearch                   |
| -------- | ------------------------------------------------ | ---------- | -------------------------- | ------------------------------- |
| 优点     | 简单、高效、灵活                                 | 资源消耗低 | 查询速度快                 | 功能全面、Restful API、扩展性强 |
| 缺点     | 部分功能欠缺                                     | 功能简单   | 写入影响查询速度、配置繁杂 | 资源消耗高、写入默认有1S 延迟   |
| 优势场景 | 日志监控信息、地理位置信息、数据可视化、简单聚合 | 简单搜索   | 传统搜索、推荐系统         | 上述所有场景                    |

ES 在处理复杂查询时的优势还是很明显的，如果你想要一个全面的解决方案，ES 基本可以满足。

MongoDB 也能实现 ES 使用场景下的许多功能，但由于不是专业的搜索引擎，某些复杂的查询和聚合就显得特别棘手。

RediSearch 实际用的比较少，比较适合小型项目比如博客程序使用。

老牌的搜索引擎 Solr 在正常情况下的查询速度比 ES 要快很多，但在有索引写入时查询的性能会大幅度下降。因此一般不会实时构建索引，而是采用定时构建。比较适合用于对实时性要求不高的类似百度、谷歌这种传统搜索引擎。

#### Elasticsearch 的 "Elastic" 体现在什么地方？

##### 弹性

"Elastic" 的意思是“弹性”，Elasticsearch 的弹性主要体现在其集群支持弹性扩容，具体架构如下：

首先明确一下几个基本概念：

**分片（shard）**：分片是 ES 中的最小工作单元，每个分片都是一个 Lucene 实例。文档保存在分片内，分片又被分配到集群内的各个节点里。

**主分片（primary shard）**：一个分片可以是主分片或者副本分片。 索引内任意一个文档都归属于一个主分片，所以主分片的数目决定着索引能够保存的最大数据量。

**副本分片（replica shard）**：一个副本分片只是一个主分片的拷贝。副本分片作为硬件故障时保护数据不丢失的冗余备份，并为搜索和返回文档等读操作提供服务。

在索引建立的时候就已经确定了主分片数，但是副本分片数可以随时修改。

![拥有两个节点的集群](https://i.loli.net/2020/06/16/jhdTg4QqWYaVSNn.png)

图中我们的集群有两个节点，只有一个索引，这个索引有三个主分片和三个副本分片。

![拥有三个节点的集群](https://i.loli.net/2020/06/16/sVYTGWZxu3Kop2F.png)

这时候如果我们新增一个节点，Elasticsearch 集群会为了分散负载而对分片进行重新分配。

因为我们的索引总共只有 6 个分片，所以最大只能有效扩容到 6 个节点，让每个分片独享一个节点的资源。如果想要扩容到 6 个以上的节点就需要增加副本数了。

![拥有2份副本分片3个节点的集群](https://i.loli.net/2020/06/16/7ZrWsIYVFfcqXtQ.png)

先将每个主分片的副本数改为两个，接下来就可以将节点扩容到 9 个了。

注意：主分片数在索引建立时设置好就不能变了，在节点数不变的情况下增加副本数性能不但不会提升，反而还会降低，因为每个分片从节点上获得的资源会变少。但是更多的副本数提高了数据冗余量：按照上面的节点配置，我们可以在失去 2 个节点的情况下不丢失任何数据。

##### 灵活

"Elastic"还有另一层意思“灵活”，Elasticsearch 的灵活性主要体现在即便你不预先指定索引中字段的类型 Elasticsearch 也能够自动识别，这一特性被称作 Schema-free。这点和 MongoDB 很像，在日志监控场景下尤其有用。因为不管你的日志中有什么样的内容，ES 都会用合适的类型建立索引。不仅是基础类型，像日期和 IP 这种也能自动识别。当然你也可以禁用该功能保证文档数据按你的定义构建索引。

#### 一个复杂的查询包括什么？

打开我们 APP 的商品搜索结果页就知道了。

![image.png](https://i.loli.net/2020/06/08/HyYOiVXTpmkKgqb.png)

可以看到一个复杂的查询可以大概拆分为四类子需求：**查询 / 过滤 / 排序 / 聚合**。

这里实际上有两个查询：一个是通过聚合查询得到有结果的筛选项，另一个则是真正展示查询结果的查询，并且可以应用刚才通过聚合得到的过滤条件。

##### 查询（Query）与过滤（Filter）	


| 查询类型 | 含义                                             | 字段类型                                             | 查询语句                                                     | 布尔查询          |
| -------- | ------------------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------ | ----------------- |
| 查询     | 有多匹配？（计算相关度评分）                     | 全文（full text） eg: text（经过了 Analyzer 的处理） | [full text queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html) eg: match / match_phrase…… | must  / shoud     |
| 过滤     | 匹配还是不匹配？（计算布尔值，不影响相关度评分） | 词语（term） eg: keyword / long / date……             | [term-level queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/term-level-queries.html) eg: term / range / exists…… | must_not / filter |

此处的查询特指评分查询。过滤查询相比评分查询要简单的多，通常速度也更快，结果会被缓存在内存中。过滤能够减少需要通过评分查询检查的文档。因此，应尽可能多的使用过滤查询，仅在需要计算相关性时使用评分查询。

##### 排序（Sort）

相关性排序：按相关性评分，也就是 _score 字段的值进行排序，查询结果默认是按相关性排序的。

字段值排序：按指定字段的值排序。

多级排序：按一定的优先级应用多个排序条件。

##### 聚合（Aggregation）

聚合（Aggregation）：聚合得到的是数据的概览，而非数据本身。如果将搜索比作大海捞针，那聚合就是在回答“大海里有多少针？”、“针的平均长度是多少？”、“每月加入到海中的针有多少？”这类问题。

桶（Bucket）：满足特定条件的文档的集合，类似 SQL 中的 分组 GROUP BY。

指标（Metrics）：对桶内的文档进行统计计算，类似 COUNT()、SUM()、MAX() 等统计方法。

#### 支线任务

以上就是 ES 中最核心的几个概念了，接下来可以根据自己的需要选择支线任务了。

#####搜索引擎

如果想做传统的搜索引擎就要研究一下分析器和全文查询了，底层涉及自然语言处理和倒排索引。

##### 数据可视化

而如果你想做数据可视化则需要用到各种各样的聚合，包括嵌套聚合、直方图聚合、日期直方图聚合等。比如，计算多个商品的评分时候就用到了嵌套聚合，需要先进行一次桶聚合，就是将评价按商品 id 聚合，然后再对每个桶的评分指标进行平均聚合。这样就得到每个商品的平均评分了。直方图聚合就更高级了，比如你有一堆数值范围是 1 ~ 100 的数据，然后你告诉它以 10 为间隔进行直方图聚合，它就会返回 0 ~ 10 有多少，10 ~ 20 有多少。日期直方图聚合也是类似的，只不过你要告诉它间隔的时间是多少，比如以 1 天为间隔，或者一分钟等等，这在数据可视化中可以说是最常见的场景了。

搜索引擎和数据可视化是 ES 最典型的两个使用场景，如果深入研究下去都非常的有趣。

#### 关注细节

虽然 ES 总体上用起来非常的顺手，但是也有许多细节需要我们注意，我简单总结了一些：

##### 设置（Setting）

分片数和副本数：前面介绍 ES 的弹性扩容的时候提到了分片数和节点配置决定了索引的最大存储量，副本数会影响高可用和查询性能，这两个设置要和节点数匹配。

refresh 时间间隔：新添加的文档是不能立刻被搜索到的，因为写入物理磁盘 fsync 操作耗时较久，ES 有一个文件系统缓存，这里面的数据也是可搜索的，ES 为了提高搜索的实时性，最新的操作不会直接写入磁盘，而是默认每隔一秒钟从内存索引缓冲区写入文件系统缓存，然后还有个 translog 来记录这些操作，每隔 30 分钟或者 translog 满了的时候会执行一次 flush 操作，将文件系统缓存的数据写入到磁盘，并且清空 translog。refresh 操作虽然比 flush 消耗低，但还是会有性能消耗，因此 ES 默认设置了一秒间隔而不是每次写入都 refresh。如果你更看重索引的构建速度而对实时性要求不高，就可以把 refresh 间隔调低甚至关闭，比如需要大量写入索引的时候。

最大结果窗口：ES 的分页和 MySQL 类似，比如你设置每页返回 10 条，当你查询第 100 页时 ES 会把前 1000 条 符合条件的都找出来并排序再去除前 990 条，因此分页越大查询性能越差而且有可能导致 OOM。因此 ES 有一个最大分页结果的配置，默认是10000，超过之后就不再返回结果了。我们应该在产品逻辑层就尽量避免使用大分页，有些场景可以考虑用 [Scroll](https://www.elastic.co/guide/en/elasticsearch/reference/7.x/search-request-body.html#request-body-search-scroll) 和 [Search After](https://www.elastic.co/guide/en/elasticsearch/reference/7.x/search-request-body.html#request-body-search-search-after) 的方式代替 from + size 的分页，从而避免这个问题。

##### 映射（Mapping）

各字段是否需要索引、是否需要保存原始数据、是否需要分析器处理。

##### 查询（Query）

根据 mapping 设置的字段类型选择合适的查询语句、特定情况下的聚合应指定使用广度优先。

深度优先聚合：先构建完整的树，然后修剪无用节点。

广度优先聚合：先执行第一层聚合， 再继续下一层聚合之前会先做修剪。

虽然 ES 的细节很多，但这也正体现了它足够”灵活“，足够 "Elastic"。在你了解了这些细节之后你便能让 ES 更好的服务于你的需求，灵活即强大。

#### 出发

好了，以上就是使用 Elasticsearch 前你需要知道的几件事了，在出发之前我再送你一份通关指南：[Elasticsearch: 权威指南](https://www.elastic.co/guide/cn/elasticsearch/guide/cn/index.html)。愿风指引你的道路！