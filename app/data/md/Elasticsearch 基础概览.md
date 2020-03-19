## Elasticsearch 基础概览

2020-03-19 17:47:44

Elasticsearch 是当前[最流行](https://db-engines.com/en/ranking/search+engine)的搜索引擎数据库，本文会着重介绍 Elasticsearch 中搜索相关的一些基本概念，了解这些在你深入学习 Elasticsearch 之前是很有必要的。

#### Elastic Stack (ELK)

![image-20200310171250641](https://i.loli.net/2020/03/10/2vynuFqULMaPJ5Y.png)

在介绍 Elasticsearch 之前，我们先来简单了解一下 Elastic Stack。相比 Elastic Stack，人们还是更常用它之前的名字：ELK。ELK 是三个开源项目的首字母缩写，这三个项目分别是：Elasticsearch、Logstash 和 Kibana。Elasticsearch 是一个搜索和分析引擎。Logstash 是服务器端数据处理管道，能够同时从多个来源采集数据，转换数据，然后将数据发送到诸如 Elasticsearch 等“存储库”中。Kibana 则可以让用户在 Elasticsearch 中使用图形和图表对数据进行可视化。ELK 后来因为加入了新项目 Beats 就改名为 Elastic Stack，Beats 是一系列轻量型的单一功能数据采集器。

#### Elasticsearch 的特点

![image-20200310180733260](https://i.loli.net/2020/03/10/OFxCVzZi6aNkr31.png)

实时性能好 / 高可用 / 易扩展 / 分布式 / 多租户 / RESTful API / 自动识别 Schema / 开源 / 基于 Lucene……

可以看到 Elasticsearch 的优点有很多，这也是它之所以这么流行的原因。

#### 精确值（Exact value）与全文（Full-text）

Elasticsearch 中的数据可以概括的分为两类：**精确值**和**全文**。

精确值如它们听起来那样精确。例如日期或者用户 ID，但字符串也可以表示精确值，例如用户名或邮箱地址。对于精确值来讲，`Foo` 和 `foo` 是不同的，`2014` 和 `2014-09-15` 也是不同的。

另一方面，全文是指文本数据（通常以人类容易识别的语言书写），例如一个推文的内容或一封邮件的内容。

精确值很容易查询。结果是二进制的：要么匹配查询，要么不匹配

查询全文数据要微妙的多。我们问的不只是“这个文档匹配查询吗”，而是“该文档匹配查询的程度有多大？”换句话说，该文档与给定查询的相关性如何？

我们很少对全文类型的域做精确匹配。相反，我们希望在文本类型的域中搜索。不仅如此，我们还希望搜索能够理解我们的意图：

- 搜索 `UK` ，会返回包含 `United Kindom` 的文档。
- 搜索 `jump` ，会匹配 `jumped` ， `jumps` ， `jumping` ，甚至是 `leap` 。
- 搜索 `johnny walker` 会匹配 `Johnnie Walker` ， `johnnie depp` 应该匹配 `Johnny Depp` 。
- `fox news hunting` 应该返回福克斯新闻（ Foxs News ）中关于狩猎的故事，同时， `fox hunting news` 应该返回关于猎狐的故事。

针对这类在全文域中的查询，Elasticsearch 首先会**分析**文档，之后再根据结果创建**倒排索引**。

#### 倒排索引（Inverted index）

Elasticsearch 使用一种称为**倒排索引**的结构，它适用于快速的全文搜索。一个倒排索引由文档中所有不重复词的列表构成，对于其中每个词，有一个包含它的文档列表。

例如，假设我们有两个文档，每个文档的 `content` 域包含如下内容：

1. The quick brown fox jumped over the lazy dog
2. Quick brown foxes leap over lazy dogs in summer

为了创建倒排索引，我们首先将每个文档的 `content` 域拆分成单独的词（我们称它为 `词条` 或 `tokens` ），创建一个包含所有不重复词条的排序列表，然后列出每个词条出现在哪个文档。结果如下所示：

| Term   | Doc_1 | Doc_2 |
| ------ | ----- | ----- |
| Quick  |       | √     |
| The    | √     |       |
| brown  | √     | √     |
| dog    | √     |       |
| dogs   |       | √     |
| fox    | √     |       |
| foxes  |       | √     |
| in     |       | √     |
| jumped | √     |       |
| lazy   | √     | √     |
| leap   |       | √     |
| over   | √     | √     |
| quick  | √     |       |
| summer |       | √     |
| the    | √     |       |

现在，如果我们想搜索 `quick brown` ，我们只需要查找包含每个词条的文档：

| Term      | Doc_1 | Doc_2 |
| --------- | ----- | ----- |
| brown     | √     | √     |
| quick     | √     |       |
| **Total** | **2** | **1** |

两个文档都匹配，但是第一个文档比第二个匹配度更高。如果我们使用仅计算匹配词条数量的简单 *相似性算法* ，那么，我们可以说，对于我们查询的相关性来讲，第一个文档比第二个文档更佳。

但是，我们目前的倒排索引有一些问题：

- `Quick` 和 `quick` 以独立的词条出现，然而用户可能认为它们是相同的词。
- `fox` 和 `foxes` 非常相似, 就像 `dog` 和 `dogs` ；他们有相同的词根。
- `jumped` 和 `leap`，尽管没有相同的词根，但他们的意思很相近。他们是同义词（Synonyms）。

使用前面的索引搜索 `+Quick +fox` 不会得到任何匹配文档。（记住，`+` 前缀表明这个词必须存在。）只有同时出现 `Quick` 和 `fox` 的文档才满足这个查询条件，但是第一个文档包含 `quick fox` ，第二个文档包含 `Quick foxes` 。

我们的用户可以合理的期望两个文档与查询匹配。我们可以做的更好。

如果我们将词条规范为标准模式，那么我们可以找到与用户搜索的词条不完全一致，但具有足够相关性的文档。例如：

- `Quick` 可以小写化为 `quick` 。
- `foxes` 可以词干提取（Stemming）——变为词根的格式——为 `fox` 。类似的， `dogs` 可以为提取为 `dog` 。
- `jumped` 和 `leap` 是同义词，可以索引为相同的单词 `jump` 。

现在索引看上去像这样：

| Term   | Doc_1 | Doc_2 |
| ------ | ----- | ----- |
| brown  | √     | √     |
| dog    | √     | √     |
| fox    | √     | √     |
| in     |       | √     |
| jump   | √     | √     |
| lazy   | √     | √     |
| over   | √     | √     |
| quick  | √     | √     |
| summer |       | √     |
| the    | √     | √     |

这还远远不够。我们搜索 `+Quick +fox` 仍然会失败，因为在我们的索引中，已经没有 `Quick` 了。但是，如果我们对搜索的字符串使用与 `content` 域相同的标准化规则，会变成查询 `+quick +fox` ，这样两个文档都会匹配！

这非常重要。你只能搜索在索引中出现的词条，所以索引文本和查询字符串必须标准化为相同的格式。

分词和标准化的过程称为**分析**。

#### 分析（Analysis）与分析器（Analyzer）

分析包含下面的过程：

- 首先，将一块文本分成适合于倒排索引的独立的词条
- 之后，将这些词条统一化为标准格式以提高它们的“可搜索性”，或者召回率（recall）

分析器执行上面的工作。分析器实际上是将三个功能封装到了一个包里：

- **字符过滤器（Character Filter）**

  首先，字符串按顺序通过每个字符过滤器 。他们的任务是在分词前整理字符串。一个字符过滤器可以用来去掉 HTML，或者将 `&` 转化成 `and`。

- **分词器（Tokenizer）**

  其次，字符串被分词器分为单个的词条。一个简单的分词器遇到空格和标点的时候，可能会将文本拆分成词条。一个分析器必需且只可包含一个分词器 

- **词元过滤器（Token filter）**

  最后，词条按顺序通过每个词元过滤器 。这个过程可能会改变词条（例如，小写化 `Quick` ），删除词条（例如， 像 `a`， `and`， `the` 等无用词），或者增加词条（例如，像 `jump` 和 `leap` 这种同义词）。一个分析器可包含 0 个或多个词元过滤器，多个词元过滤器按配置顺序进行过滤。

#### 查询（Query）与过滤（Filter）

##### 过滤查询（Filtering queries）

- 是否匹配？匹配或不匹配（找出匹配的文档即可，无需计算相关度）
- 结果会被缓存到内存中以便快速读取，一般情况下比评分查询性能好
- 用于不需要相关性得分的场景，针对 non-analyzed 数据

##### 评分查询（Scoring queries）

- 有多匹配？（不仅要找出匹配的文档，还要计算每个匹配文档的相关性）
- 计算相关性使得它们比过滤查询费力的多，一般情况下比过滤查询性能差
- 用于全文搜索等需要相关性得分的场景，针对 analyzed 数据

#### 参考文献

[Elasticsearch: 权威指南](https://www.elastic.co/guide/cn/elasticsearch/guide/cn/index.html)

