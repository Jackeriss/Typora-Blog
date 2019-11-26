## 从后端视角认识 GraphQL

2019-11-26 13:54:47

本文以一个后端开发者的视角去认识和学习 GraphQL，比较 SDL 优先和代码优先这两种 GraphQL 服务端开发方法，发现 GraphQL 的优势并分析目前存在的问题。最后对 GraphQL 的未来进行了展望。

### 什么是 GraphQL

GraphQL 既是一种用于 API 的查询语言也是一个满足你数据查询的运行时。 GraphQL 对你的 API 中的数据提供了一套易于理解的完整描述，使得客户端能够准确地获得它需要的数据，而且没有任何冗余，也让 API 更容易地随着时间推移而演进，还能用于构建强大的开发者工具。

![](https://i.loli.net/2019/11/03/aHRLVuiSE895CJy.gif)

以上便是 GraphQL 官网上对它的介绍。形象点说就是把服务器作为一个数据源，使用 GraphQL 接口就好像使用数据库的 SQL 语句一样，前端可以自由查询自己需要的数据。

### 为什么需要 GraphQL

大家都知道 RESTful 一直是行业中 API 接口的通用规范，那么 GraphQL 是在什么背景下诞生的？它又解决了传统 API 的哪些问题呢？

2012 年 Facebook 开发 GraphQL 的最初原因是移动用户的增加，当时的移动设备和网络性能很差，GraphQL 最小化了需要网络传输的数据量，从而极大地改善了在这些条件下运行的应用程序。而且 Facebook 的页面所需的接口数据十分复杂，用户之间的关注关系是网状的，使用 GraphQL 可以轻松实现递归关联查询。

![](https://i.loli.net/2019/11/03/3wUgiOYQatX9K6L.png)  ![](https://i.loli.net/2019/11/03/VmNi5KUq2P7Fpt3.png)

上面的图片对比了 RESTful API 与 GraphQL API 在查询用户详情页时的请求情况。可以看到， 使用 RESTful API 需要同时完成三个请求而 GraphQL 只需要一次请求。

然而，GraphQL 带来的好处远不止这些。随着移动互联网和前端技术的飞速发展，各种不同的前端框架和平台层出不穷，这使得构建和维护一个符合所有平台需求的 API 变得十分困难，而使用 GraphQL 每个客户端都可以精确地访问它所需要的数据。还有就是在产品快速迭代的过程中，对于 RESTful API，服务器公开数据的方式常常需要修改，以满足客户端的特定需求和设计更改，这阻碍了产品的快速开发和迭代。

### GraphQL 如何使用

和所有的 API 接口一样，你需要一个服务端和一个客户端，服务端主要包括 Schema 的定义和 Resolver（等价于传统 API 中的 Handler）。而客户端则要写不同场景下的查询语句。

#### 查询、变更与订阅

GraphQL 有三种操作，分别是 query（查询）、mutation（变更）和 subscription （订阅）

可以尝试一下这个[在线例子](https://www.graphqlbin.com/v2/6RQ6TM)，点击右侧的 `DOCS` 可以打开文档。

```graphql
{
  allPersons(orderBy: name_ASC) {
    name
    films {
      director
    }
  }
}
```

这些前端使用向的东西我就不做过多介绍了，可以参考 [GraphQL 官方教程](https://graphql.cn/learn/queries/)，下面着重介绍一下 GraphQL 的服务器开发。

#### Schema 和类型

GraphQL 的 Schema 定义有自己的一套语言，叫做 GraphQL SDL （GraphQL Schema Definition Language）。下面以一个博客程序的 Schema 定义为例：

```graphql
type Post {
  id: String!
  title: String!
  publishedAt: DateTime!
  likes: Int! @default(value: 0)
  blog: Blog @relation(name: "Posts")
}

type Blog {
  id: String!
  name: String!
  description: String
  posts: [Post!]! @relation(name: "Posts")
}
```

它主要定义了接口的字段和类型，其他信息包括默认值和关联关系等。这其实和数据库的 Schema 定义很像。

##### Type

Type （类型）有一个名字，并且可以实现一个或多个 Interface（接口）：

```graphql
type Post implements Item {
  # ...
}
```

##### Field

Field（字段）有一个名字和类型：

```graphql
age: Int
```

GraphQL 规范定义了一些内置标准类型，但可以通过具体实现来定义更多类型。内置的标准类型包括：

- Int

- Float

- String

- Boolean

- ID

在字段中除了使用标准类型外还可以使用任何在 Schema 中定义过的类型。

不可为空的字段通过在后面加 `!` 来表示：

```graphql
age: Int!
```

列表用方括号表示：

```graphql
names: [String!]
```

##### Enum

Enum（枚举）是具有一组指定值的标量：

```graphql
enum Category {
  PROGRAMMING_LANGUAGES
  API_DESIGN
}
```

##### Interface

在 GraphQL 中，接口是字段列表。 GraphQL 类型必须与其实现的所有接口都具有相同的字段，并且所有接口字段都必须具有相同的类型。

```graphql
interface Item {
  title: String!
}
```

##### Schema directive

Directive （指令）没有内在的含义。 每个 GraphQL 实现都可以定义自己的自定义指令，以添加新功能。

```graphql
name: String! @defaultValue(value: "new blogpost")
```

#### SDL 优先 vs 代码优先

##### GraphQL 服务器开发的演变

![](https://i.loli.net/2019/11/05/Ri1TysQZrELkCzm.jpg)

当 GraphQL 于 2015 年发布时，工具生态系统十分匮乏。只有官方[规范](https://facebook.github.io/graphql/)及其在 JavaScript 中的参考实现：[`graphql-js`](https://github.com/graphql/graphql-js)。直到今天，`graphql-js`仍在最流行的 GraphQL 服务器框架中被使用，如`apollo-server`，`express-graphql`和`graphql-yoga`。

使用`graphql-js`构建 GraphQL 服务器时，Schema 被定义为普通的 JavaScript 对象：

```js
const { GraphQLSchema, GraphQLObjectType, GraphQLString } = require('graphql')

const schema = new GraphQLSchema({
  query: new GraphQLObjectType({
    name: 'Query',
    fields: {
      hello: {
        type: GraphQLString,
        args: {
          name: { type: GraphQLString },
        },
        resolve: (_, args) => `Hello ${args.name || 'World!'}`,
      },
    },
  }),
})
```

从这些示例可以看出，使用`graphql-js`来创建 GraphQL 的 Schema 非常的冗长。而 Schema 的 SDL 表示则更加简洁，易于掌握：

```graphql
type Query {
  hello(name: String): String
}
```

为了简化开发并提高对实际 API 定义的可见性，Apollo 于 2016 年 3 月开始构建[`graphql-tools`](https://github.com/apollographql/graphql-tools)。目标是将 Schema 的定义与实际实现分开，从而诞生了当前流行的 SDL 优先（SDL-first）开发方法：

1. 在 GraphQL SDL 中手动编写 GraphQL Schema 定义
2. 实现所需的解析器功能

通过这种方法，上面的示例现在看起来像这样：

```js
const { makeExecutableSchema } = require('graphql-tools')

const typeDefs = `
type Query {
  hello(name: String): String
}
`

const resolvers = {
  Query: {
    hello: (_, args) => `Hello ${args.name || 'World!'}`,
  },
}

const schema = makeExecutableSchema({
  typeDefs,
  resolvers,
})
```

这些代码段与上面使用的代码 100％ 等效，不同之处在于它们更具可读性。

可读性不是 SDL 优先的唯一优势：

- 该方法**易于理解**，**非常适合快速构建**
- 由于每个新的 API 操作都首先需要在 Schema 中体现，因此 **GraphQL Schema 应优先设计**
- Schema 定义可以用作 **API 文档**
- Schema 定义可以用作**前端团队和后端团队之间**的**交流工具**，前端开发人员更多地参与了 API 设计
- Schema 定义可以**快速 mock API**

尽管 SDL 优先具有许多优势，但最近两年表明将其扩展到更大的项目具有挑战性。在更复杂的环境中会出现许多问题（我们将在下一节中详细讨论）。

实际上，这些问题实际上基本上可以解决——实际的问题是解决这些问题需要使用（和学习）许多其他工具。在过去的两年中，已经发布了无数工具，这些工具试图改善围绕 SDL 优先开发的工作流程：从编辑器插件，CLI 到语言库。

学习，管理和集成所有这些工具的开销减慢了开发人员的速度，并使其难以跟上 GraphQL 生态系统的步伐。

##### 分析 SDL 优先开发的问题

###### 问题1：模式定义和解析器之间的不一致

如果使用 SDL 优先，则 Schema 定义必须与 Resolver 程序实现的确切结构匹配。这意味着开发人员需要确保 Schema 定义始终与 Resolver 同步！

尽管即使对于小型 Schema 而言，这已经是一个挑战，但随着 Schema 增长到成百上千行（实际上，[GitHub 的 GraphQL Schema](https://gist.github.com/nikolasburk/15f30bb3e19e5bf8329ff52787fa72b5) 有超过一万行），这几乎变得不可能。

**工具 / 解决方案**：有一些工具可帮助保持 Schema 定义和 Resolver 同步。例如，通过使用诸如[`graphqlgen`](https://github.com/prisma/graphqlgen)或库的代码生成[`graphql-code-generator`](https://github.com/dotansimha/graphql-code-generator)。

###### 问题2：GraphQL Schema 的模块化

编写大型 GraphQL 模式时，通常不希望所有 GraphQL 类型定义都驻留在同一文件中。相反，您想将它们分成较小的部分（例如，根据功能或产品）。

**工具/解决方案**：类似[`graphql-import`](https://github.com/prisma/graphql-import)的工具或更新的[`graphql-modules`](https://graphql-modules.com/)库对此提供了帮助。`graphql-import`使用编写为 SDL 注释的自定义导入语法。`graphql-modules`是一个工具集，可帮助进行 Schema 分离，Resolver 组合以及为 GraphQL 服务器实现可伸缩结构。

###### 问题3：Schema 定义中的冗余（代码重用）

另一个问题是如何重用 SDL 定义。

当前没有工具可以解决此问题。开发人员可以编写自定义工具来减少重复代码的需求，但是目前该问题尚缺乏通用的解决方案。

###### 问题4：IDE 支持和开发人员经验

GraphQL 模式基于强大的类型系统，这可以在开发期间带来巨大的好处，因为它允许对代码进行静态分析。不幸的是，SDL 通常在程序中表示为纯字符串，这意味着该工具无法识别其中的任何结构。

然后，问题就变成了如何在编辑器工作流程中利用 GraphQL 类型来受益于诸如 SDL 代码自动完成和构建时错误检查之类的功能。

**工具 / 解决方案**：该[`graphql-tag`](https://github.com/apollographql/graphql-tag)库提供了`gql`将 GraphQL 字符串转换为 AST（抽象语法树） 的功能，因此可以进行静态分析以及随之而来的功能。除此之外，还有各种编辑器插件，例如 VS Code 的 [GraphQL](https://marketplace.visualstudio.com/items?itemName=Prisma.vscode-graphql) 或 [Apollo GraphQL](https://marketplace.visualstudio.com/items?itemName=apollographql.vscode-apollo) 插件。

##### 结论：SDL 优先可以工作，但需要无数的工具

在探究了问题领域和开发出解决问题的各种工具之后，似乎 SDL 优先的开发最终可以工作——但它也要求开发人员学习和使用大量其他工具。

##### SDL 优先忽略编程语言的个别特征

SDL 优先的另一个有问题的方面是，无论使用哪种编程语言，它都通过施加相似的原理而忽略了编程语言的各个功能。

代码优先方法在其他语言中确实非常有效：Scala 库[`sangria-graphql`](https://github.com/sangria-graphql/sangria)利用 Scala 强大的类型系统来优雅地构建 GraphQL 模式，并[`graphlq-ruby`](https://github.com/rmosolgo/graphql-ruby)使用了 Ruby 语言的许多很棒的DSL 功能。

#### 代码优先

##### 你唯一需要的工具是编程语言

大多数 SDL 优先问题来自以下事实：我们需要将手动编写的 SDL 模式映射到编程语言。这种映射是导致需要其他工具的原因。如果我们遵循以 SDL 优先的道路，则需要为每种语言生态系统重新设计所需的工具，并且每种工具的外观也将有所不同。

与其使用更多的工具来增加 GraphQL 服务器开发的复杂性，我们应该争取一种更简单的开发模型。理想的情况是，开发人员可以利用他们已经在使用的编程语言——这就是代码优先的想法。

##### 什么是代码优先？

还记得在中定义 Schema 的最初示例`graphql-js`吗？这就是“ 代码优先”。没有任何手动维护的 Schema 定义，而是从实现该 Schema 的代码生成了 SDL 。

尽管`graphql-js`非常冗长，但其他语言中有许多流行的框架都基于代码优先方法工作，例如已经提到的，以及适用于 Python 或 Elixir 的框架：[`graphlq-ruby`](https://github.com/rmosolgo/graphql-ruby) [`sangria-graphql`](https://github.com/sangria-graphql/sangria) [`graphene`](https://github.com/graphql-python/graphene) [`absinthe-graphql`](https://github.com/absinthe-graphql/absinthe)

##### 实践中的代码优先

使用代码优先的框架构建 GraphQL Schema 的例子：

```ts
const Query = objectType('Query', t => {
  t.string('hello', {
    args: { name: stringArg() },
    resolve: (_, { name }) => `Hello ${name || `World`}!`,
  })
})

const schema = makeSchema({
  types: [Query],
  outputs: {
    schema: './schema.graphql'),
    typegen: './typegen.ts',
  },
})
```

通过这种方法，可以直接在 TypeScript / JavaScript 中定义 GraphQL 类型。借助智能的代码补全功能，可以在定义它们时提示可用的 GraphQL 类型，字段和参数。

定义所有 GraphQL 类型后，会将它们传递到函数中以创建[`GraphQLSchema`](https://graphql.org/graphql-js/type/#graphqlschema)——可在 GraphQL 服务器中使用的实例。通过指定`ouputs`，可以定义所生成的 SDL 和类型应该位于何处。

##### 无需所有工具即可获得 SDL 的好处

之前我们列举了 SDL 优先开发的好处。实际上，在使用代码优先方法时，无需折中大多数。

以 GitHub GraphQL API 为例：GitHub 使用 Ruby 和代码优先的方法来实现其 API。SDL 模式定义是基于实现 API 的代码生成的。但是，Schema 定义仍被纳入版本控制中。这使得在开发过程中跟踪 API 的更改变得异常容易，并改善了各个团队之间的沟通。

API 文档等其他好处也不会因代码优先方法而丢失。

### GraphQL 的更多优势

在“为什么需要 GraphQL ”部分我已经介绍了许多 GraphQL 相对于传统 API 的优势，但 GraphQL 的优势远不止这些。下面我再介绍几个 GraphQL 比较明显的优势：

#### 版本控制

使用 REST API，通常会看到许多带有 v1 或 v2 的 API。这些在 GraphQL 中并不需要，因为你可以通过添加或删除类型来改进 API。

在 GraphQL 中，你所需要做的就是写新代码。可以编写新类型、查询和修改，而无需维护其他版本的 API。

#### 接口校验

显而易见，由于强类型的使用，我们对收到的数据进行检验的操作变得更为容易和严格，自动化的简便度和有效性也大大提高。对 query 本身的结构的校验也相当于是在Schema 完成后就自动得到了，所以我们甚至不需要再引入任何别的工具或者依赖，就可以很方便地解决所有的 validation。

#### 接口文档

前面提到，由于 GraphQL 的 Schema 已经定义了字段和类型，正常情况后端不必再提供额外的接口文档，一些 GraphQL 的工具自带了文档展示功能，例如 [graphql-playground](https://github.com/prisma-labs/graphql-playground) 和 [graphiql](https://github.com/graphql/graphiql)。流行的 GraphQL 框架中都集成了这些工具，这很大程度上提升了 GraphQL 的开发体验，也提高了前后端的沟通效率，这在前后端分离的架构下是很重要的。

#### 自动生成代码

无论是 SDL 优先的从 SDL 生成代码还是代码优先的从代码生成 SDL 都还只是开发流程上的简化，还是需要自己写Resolver 才能使用，而类似 [prisma](https://www.prisma.io/) 的项目已经可以让你直接将数据库变成一个 GraphQL Server，无需手写 Resolver，他会自动生成常见的查询方法。

### GraphQL 的劣势与难点

#### 性能

一个 RESTful 应用，由于每个 API 的确定性，我们可以针对每一个 API 的逻辑，非常好的优化它们的性能，所以就算存在一定程度的 Overfetching / Underfetching，前后端的性能都可以保持在能够接受的范围内。然而想要更普适性一些的 GraphQL，则可能会因为一个层级结构复杂而且许多域都有很大数据量的 Query 跑许多个Resolvers，使得数据库的查询性能成为了瓶颈。使用 [DataLoader](https://github.com/graphql/dataloader) 可以在一定程度上解决这个问题。

#### 缓存

在 RESTful 等基于 URL 的 API 中，客户端可以根据 URL 使用 HTTP 缓存。这些 API 中的 URL 就是全局唯一标识符。而 GraphQL 是单入口的 API，无法用 URL 实现缓存。
GraphQL 中提供 Global ID 字段作为全局唯一标识符。可以将一个字段（如 id）保留为全局唯一标识符，例如`"id": "MDEwOlJlcG9zaXRvcnk2MDE4MTY4OA=="`。
如果后端使用类似 UUID 的标识符，那么直接暴露这个全局唯一 ID 即可。如果后端并没有给每个对象分配全局唯一 ID，则 GraphQL 层需要构造此 ID。

#### 资源与速率限制

对于 RESTful 请求，简单的限制请求次数即可。而对于 GraphQL，一个复杂的 GraphQL 调用可能等同于数千个 RESTful 请求，而一个简单的 GraphQL 调用可能只等同于一两个 RESTful 请求。

为了准确地计算一个查询带来的服务器负载，GitHub 的 GraphQL API v4 根据标准化点数（normalized scale of points）来计算速率限制分数（rate limit score）。每个 GraphQL 请求的分数，由父连接及其子节点上 的 first 和 last 参数决定。

- 客户必须为每个 connection 提供 first 或 last 参数。
- first 或 last 参数的取值范围在 1-100 之间。
- 每一个独立调用最多可以请求 50 万个节点。

查询：

```graphql
query {
  viewer {
    repositories(first: 50) {
      edges {
        repository:node {
          name

          issues(first: 10) {
            totalCount
            edges {
              node {
                title
                bodyHTML
              }
            }
          }
        }
      }
    }
  }
}
```

计算：

```svg
50       = 50 repositories
+
50 x 10  = 500 repository issues

         = 550 total nodes
```

- 公式使用父连接及其子级上的 first 和 last 参数来预先计算 GitHub 系统（如MySQL，ElasticSearch 和 Git）上的潜在负载。

- 每个新连接都有自己的点数。这个点数与请求中的其他点数合并为一个总体的速率限制分数（rate limit score）。

- GraphQL API v4 速率限制是每小时 5000 点。

请求：

```graphql
query {
  viewer {
    login
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
```

响应：

```json
{
  "data": {
    "viewer": {
      "login": "kikajack"
    },
    "rateLimit": {
      "limit": 5000,
      "cost": 1,
      "remaining": 4999,
      "resetAt": "2018-01-21T04:42:30Z"
    }
  }
}
```

#### 生态

尽管 GraphQL 有着很好的社区支持，但本质上使用 GraphQL，就等于要使用 React 与 NodeJS，其他语言和框架的成熟度和社区活跃度都比较低。

### 总结

GraphQL 是 API 的未来吗？至少在数据聚合和网关层是的。当然 Restful 也不会被完全替代，只是今后提到开放 API 不再只有 Restful 这一种选项了。

### 参考文献

- [GraphQL SDL — Schema Definition Language](https://www.prisma.io/blog/graphql-sdl-schema-definition-language-6755bcb9ce51)

- [The Problems of "Schema-First" GraphQL Server Development](https://www.prisma.io/blog/the-problems-of-schema-first-graphql-development-x1mn4cb0tyl3/)

- [GraphQL resource limitations](https://developer.github.com/v4/guides/resource-limitations/)
