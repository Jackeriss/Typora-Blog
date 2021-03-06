## Kafka 基础概览

2019-09-15 22:22:32

![](https://i.loli.net/2019/10/22/Ssm6YgbQlUawEGR.jpg)

部分内容取自 [Kafka 官方文档](http://kafka.apachecn.org/)

### 架构概览

![](https://i.loli.net/2019/09/15/dIWvMTNEOJwXqYS.png)

### 基本概念

#### Broker

在消息队列中处理存储消息的服务器一般被称为 Broker（经纪人），目的是与 Producer（生产者） 和 Consumer（消费者）区分。

#### Topic

Topic 就是数据主题，是数据记录发布的地方，可以用来区分业务系统。Kafka 中的 Topic 总是多订阅者模式，一个 Topic 可以拥有一个或者多个消费者来订阅它的数据。（物理上不同 Topic 的消息分开存储，逻辑上一个 Topic 的消息虽然保存于一个或多个 Broker 上，但用户只需指定消息的 Topic 即可生产或消费数据而不必关心数据存于何处）。

#### 分区日志与 Offset

对于每一个 Topic， Kafka 集群都会维持一个分区日志，如下所示：

![](https://i.loli.net/2019/09/15/nFYfJlyNSbwzj1O.png)

每个 Topic 包含一个或多个分区（Partition）。每个分区都是有序且顺序不可变的记录集，并且不断地追加到结构化的 commit log 文件。分区中的每一个记录都会分配一个 ID 来表示顺序，称作 offset，offset 用来唯一的标识分区中每一条记录。

Kafka 只保证分区内的记录是有序的，而不保证主题中不同分区的顺序。如果你需要总记录在所有记录的上面，可使用仅有一个分区的主题来实现，但这意味着每个消费者组只有一个消费者线程（下面介绍 Consumer 与 Consumer Group 时有解释原因）。

事实上，在每一个消费者中唯一保存的元数据是 offset（偏移量）即消费在日志中的位置。偏移量由消费者所控制：通常在读取记录后，消费者会以线性的方式增加偏移量，但是实际上，由于这个位置由消费者控制，所以消费者可以采用任何顺序来消费记录。例如，一个消费者可以重置到一个旧的偏移量，从而重新处理过去的数据；也可以跳过最近的记录，从“现在”开始消费。

这些细节说明 Kafka 消费者是非常廉价的——消费者的增加和减少，对集群或者其他消费者没有多大的影响。比如，你可以使用命令行工具，对一些 Topic 内容执行 tail 操作，并不会影响已存在的消费者消费数据。

日志中的分区有以下几个用途：第一，当日志大小超过了单台服务器的限制，允许日志进行扩展。每个单独的分区都必须受限于主机的文件限制，不过一个主题可能有多个分区，因此可以处理无限量的数据。第二，可以作为并行的单元集。

#### Leader 与 Follower

日志的分区分布在 Kafka 集群的服务器上。每个服务器在处理数据和请求时，共享这些分区。每一个分区都会在已配置的服务器上进行备份，确保容错性。每个分区都有一台 Broker 作为 Leader，零台或者多台 Broker 作为 Follwer 。Leader 处理一切对分区的读写请求，而 Follower 只需被动的同步 Leader 上的数据。当 Leader 宕机了，Follower 中的一台服务器会自动成为新的 Leader。每台 Broker 都会成为某些分区的 Leader 和某些分区的 Follower，因此集群的负载是平衡的。

![](https://i.loli.net/2019/09/15/BhXU5fCGrTpHO1e.png)

#### Producer

生产者（Producer）可以将数据发布到所选择的 Topic 中。生产者负责将记录分配到 Topic 的哪一个分区中。可以使用循环的方式来简单地实现负载均衡，也可以根据某些语义分区函数（例如：记录中的 key）来完成。

#### Consumer 与 Consumer Group

消费者（Consumer）使用一个消费组（Consumer Group）名称来进行标识，发布到 Topic 中的每条记录被分配给订阅消费组中的一个消费者实例。消费者实例可以分布在多个进程中或者多个机器上。

如果所有的消费者实例在同一消费组中，消息记录会负载均衡到每一个消费者实例。

如果所有的消费者实例在不同的消费组中，每条消息记录会广播到所有的消费者进程。

![](https://i.loli.net/2019/09/15/7R4sFLC1qyfXjWv.png)

多个消费者消费同一个 Topic 时，同一条消息只会被同一消费者组内的一个消费者所消费。而数据并非按消息为单位分配，而是以分区为单位分配，即同一个分区的数据只会被一个消费者所消费。如果消费者的个数多于分区的个数，那么会有部分消费者无法消费该 Topic 的任何数据，也就是说，当消费者个数超过分区数后，增加消费者并不能增加并行度。分区数决定了最大并行度。所以，如果你的分区数是 N，那么最好线程数也保持为 N，这样通常能够达到最大的吞吐量。超过 N 的配置只是浪费系统资源，因为多出的线程不会被分配到任何分区。

### 与 RabbitMQ 等对比

> 从功能维度上来说，RabbitMQ 的优势要大于 Kafka，但是 Kafka 的吞吐量要比 RabbitMQ 高出 1 至 2 个数量级，一般 RabbitMQ 的单机 QPS 在万级别之内，而 Kafka 的单机 QPS 可以维持在十万级别，甚至可以达到百万级。
> 
> Kafka 设计之初是为日志处理而生，给人们留下了数据可靠性要求不要的不良印象，但是随着版本的升级优化，其可靠性得到极大的增强，详细可以参考 KIP101。就目前而言，在金融支付领域使用 RabbitMQ 居多，而在日志处理、大数据等方面 Kafka 使用居多，随着 RabbitMQ 性能的不断提升和 Kafka 可靠性的进一步增强，相信彼此都能在以前不擅长的领域分得一杯羹。
> 
> 这里还要提及的一个方面是扩展能力，这里我狭隘地将此归纳到可用性这一维度，消息中间件的扩展能力能够增强其用可用能力及范围，比如前面提到的 RabbitMQ 支持多种消息协议，这个就是基于其插件化的扩展实现。还有从集群部署上来讲，归功于 Kafka 的水平扩展能力，其基本上可以达到线性容量提升的水平，在 LinkedIn 实践介绍中就提及了有部署超过千台设备的 Kafka 集群。

总体来看，功能和功能扩展性：RabbitMQ > Kafka，性能和性能扩展性：Kafka > RabbitMQ，可靠性 Kafka ≈ RabbitMQ。

#### 相关链接

- [消息中间件选型分析：从 Kafka 与 RabbitMQ 的对比看全局](https://www.infoq.cn/article/kafka-vs-rabbitmq)

- [Kafka、RabbitMQ、RocketMQ 发送小消息性能对比](http://jm.taobao.org/2016/04/01/kafka-vs-rabbitmq-vs-rocketmq-message-send-performance/)

- [Kafka vs RocketMQ——Topic 数量对单机性能的影响](http://jm.taobao.org/2016/04/07/kafka-vs-rocketmq-topic-amout/)

- [Kafka vs RocketMQ——多 Topic 对性能稳定性的影响](http://jm.taobao.org/2016/04/20/kafka-vs-rocketmq-3/)

- [业界主流 MQ 对比](http://jm.taobao.org/2016/03/24/rmq-vs-kafka/)

### 监控

比较流行的 Kafka 监控系统有 Kafka Manager, Kafka Monitor, Kafka Offset Monitor, Burrow, Chaperone, Confluent Control Center 等。常用监控指标如下：

| 监控指标    | 含义                                   |
| ------- | ------------------------------------ |
| logSize | 已经写到该分区的消息数                          |
| offset  | 该分区已经消费的消息数                          |
| lag     | 该分区还有多少消息未消费（lag = logSize - offset） |

### spring-kafka 重要配置

#### 设置 producer 是否需要 broker 的反馈

可以设置的值为：`all, -1, 0, 1`

- 0：producer不会等待 broker 发送 ack，无法保证服务器已收到记录。

- 1：当 leader 接收到消息后发送 ack，如果 leader 在确认记录后宕机，但在将数据复制到所有的副本服务器之前，则记录将会丢失。

- -1 或 all：当所有的 follower 都同步消息成功后发送 ack，这保证了只要至少一个同步副本服务器仍然存活，记录就不会丢失，这是最强有力的保证。

```
spring.kafka.producer.acks = all
```

#### 设置 producer 的失败重试次数

设置大于 0 的值将使客户端重新发送任何数据，一旦这些数据发送失败。允许重试将潜在的改变数据的顺序，如果这两个消息记录都是发送到同一个 partition，则第一个消息失败第二个发送成功，则第二条消息会比第一条消息出现要早。

```
spring.kafka.producer.retries = 1000
```

#### 设置 producer 数据压缩类型

可以设置的值为`none、gzip、snappy`，默认是`none`

压缩最好用于批量处理，批量处理消息越多，压缩性能越好。

```
spring.kafka.producer.compression-type = gzip
```

#### 设置 consumer 的 group-id

可以根据环境不同使用不同的 group-id ，方便区分。

```
spring.kafka.consumer.group-id = xxx
```

#### 设置 consumer 在无 offset 时的行为

当 Kafka 中没有初始偏移或当前偏移在服务器上不再存在时（例如，因为该数据已被删除），该怎么办

- earliest：自动将偏移重置为最早的偏移
- latest：自动将偏移重置为最新偏移
- none：如果没有为消费者组找到以前的偏移，则向消费者抛出异常

可以设置的值为`latest, earliest, none`，默认是`latest`

```
spring.kafka.consumer.auto-offset-reset = earliest
```

#### 设置 consumer 提交模式

- 自动提交
  
  ```
  spring.kafka.consumer.enable-auto-commit = true
  ```
  
  这种方式也被称为`at most once`，获取到消息后就可以更新 offset，无论是否消费成功。

- 手动提交
  
  ```
  spring.kafka.consumer.enable-auto-commit = false
  ```
  
  这种方式称为`at least once`。获取到消息后，等消费完成再调用`commitSync()`方法 ，手动更新 offset。如果消费失败，则 offset 也不会更新，此条消息会被重复消费一次。如果消费者保证幂等性，则即便会有重复消息也影响不大。当然也可以通过事务实现`exactly once`。
  
  手动提交又有好几种方式：
  
  - RECORD：每处理一条 commit 一次
  - BATCH（默认）：每次 poll 的时候批量提交一次，频率取决于 poll 的频率
  - TIME：每次间隔 ackTime 的时间去 commit
  - COUNT：累积达到 ackCount 次的 ack 去 commit
  - COUNT_TIME：ackTime 或 ackCount 哪个条件先满足，就 commit
  - MANUAL：listener 负责 ack，但是背后也是批量提交上去的
  - MANUAL_IMMEDIATE：listener 负责 ack，每调用一次，就立即 commit
  
  一般设置为 listener 立即 commit，此设置只有设置`spring.kafka.consumer.enable-auto-commit = false`时才会生效。
  
  ```
  spring.kafka.listener.ack-mode = MANUAL_IMMEDIATE
  ```

#### 设置在 consumer 侦听器容器中运行的线程数

```
spring.kafka.listener.concurrency = 5
```

#### 设置 consumer 一次拉取消息的个数

默认为 500，当消息处理耗时较长或开销较大时应调小。

```
spring.kafka.consumer.max-pull-records = 1
```

#### 相关链接

[spring-kafka 生产者消费者配置详解](https://www.cnblogs.com/yx88/p/11013338.html)

### 推荐文章

[Kafka 设计解析](http://www.jasongj.com/tags/Kafka/)

[深入浅出理解基于 Kafka 和 ZooKeeper 的分布式消息队列](https://gitbook.cn/books/5ae1e77197c22f130e67ec4e/index.html)
