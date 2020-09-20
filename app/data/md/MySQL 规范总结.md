## MySQL 规范总结

2020-07-20 13:07:34

### <div class="a">一、建库规范

1. 库命名规范：
   1. 库名称必须控制在 25 个字符以内
   2. 库名与应用名称尽量一致，库的命名规则必须契合所属业务的特点</div>
   3. 库名用小写（尽量不要使用除下划线、小写英文字母之外的其他字符，如果要用下划线，应该尽量保持一致的风格）
2. 字符集规范：创建数据库时必须显示指定字符集，建议使用 utf8mb4 字符集：CREATE DATABASE xxxxxx DEFAULT CHARACTER SET utf8mb4。 MySQL 5.5.3 之后增加 utf8mb4 编码，utf8mb4 是utf8 的一个扩展。许多新类型的字符，例如 emoji 这种类型的符号，utf8 不支持存储，但 utf8mb4 支持。所以，设计数据库时如果想要允许用户使用特殊符号，最好使用 utf8mb4 编码来存储，使得数据库有更好的兼容性。可参考官方说明：https://dev.mysql.com/doc/refman/5.5/en/charset-unicode-utf8mb4.html

### 二、建表规范

1. 表命名规范：
   1. 表命名做到专业、简洁、见名知意，多使用专业词汇命名，不使用拼音，以使用方便记忆、描述性强的可读性名称为第一准则，应尽量避免使用缩写或代码来命名
   2. 表命名必须使用小写字母或数字，禁止出现数字开头，禁止两个下划线中间只出现数字，应该尽量保持一致的风格。正例：aliyun_admin，rdc_config，level3_name ；反例：AliyunAdmin，rdcConfig，level_3_name
   3. 命名不要过长（应尽量少于25个字符）
   4. 禁止使用数字开头，禁止使用关键字或保留字，可参考官方说明：https://dev.mysql.com/doc/refman/5.7/en/keywords.html
   5. 同一个应用(或领域)下的表需要有相同的前缀名称，如：acticity_share、acticity_order、activity_item；同一个数据库下有不同的应用模块，则可以考虑对表名用不同的前缀标识
   6. 备份表命名时加上时间标识
   7. 相关模块的表名与表名之间尽量体现 JOIN 的关系，如 user 表和 user_login 表
   8. 表命名加上“业务名称_表的作用”，如：alipay_task / force_project / trade_config
2. 表注释规范：
   1. 每个表建立时必须加上表描述，如：COMMENT='履约单商品表'，方便参考理解、维护管理
3. 存储引擎规范：
   1. 若没有特殊要求，存储引擎均采用默认的 InnoDB（ENGINE=InnoDB）
4. 数据表存储格式规范：
   1. ROW_FORMAT 没有特殊需求时默认即可，不需要指定。ROW_FORMAT=Dynamic/Compressed只有在innodb_file_format=barracuda的情况下才支持，如果强制设置了，后续再对表进行DDL操作时会产生警告：#1 Execute(Warning, Code 1478):InnoDB: ROW_FORMAT=DYNAMIC requires innodb_file_format > Antelope. #2 Execute(Warning, Code 1478):InnoDB: assuming ROW_FORMAT=COMPACT
5. 表字符集规范：
   1. 若没有特殊要求，统一设置为 utf8mb4，即 CHARSET=utf8mb4。关联查询时，若字符集不一致，可能会导致索引失效
6. 主键规范：
   1. 每个表建立时必须设置主键 id（PRIMARY KEY (\`id\`)），自增长（AUTO_INCREMENT）、步长为1，类型为整型（根据需要选择 INT 或 BIGINT。一般情况下业务表使用 BIGINT 类型，防止数据量增长后自增主键值不够用；对于数据量不会增长很多的配置表，可使用 INT 类型）

### 三、字段规范

1. 字段命名规范：

   1. 字段命名要做到专业、简洁，做到见名知意，多使用专业词汇命名，不使用拼音，以使用方便记忆、描述性强的可读性名称为第一准则，应尽量避免使用缩写或代码来命名
   2. 字段名必须使用小写字母或数字，禁止出现数字开头，禁止两个下划线中间只出现数字，应该尽量保持一致的风格。正例：aliyun_admin，rdc_config，level3_name ；反例：AliyunAdmin，rdcConfig，level_3_name
   3. 命名不要过长（应尽量少于25个字符）
   4. 禁止使用数字开头，禁止使用 MySQL 关键字，MySQL 官方保留字：https://dev.mysql.com/doc/refman/5.7/en/keywords.html
   5. 注意字段类型的一致性、命名的一致性，同一个字段在不同的表中也应是相同的类型或长度，方便大家理解（如用户 ID，都用user_id，就不需要再造一个 member_id；如创建时间统一命名为 create_time，更新时间统一命名为 update_time）
   6. 表达是与否概念的字段，必须使用 is_xxx 的方式命名，数据类型是 unsigned tinyint（1 表示是，0 表示否）。正例：表达逻辑删除的字段名 is_deleted，1 表示删除，0 表示未删除

2. 字段注释规范：

   1. 字段注释必须加上（如 `product varchar(100) NOT NULL DEFAULT '' COMMENT '商品名称'`），字段取值范围含义、枚举常量等注释必须加上，方便参考理解、维护管理
   2. 字段注释规范：修改字段含义或对字段表示的状态追加时，需要及时更新字段注释

3. 字段默认值规范：

   1. 尽量将字段设置成 NOT NULL DEFAULT xxx。可为 NULL 的列使得索引、索引统计和值都比较复杂，InnoDB 使用单独的位（bit）存储 NULL 值，当可为 NULL 的列被索引时，每个索引记录需要一个额外的字节，所以会占用更多的存储空间，在MyISAM 引擎中，NULL 值会使索引失效。另外，使用 NULL 值之后，SQL 的复杂度变大，会使优化器更难以优化 SQL，如下 SQL 所示，如果 box_type 有默认值，则 SQL 不需要用 OR 来关联：

      ```sql
      SELECT
          idle_sku.sku_id,
          sum(1) AS stocked_sum
      FROM
          idle_sku
          LEFT JOIN box_sku ON box_sku.id = idle_sku.box_id
      WHERE
          idle_sku.status NOT IN ('IDLE_TRASH')
          AND (
              box_sku.box_type = 1
              OR box_sku.box_type IS NULL
          )
      GROUP BY
          idle_sku.sku_id;
      ```

   2. 在对字段进行 count() 统计时，值为 NULL 的不会被 count 统计进去，即当字段值为 NULL 时，count(*) 和 count(字段) 值是不一样的

   3. 字段默认值规范：当前字段为 NULL 时，更改字段时不必要再 NOT NULL DEFAULT xxx，因为数据量过多，改动成本过大，可能会对磁盘 IO 造成过多压力，阻塞其他进程

4. 字段顺序规范：

   1. 表的字段顺序很重要，从前到后，按照字段的重要性和使用频率排列，create_time、update_time、remark 等字段在最后。按字段的分类归集排列，如金额相关的字段在一块，时间相关的字段在一块等。以方便查看、排查问题（注：增加字段时不采用after 和 first 关键字，原因是数仓增量采集数据时无法感知 after 的位置，如果在表中间位置加字段，会使数仓同步数据失败）

5. 字段拆分规范：

   1. 考虑使用垂直分区。比如，我们可以把大字段或使用不频繁的字段分离到另外的表中，这样做可以减少表的大小，让表执行得更快。我们还可以把一个频繁更新的字段放到另外的表中，因为频繁更新的字段会导致 MySQL Query Cache 里相关的结果集频繁失效，可能会影响性能。需要留意的一点是，垂直分区的目的是为了优化性能，但如果将字段分离了到分离表后，又经常需要建立连接，那可能就会得不偿失了，所以，我们要确保分离的表不会经常进行连接，这时，用程序进行连接是一个可以考虑的办法

### 四、字段数据类型规范

1. 设计字段有一个基本的原则，保小不保大，也就是一般情况应该尽量使用可以正确存储数据的最小数据类型，更小的数据类型执行速度通常更快，因为它们占用更小的磁盘、内存和 CPU 缓存，处理时需要的 CPU 周期也更小

2. 整型：

   1. 在 MySQL 中支持的 5 个主要整数类型是 tinyint、smallint、mediumint、int、bigint，下表列出了各种数值类型以及它们的允许范围和占用的内存空间：

      | 类型      | 字节 | 最小值~最大值（有符号）                              | 最小值~最大值（无符号）      |
      | :-------- | :--- | :--------------------------------------------------- | :--------------------------- |
      | tinyint   | 1    | -128~127                                             | 0~255                        |
      | smallint  | 2    | -32 768~32 767                                       | 0~65 535                     |
      | mediumint | 3    | -8 388 608~8 388 607                                 | 0~16 777 215                 |
      | int       | 4    | -2 147 483 648~2 147 483 647                         | 0~4 294 967 295              |
      | bigint    | 8    | -9 223 372 036 854 775 808~9 223 372 036 854 775 807 | 0~18 446 744 073 709 551 615 |

   2. 建议使用 unsigned（无符号类型）存储非负值，这样数值范围可以扩大一倍，例如 tinyint 的取值范围为-127~128，unsigned tinyint 的取值范围为0~255

   3. 建议使用无符号整型存储 IPV4（IP地址），可以使用 inet_aton()、inet_ntoa() 函数进行转换，基本上没必要使用 char 类型来存储。例如，使用 inet_aton('172.16.23.16') 将 IP 转化成整数值 2886735632，使用 inet_ntoa(2886735632) 可得到 IP 值172.16.23.16

   4. 整型定义中不添加显示长度的值，比如使用 INT，而不是 INT(4)

   5. 使用更短小的列，比如短整型，整型列的执行速度往往更快。年龄、性别、状态、删除标记等枚举类型：可以用 tinyint 来存放，它只占用 1 个字节，unsigned tinyint 可以表示 0~255 的范围，基本够用

   6. 手机号：通常我们在存储手机号时，喜欢用 varchar 类型。假设是 11 位的手机号，用 utf8 编码。如果使用字符串存储，每位需要 3 个字节，一共需要 11*3=33 个字节；如果使用 bigint，只需要 8 个字节

   7. 能用整型的就用整型而不用字符型，如下反面示例中状态值完全可以用整型替代，从数据库读取之后再做释义即可：

      1. `\`status\` varchar(32) NOT NULL DEFAULT 'IDLE_UNALLOCATED' COMMENT '状态: IDLE_UNALLOCATED,IDLE_TO_SHELVE, IDLE_SHELVED, IDLE_OCCUPIED, IDLE_TO_OFF_SHELF,IDLE_TRASH, IDLE_FIN'`

3. 浮点型：

   1. 存储精确浮点数（如金额）时必须使用 decimal 替代 float 和 double，float 和 double 可能会存在精度损失的问题
   2. decimal 存在额外的存储和计算开销，在数据量非常大时可以用 bigint 代替：将数据乘以 100 万存储使用时再除以 100 万

4. 字符类型：

   1. char 和 varchar 是我们常用的字符类型。char(n) 用来记录固定长度的字符，长度最大为 255，比指定长度大的值将被截短，而比指定长度小的值将会用空格进行填补。varchar(n) 用来保存可变长度的字符，只存储字符串实际需要的长度，varchar 使用额外的 1～2 字节来存储值的长度，如果列的最大长度小于或等于 255 则使用 1 字节，否则就是用2字节。char 和 varchar 占用的字节数，根据数据库的编码格式不同而不同。latin1 占用 1 个字节，gbk 占用 2 个字节，utf8 占用 3 个字节
   2. 用法方面，如果存储的内容是可变长度的，如家庭住址、用户描述等就可以用 varchar；如果内容是固定长度的，例如：uuid（36 位）、md5 加密串（32 位）等就可以使用 char 存放；如果存储的字符串长度几乎相等，使用 char ；如果存储的字符串长度差别大，使用 varchar
   3. 字符串存储能用 varchar 就不要用 text，varchar 长度不要超过 5000，存储搜索性能均高于 text，text 查询时会产生临时磁盘文件，性能差。如果字符串长度超过 5000 需要使用 text 类型存储，则建议独立出来一张表，用主键来对应，避免影响其它字段索引效率。MySQL 把 text 值当作一个独立的对象处理，存储引擎在存储时通常会做特殊处理，当 text 值过大时，InnoDB 会使用专门的外部存储区域来进行存储，此时每个值在行内需要 1-4 个字节存储一个指针，然后在外部存储区域存储实际的值
   4. 慷慨是不明智的，最好的策略是只分配真正需要的空间。如使用 varchar(5) 和 varchar(200) 存储 'hello' 的空间开销是一样的，但是 varchar(200) 会消耗更多的内存，因为 MySQL 通常会分配固定大小的内存块来保存内部值，尤其是使用内存临时表进行排序或操作时会特别糟糕，在利用磁盘临时表进行排序时也同样糟糕。
   5. 字段数据类型的选择要方便以后扩展。一般扩展性有限的常量类型，建议用整型，性能高、占空间少，比如状态字段；一般不确定扩展性的类型，建议用字符型，可以添加业务规则，一个字段可以同时表示多种含义
   6. 在 varchar(n) 中，N表示的是字符数而不是字节数，比如 varchar(255)，最大可存储 255 个汉字。需要根据实际的宽度来选择 n。此外，n 应尽可能地小，因为在 MySQL 的一个表中，所有的 varchar 字段的最大长度是 65535 个字节，进行排序和创建临时表一类的内存操作时，会使用 n 的长度申请内存（对于这一点，MySQL 5.7后有了改进）
   7. 字符型详解参考链接：[字符类型详解](http://wiki.yuceyi.com/pages/viewpage.action?pageId=43959039)

5. JSON 类型（MySQL 5.7.8 以后才支持）：

   1. 存储 JSON 字符串时选用 JSON 类型，而不要选 varchar、text 类型存储
   2. JSON 类型的意义：
      1. 保证了 JSON 数据类型的强校验，JSON 数据列会自动校验存入此列的内容是否符合 JSON 格式，非正常格式则报错，而varchar 类型和 text 等类型不存在这种机制
      2. 更优化的存储格式，存储在 JSON 列中的 JSON 数据会被转成内部特定的存储格式，允许快速读取
      3. MySQL 同时提供了一组操作 JSON 类型数据的内置函数
      4. 可以基于JSON格式的特征支持修改特定的键值（即不需要把整条内容拿出来放到程序中遍历然后寻找替换再塞回去，MySQL 内置的函数允许你通过一条 SQL 语句就能搞定）

6. 时间类型：

   1. 存储年时使用 year 类型，存储日期时使用 date 类型，存储时间时使用 time 类型，date 保存精度到天，格式为：YYYY-MM-DD，如2019-11-07
   2. 时间类型的精度统一到毫秒级别，毫秒的格式类似为：2019-11-07 10:58:27.257，定义方法：datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)，datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
   3. 建议使用 datetime 类型存储日期时间，因为它的可用范围比 timestamp 更大，MySQL 5.6.4以后物理存储上仅比 timestamp 多 1 个字节，整体性能上的损失并不大
   4. datetime 和 timestamp 有下面几个小区别，需要注意：
      1. 区别一：存储数据方式不同
         - timestamp 是转化成 UTC 时间进行存储，查询时转化为客户端时间返回
      2. 区别二：可存储的时间范围不同
         - timestamp 为'1970-01-01 00:00:01.000000' 到 '2038-01-19 03:14:07.999999'
         - datetime 为'1000-01-01 00:00:00.000000' 到 '9999-12-31 23:59:59.999999'
      3. 区别三：占用存储空间不同
         - MySQL 5.6.4之前：datetime 占用 8 个字节，timestamp 占用 4 个字节
         - MySQL 5.6.4开始：datetime 占用 5 个字节+小数秒存储，timestamp 占用 4 个字节+小数秒存储
      4. 区别四：受时区影响不同
         - 当更改时区参数 time_zone 时，timestamp 会随时区改变而改变，datetime 不会改变
      5. 区别五：索引效率不同
         - timestamp 更轻量，索引相对更快

7. text、blob 类型：

   1. 尽可能不要使用 text、blob 类型
   2. 不要在数据库中使用 varbinary 或 blob 存储图片及文件等。MySQL 并不适合大量存储这种类型的文件

### 五、索引规范

1. 索引命名规范：

   1. 主键索引名为 pk\_字段名；唯一索引名为 uniq\_字段名；普通索引名则为 idx\_字段名（pk_ 即 PRIMARY KEY；uniq_ 即 UNIQUE KEY；idx_ 即 INDEX）
   2. 用小写，命名不要过长

2. 主键规范：每个表必须设置主键 id（PRIMARY KEY (`id`)），字段类型必须为整型、自增长（AUTO_INCREMENT）、步长为1（根据需要选择 int 或 bigint。一般情况下业务表使用 bigint 类型，防止数据量增长后自增主键值不够用。对于数据量不会增长过多的配置表，可使用 int 类型）

3. 外键规范：禁止使用外键，约束逻辑在应用层面解决，外键影响性能，并且在并发操作时容易引起死锁

4. 索引数量规范：单张表的索引数量建议控制在 5 个以内

5. 普通索引规范：

   1. 选择性低的字段不适合单独建立索引（如状态值、性别等），即使设计了索引也未必会生效，查询时 MySQL 优化器可能仍然选择全表扫描，这样的索引反而浪费存储空间，影响增删改的效率
      这里需要引入一个概念，索引的选择性。索引的选择性是指，不重复的索引值和数据表的记录总数的比值。索引的选择性越高则查询效率越高，因为选择性高的索引可以让 MySQL 在查找时过滤掉更多的行
   2. UPDATE、DELETE 语句需要根据 WHERE 条件添加索引
   3. 使用 EXPLAIN 判断 SQL 语句是否合理使用了索引，尽量避免 Extra 列出现 Using FileSort，Using Temporary
   4. 合理地利用覆盖索引。由于覆盖索引一般常驻于内存中，因此可以大大提高查询速度
   5. 对长度过长的 varchar 字段（比如网页地址）建立索引时，需要增加散列字段，对 varchar 使用散列算法时，散列后的字段最好是整型，然后对该字段建立索引
   6. 存储域名地址时，可以考虑采用反向存储的方法，比如把 [news.sohu.com](http://news.sohu.com/) 存储为 com.sohu.news，方便在其上构建索引和进行统计

6. 联合索引规范：

   1. 建议联合索引中的字段数量不超过5个
   2. 经常用的列优先（最左前缀原则）、离散度高的列优先（离散度高原则）、宽度小的列优先（最少空间原则），另外还是要结合索引的原理结构和具体使用的业务场景
   3. 索引字段的顺序需要考虑字段唯一值的个数，一般选择性高的字段放在前面
   4. ORDER BY、GROUP BY、DISTINCT 的字段需要放在联合索引的后面，也就是说，联合索引的前面部分用于等值查询，后面的部分用于排序
   5. 合理创建联合索引，联合合索引 (a,b,c) 可以用于`WHERE a=?`、`WHERE a=? AND b=?`、`WHERE a=? AND b=? AND c=?`等形式，但对于`WHERE a=?`的查询，可能会比仅仅在 a 列上创建单列索引查询要慢，因此需要在空间和效率上达成平衡
   6. 把范围条件放到联合索引的最后，WHERE 条件中的范围条件（BETWEEN、<、<=、>、>=）会导致后面的条件使用不了索引

7. 前缀索引规范：

   1. 对于超过 20 个长度的字符串列，可以考虑创建前缀索引
   2. 或者一个字段的前几个字符的选择性跟整个字段的选择性差不多，这时候考虑前缀索引，节省空间且提高效率，例如邮箱地址xxxx@clubfactory.com，取前几位姓名做前缀索引即可
   3. 缺点是排序无法使用前缀索引

8. 时间索引规范：每个业务相关的表在建表时必须加上创建时间索引和更新时间索引，以方便数据清理转移、数仓同步数据

   最后的最后，SQL 进行 EXPLAIN 后再提测是一种美德

### 六、分表规范

1. MySQL 单表数据量在 300 万 ~ 500 万 左右时性能最佳。每张表的数据量控制在 5000 万以下，数据量超过 5000 万考虑水平拆分，单表字段值过多考虑垂直拆分
2. 对于可预见的短期内会形成大表的，在建表时即可考虑分表，以免后期被动
3. 推荐使用 CRC32 求余（或者类似的算术算法）进行分表，表名后缀使用数字，数字必须从 0 开始并等宽，比如散 100 张表，后缀则是从 00-99
4. 使用时间分表，表名后缀必须使用固定的格式，比如按日分表为 user_20110101
5. 深入理解业务，根据业务特性、查询需求来分表，如按年、季度、月分，如按 user_id 取模、seller_id 末尾数字来分等

### 七、其他规范

1. 禁止使用函数、触发器、存储过程、事件、外键等，这些会将业务逻辑和数据库耦合在一起，维护起来不方便、出现问题难以排查，

   除此之外还会消耗数据库资源，降低数据库集群可扩展性，因此推荐在程序端实现

2. 添加索引前第一步先确认需要加索引的字段是否已经存在索引，禁止添加重复的索引降低性能、浪费资源

3. 清空表数据请使用 TRUNCATE，而不用 DELETE，DELETE 速度慢，会造成主从延迟，且产生大量 binlog

### 八、建表示例

```sql
CREATE TABLE `air_route` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `air_route_code` varchar(32) NOT NULL DEFAULT '' COMMENT '航线简码',
  `air_route_middle` varchar(1024) NOT NULL DEFAULT '' COMMENT '经停信息',
  `origin_country_name` varchar(128) NOT NULL DEFAULT '' COMMENT '出发国',
  `origin_country_code` varchar(32) NOT NULL DEFAULT '' COMMENT '出发国简码',
  `origin_air_line_code` varchar(64) NOT NULL DEFAULT '' COMMENT '出发港航司简码',
  `origin_port_code` varchar(32) NOT NULL DEFAULT '' COMMENT '出发港简码',
  `dest_country_name` varchar(128) NOT NULL DEFAULT '' COMMENT '目的国',
  `dest_country_code` varchar(32) NOT NULL DEFAULT '' COMMENT '目的国简码',
  `dest_port_code` varchar(32) NOT NULL DEFAULT '' COMMENT '目的港简码',
  `air_space_type` tinyint(4) unsigned DEFAULT NULL COMMENT '舱位类型',
  `air_route_status` tinyint(4) NOT NULL DEFAULT '2' COMMENT '状态，1. 使用中 2. 暂停使用',
  `create_time` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `update_time` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `is_deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '逻辑删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_air_route_code` (`air_route_code`),
  KEY `idx_air_route_status` (`air_route_status`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '航线表';
```

### 九、查询优化

1. SELECT 语句指定具体字段名称，杜绝使用 SELECT *  读取全部字段。尤其是当表中存在 text / blob 大列时就会是灾难，可能本来不需要读取这些列，但因为偷懒写成 SELECT * 导致内存 buffer pool 被这些“垃圾“数据把真正需要缓冲起来的热点数据给洗出去了

2. SELECT 语句避免使用 UNION，推荐使用 UNION ALL，并且子句个数限制在 5 个以内。因为 UNION ALL 不需要去重，节省数据库资源，提高性能

3. `SELECT … WHERE … IN (…)`，IN 值不要过多，限制在 500 以内，会增加底层扫描，影响查询效率。因为哪怕是基于索引的条件过滤，如果优化器意识到总共需要扫描的数据量超过 30% 时，就会直接改表执行计划为全表扫描，不再使用索引

4. SELECT 查询时必须加上 limit 限制查询行数，避免慢查询

5. 生产环境禁止使用 hint，hint 是用来强制改变 MySQL 执行计划，如 FORCE INDEX、IGNORE KEY、STARAIGHT JOIN 等，但随着数据量变化我们无法保证自己当初的预判是正确的，因此要充分相信 MySQL优化器 

6. WHERE 条件中等号左右两边的字段类型必须一致，否则无法利用索引

7. WHERE 子句中禁止只使用全模糊的 LIKE 条件进行查找，必须有其他等值或范围查询条件

8. 索引列禁止使用函数或表达式，否则无法利用索引。如`WHERE length(name)=’Admin’`或`WHERE user_id+2=10023`

9. OR 语句慎用

10. 使用 EXPLAIN 判断 SQL 语句是否合理使用了索引，尽量避免 Extra 列出现 Using FileSort，Using Temporary

11. 建议不要使用`LIKE '%value'`的形式，因为 MySQL 仅支持最左前缀索引，即` LIKE '%value'`不走索引而`LIKE 'value%'`是可以走一部分索引的

12. 关联优化

    1. 不建议使用子查询，建议将子查询 SQL 拆开结合程序多次查询，或使用 JOIN 来代替子查询
    2. 多表 JOIN 不要超过3个表
    3. 多表 JOIN 时，要把过滤性最大（不一定是数据量最小，而是指加了 WHERE 条件后过滤性最大的那个）的表选为驱动表
    4. 如果 JOIN 之后有排序，排序字段只有在属于驱动表的情况下，才能利用驱动表的索引完成排序
    5. JOIN 的关联字段在不同表中的类型和命名要一致

13. ORDER BY、GROUP BY 优化

    1. 减少使用 ORDER BY，和业务沟通能不排序就不排序或将排序放到程序端去做。ORDER BY、GROUP BY、DISTINCT 这些语句都比较耗费 CPU
    2. ORDER BY、GROUP BY、DISTINCT 尽量利用索引直接检索出排序好的数据
    3. 包含了 ORDER BY、GROUP BY、DISTINCT 这些查询的语句，必须加 LIMIT，限制行数控制在 1000 以内
    4. GROUP BY 时会按照一定规则进行排序，如果业务上对顺序没有要求，可以加 ORDER BY NULL 提高查询效率
    5. 多字段联合索引情况下，WHERE 中过滤条件的字段顺序无需和索引一致，但如果有排序、分组则必须一致，比如联合索引idx(a,b,c)
       1. 下面的 SQL 都可以完整用到索引：
          - `SELECT … WHERE b = ? AND c = ? AND a = ?`——注意到，WHERE 中字段顺序并没有和索引字段顺序一致
          - `SELECT … WHERE b = ? AND a = ? AND c = ?`
          - `SELECT … WHERE a = ? AND b IN (?, ?) AND c = ?`
          - `SELECT … WHERE a = ? AND b = ? ORDER BY c`
          - `SELECT … WHERE a = ? AND b IN (?, ?) ORDER BY c`
          - `SELECT … WHERE a = ? ORDER BY b, c`
          - `SELECT … ORDER BY a, b, c`——可利用联合索引完成排序
       2. 下面的 SQL 只能用到部分索引，或者可利用 ICP 特性（ICP（Index Condition Pushdown）索引下推是 MySQL 5.6 的新特性，其机制会让索引的其他部分也参与过滤，减少引擎层和 server 层之间的数据传输和回表请求，通常情况下可大幅提升查询效率）：
          - `SELECT … WHERE b = ? AND a = ?`——只能用到 (a, b) 部分
          - `SELECT … WHERE a IN (?, ?) AND b = ?`——EXPLAIN 显示只用到 (a, b) 部分索引，同时有 ICP
          - `SELECT … WHERE (a BETWEEN ? AND ?) AND b = ?`——EXPLAIN 显示只用到 (a, b) 部分索引，同时有 ICP
          - `SELECT … WHERE a = ? AND b IN (?, ?)`——EXPLAIN 显示只用到 (a, b) 部分索引，同时有 ICP
          - `SELECT … WHERE a = ? AND (b BETWEEN ? AND ?) AND c = ?`——EXPLAIN 显示用到 (a, b, c) 整个索引，同时有 ICP
          - `SELECT … WHERE a = ? AND c = ?`——EXPLAIN 显示只用到 (a) 部分索引，同时有 ICP
          - `SELECT … WHERE a = ? AND c >= ?`——EXPLAIN 显示只用到 (a) 部分索引，同时有 ICP
       3. 下面的几个 SQL 完全用不到索引：
          - `SELECT … WHERE b = ?`
          - `SELECT … WHERE b = ? AND c = ?`
          - `SELECT … WHERE b = ? AND c = ?`
          - `SELECT … ORDER BY b`
          - `SELECT … ORDER BY b, a`

14. 分页优化

    1. 分页查询，当 LIMIT 起点较高时，可先用过滤条件进行过滤。如 `SELECT a,b,c FROM t1 LIMIT 1000,20`优化为: `SELECT a,b,c FROM t1 WHERE id>1000 LIMIT 20`

    2. 分页 LIMIT 优化，采用覆盖索引和延迟关联的思想进行优化，改写前后 SQL 查询时间从18秒缩短到1秒

       原 SQL:
       
       ```sql
       SElECT id, awb_no, cf_info_pricing_id, lm_info_pricing_id, available_pricing_time,
       main_contractor_id,logistics_business_id, lm_id, batch_adj_no, negotiation_time
       FROM reconcile_result
       WHERE 1 = 1 AND lm_id = 4
       AND main_contractor_id = 3
       AND recon_status = 80
       AND available_pricing_time >= '2019-10-01 00:00:00'
AND available_pricing_time <= '2019-10-07 23:59:59'
       AND is_deleted = 0
       LIMIT 10000, 10
       ```
       
       改写 SQL：
       
       ```sql
       SELECT a.id, a.awb_no, a.cf_info_pricing_id, a.lm_info_pricing_id, a.available_pricing_time,
       a.main_contractor_id,a.logistics_business_id, a.lm_id, a.batch_adj_no, a.negotiation_time
       FROM reconcile_result a,
       (SELECT id
       FROM reconcile_result
       WHERE 1 = 1 AND lm_id = 4
AND main_contractor_id = 3
       AND recon_status = 80
       AND available_pricing_time >= '2019-10-01 00:00:00'
       AND available_pricing_time <= '2019-10-07 23:59:59'
       AND is_deleted = 0
       LIMIT 10000, 10) b
       WHERE a.id=b.id
       ```

### 十、DML 优化

1. INSERT 语句需要指定具体字段名称，禁止写成`INSERT INTO table VALUES(…)`
2. 事务涉及的表必须全部是 InnoDB 表，否则一旦失败不会全部回滚
3. 禁止在业务的更新类 SQL 语句中使用 JOIN，比如`UPDATE t1 JOIN t2 …`
4. 事务中 INSERT | UPDATE | DELETE | REPLACE 语句操作的行数控制在 2000 以内，一次性提交过多的记录会导致线上 I/O 紧张，出现慢查询，引起主从同步延迟
5. UPDATE、DELETE 语句需要根据 WHERE 条件添加索引
6. 批量操作数据时，需要控制事务处理间隔时间，进行必要的 sleep，一般建议 5-10 秒
7. 禁用 procedure、function、trigger、views、event、外键约束，因为它们会消耗数据库资源，降低数据库集群可扩展性。推荐都在程序端实现
8. 禁止使用关联子查询，如`UPDATE t1 SET … WHERE name IN(SElECT name FROM user WHERE …)`效率极其低下
9. 禁止联表更新语句，如`UPDATE t1,t2 WHERE t1.id=t2.id …`
10. 禁用 `INSET INTO … ON DUPLICATE KEY UPDATE … `原因如下：1. 在高并发环境下，容易发生死锁 2.会造成自增主键 id 不连续，假设原来有数据 300 条，用 DUPLICATE KEY 插入 100 条数据，其中前 99 条都是和原来有重叠的，只有最后一条是新增的，那么最后一条 id 会从 400 开始
13. 禁用`INSERT IGNORE …`，在高并发环境下，容易发生交叉死锁
14. UPDATE / DELETE 禁止使用关联子查询，如 `UPDATE t1 SET … WHERE name IN(SELECT name FROM user WHERE …)`
15. UPDATE / DELETE 禁止联表更新，如`UPDATE t1,t2 WHERE t1.id=t2.id …`
16. UPDATE / DELETE 禁止使用 JOIN，比如`UPDATE t1 JOIN t2 …`
17. UPDATE / DELETE 禁止使用模糊查询 LIKE