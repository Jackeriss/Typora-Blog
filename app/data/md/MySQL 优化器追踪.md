## MySQL 优化器追踪

2020-08-11 12:00:59

排查 MySQL 查询性能问题时通常会用 EXPLAIN 来查看执行计划，但是 EXPLAIN 提供的信息十分有限，如果想知道 MySQL 的查询优化器做了些什么，为什么最终选择了当前的执行计划就需要开启优化器追踪了（需要 MySQL 版本 >= 5.6），具体方法如下：

我们就使用 MySQL 官方文档提供的示例来做演示和讲解：https://dev.mysql.com/doc/internals/en/tracing-example.html

#### 1. 查看优化器追踪是否开启

```sql
SHOW VARIABLES LIKE 'optimizer_trace'; --查看优化器追踪是否开启
SHOW VARIABLES LIKE 'optimizer_trace_max_mem_size'; --查看优化器追踪最大可用内存
```

#### 2. 开启优化器追踪

```sql
SET optimizer_trace="enabled=on";
SET optimizer_trace_max_mem_size=1000000;
```

注：优化器追踪最大可用内存默认较小，不调大可能会导致追踪结果返回不全。

开启优化器追踪会消耗系统资源，不建议在生产环境使用，不过我们也可以在会话级别临时开启：

```sql
SET SESSION optimizer_trace="enabled=on";
SET SESSION optimizer_trace_max_mem_size=1000000;
```

#### 3. 执行需要追踪分析的 SQL

```sql
SELECT SUM(alias2.col_varchar_nokey), alias2.pk AS field2
FROM t1 alias1
	STRAIGHT_JOIN t2 alias2 ON alias2.pk = alias1.col_int_key
WHERE alias1.pk
GROUP BY field2
ORDER BY alias1.col_int_key, alias2.pk;
```

#### 4. 查询优化器追踪结果

MySQL 会将最新执行的 SQL 的优化器追踪结果保存在`information_schema.OPTIMIZER_TRACE`这张表里：

```sql
SELECT * FROM information_schema.OPTIMIZER_TRACE;
```

`information_schema.OPTIMIZER_TRACE`各字段含义如下：

| 字段                              | 含义                                                         |
| --------------------------------- | ------------------------------------------------------------ |
| QUERY                             | 追踪的 SQL 语句                                              |
| TRACE                             | 追踪结果                                                     |
| MISSING_BYTES_BEYOND_MAX_MEM_SIZE | 追踪信息过长时，被截断的追踪信息的字节数                     |
| INSUFFICIENT_PRIVILEGES           | 执行跟踪语句的用户是否有查看对象的权限。当不具有权限时，该列信息为1且 TRACE 字段为空 |

#### 5. 分析追踪结果

追踪结果以 JSON 格式展示，它把优化器执行的详细步骤都记录了下来，每一步的含义我都通过查询资料在注释中做了简要说明：

```json
{
  "steps": [
    { // 进入准备阶段
      "join_preparation": {
        "select#": 1,
        "steps": [
          { // 格式化 SQL 语句，补全省略的库、表、列名等
            "expanded_query": "/* select#1 */ select sum(`alias2`.`col_varchar_nokey`) AS `SUM(alias2.col_varchar_nokey)`,`alias2`.`pk` AS `field2` from (`t1` `alias1` straight_join `t2` `alias2` on((`alias2`.`pk` = `alias1`.`col_int_key`))) where `alias1`.`pk` group by `field2` order by `alias1`.`col_int_key`,`alias2`.`pk`"
          }
        ]
      }
    },
    { // 进入优化阶段
      "join_optimization": {
        "select#": 1,
        "steps": [
          { // 转换为嵌套连接查询（对连接查询做一些转换）
            "transformations_to_nested_joins": {
              "transformations": [
                "JOIN_condition_to_WHERE", // 将 ON 条件语句改写成 WHERE
                "parenthesis_removal"
              ],
              "expanded_query": "/* select#1 */ select sum(`alias2`.`col_varchar_nokey`) AS `SUM(alias2.col_varchar_nokey)`,`alias2`.`pk` AS `field2` from `t1` `alias1` straight_join `t2` `alias2` where (`alias1`.`pk` and (`alias2`.`pk` = `alias1`.`col_int_key`)) group by `field2` order by `alias1`.`col_int_key`,`alias2`.`pk`"
            }
          },
          { // 条件语句优化
            "condition_processing": {
              "condition": "WHERE", // 条件语句类型（WHERE 和 HAVING）
              "original_condition": "(`alias1`.`pk` and (`alias2`.`pk` = `alias1`.`col_int_key`))", // 优化前
              "steps": [
                { // 等值条件转换
                  "transformation": "equality_propagation",
                  "resulting_condition": "(`alias1`.`pk` and multiple equal(`alias2`.`pk`, `alias1`.`col_int_key`))"
                },
                { // 常量条件转换
                  "transformation": "constant_propagation",
                  "resulting_condition": "(`alias1`.`pk` and multiple equal(`alias2`.`pk`, `alias1`.`col_int_key`))"
                },
                { // 无效条件移除
                  "transformation": "trivial_condition_removal",
                  "resulting_condition": "(`alias1`.`pk` and multiple equal(`alias2`.`pk`, `alias1`.`col_int_key`))"
                }
              ] // 这里有个同时用到这3个转换的例子：SELECT * FROM t1 join t2 on t1.pk=t2.pk+1 WHERE t2.pk = 5 and 1 =1;
            }
          },
          {
            "table_dependencies": [ // 本次查询涉及到的表
              {
                "table": "`t1` `alias1`", // 表名及其别名
                "row_may_be_null": false, // 列是否允许为 NULL，这里并不是指表中的列属性是否允许为 NULL，而是指 JOIN 操作之后的列是否为 NULL。比如说原始语句中如果使用了 LEFT JOIN，那么后一张表的 row_may_be_null 则会显示为 true
                "map_bit": 0, // 表的编号，从 0 开始递增
                "depends_on_map_bits": [ // 依赖的映射表，这里主要是在使用 STRAIGHT_JOIN 进行强制连接顺序或者是 LEFT JOIN / RIGHT JOIN 有顺序差别时，会在 depends_on_map_bits 中列出前置表的 map_bit
                ]
              },
              {
                "table": "`t2` `alias2`",
                "row_may_be_null": false,
                "map_bit": 1,
                "depends_on_map_bits": [
                  0
                ]
              }
            ]
          },
          { // 列出了所有可用的 ref 类型的索引。如果是使用了组合索引的多个部分，在 ref_optimizer_key_uses 下会列出多个结构体。单个结构体中会列出单表 ref 使用的索引及其对应值
            "ref_optimizer_key_uses": [
              {
                "table": "`t2` `alias2`",
                "field": "pk",
                "equals": "`alias1`.`col_int_key`",
                "null_rejecting": true
              }
            ]
          },
          { // 估算需要扫描的行数
            "rows_estimation": [ 
              {
                "table": "`t1` `alias1`",
                "table_scan": { // t1 表由于没有可用的索引，故其在此阶段的结构体非常简单，仅仅包括了一步全表扫描
                  "rows": 20, // 全表扫描的行数
                  "cost": 1 // 所需代价
                }
              },
              {
                "table": "`t2` `alias2`",
                "const_keys_added": {
                  "keys": [
                    "PRIMARY"
                  ],
                  "cause": "group_by"
                },
                "range_analysis": {
                  "table_scan": {
                    "rows": 100,
                    "cost": 23.1
                  },
                  // 分析可能可以使用的索引
                  "potential_range_indices": [
                    {
                      "index": "PRIMARY",
                      "usable": true, // 该索引是否可用
                      "key_parts": [
                        "pk"
                      ]
                    }
                  ],
                  "setup_range_conditions": [
                  ],
                  "group_index_range": { // 评估在使用了 GROUP BY 或者是 DISTINCT 的时候是否有适合的索引可用
                    "chosen": false, // 索引不可用
                    "cause": "not_single_table" // 不可用原因：在多表关联时使用了 GROUP BY 或 DISTINCT（如果可用会尝试分析可用的索引 potential_group_range_indexes，并计算对应的扫描行数及其所需代价）
                  }
                }
              }
            ]
          },
          { // 对比各可行计划的代价，选择相对最优的执行计划，由于我们使用 STRAIGHT_JOIN 强制由 t2 表驱动 t1 表进行关联，所以只有一种执行顺序的方案，如果将 STRAIGHT_JOIN 改为 JOIN 则这里可以看到两种连接顺序的执行计划，连接顺序是由优化器计算比较执行代价后决定的）
            "considered_execution_plans": [
              {
                "plan_prefix": [ // 前置的执行计划
                ],
                "table": "`t1` `alias1`",
                "best_access_path": { // 当前最优的执行顺序
                  "considered_access_paths": [
                    {
                      "access_type": "scan", // 使用索引的方式，可参照为 EXPLAIN 中的 type 字段
                      "rows": 20, // 扫描行数
                      "cost": 5, // 成本
                      "chosen": true // 是否选用
                    }
                  ]
                },
                "cost_for_plan": 5, // 该执行计划的成本
                "rows_for_plan": 20, // 该执行计划的扫描行数
                "rest_of_plan": [ // 如果是三张表之间的 JOIN 则在 rest_of_plan 下还会存在下级的 rest_of_plan 
                  {
                    "plan_prefix": [ 
                      "`t1` `alias1`"
                    ],
                    "table": "`t2` `alias2`",
                    "best_access_path": {
                      "considered_access_paths": [
                        {
                          "access_type": "ref",
                          "index": "PRIMARY",
                          "rows": 1,
                          "cost": 20.2,
                          "chosen": true
                        },
                        {
                          "access_type": "scan",
                          "using_join_cache": true,
                          "rows": 75,
                          "cost": 306,
                          "chosen": false
                        }
                      ]
                    },
                    "cost_for_plan": 29,
                    "rows_for_plan": 20,
                    "chosen": true
                  }
                ]
              }
            ]
          },
          { // 基于 considered_execution_plans 中已选执行计划改造原有的 WHERE 条件句并针对表的增加适当的附加条件便于单表数据的筛选。这部分条件的增改主要是为了便于 ICP，但是 ICP 是否开启并不影响该部分的构造
            "attaching_conditions_to_tables": {
              "original_condition": "((`alias2`.`pk` = `alias1`.`col_int_key`) and `alias1`.`pk`)",
              "attached_conditions_computation": [
              ],
              "attached_conditions_summary": [ // 附加条件汇总
                {
                  "table": "`t1` `alias1`",
                  "attached": "(`alias1`.`pk` and (`alias1`.`col_int_key` is not null))" // 附加的条件或者是原语句中能直接下推给单表筛选的条件
                },
                {
                  "table": "`t2` `alias2`",
                  "attached": null
                }
              ]
            }
          },
          { // 子句优化
            "clause_processing": {
              "clause": "ORDER BY", // 子句类型（DISTINCT、GROUP BY 和 ORDER BY）
              "original_clause": "`alias1`.`col_int_key`,`alias2`.`pk`", // 优化前
              "items": [ // original_clause 中包含的对象
                {
                  "item": "`alias1`.`col_int_key`"
                },
                {
                  "item": "`alias2`.`pk`",
                  "eq_ref_to_preceding_items": true // 与前置表关联的是否是唯一索引
                }
              ],
              "resulting_clause_is_simple": true, // 优化后子句是否是简单子句
              "resulting_clause": "`alias1`.`col_int_key`" // 优化后
            }
          },
          {
            "clause_processing": {
              "clause": "GROUP BY",
              "original_clause": "`field2`",
              "items": [
                {
                  "item": "`alias2`.`pk`"
                }
              ],
              "resulting_clause_is_simple": false,
              "resulting_clause": "`field2`"
            }
          },
          { // 改善之后的执行计划
            "refine_plan": [
              {
                "table": "`t1` `alias1`",
                "access_type": "table_scan" // 优化后的索引访问类型
                // pushed_index_condition: 可用到 ICP 的条件句
                // table_condition_attached: 在 attaching_conditions_to_tables 阶段添加了附加条件的条件语句
              },
              {
                "table": "`t2` `alias2`" // 只有表名表示没有需要优化的地方
              }
            ]
          }
        ]
      }
    },
    { // 进入执行阶段（如果追踪的是 explain 语句则不会走到这个阶段）
      "join_execution": {
        "select#": 1,
        "steps": [
          { // 创建临时表
            "creating_tmp_table": {
              "tmp_table_info": { // 临时表信息
                "table": "intermediate_tmp_table", // 临时表名称
                "row_length": 18, // 临时表单行长度
                "key_length": 4, // 临时表索引长度
                "unique_constraint": false, // 是否有使用唯一约束
                "location": "memory (heap)", // 表存储位置，比如内存表 memory (heap)，或者是转换到磁盘的物理表 disk (InnoDB)
                "row_limit_estimate": 932067 // 该临时表中能存储的最大行数
              }
            }
          },
          { // 文件排序信息（多列排序则有多个）
            "filesort_information": [
              {
                "direction": "asc", // 排序列是升序还是降序
                "table": "intermediate_tmp_table", // 排序的表对象名
                "field": "col_int_key" // 排序列
              }
            ],
            "filesort_priority_queue_optimization": { // 优先队列优化排序，一般在使用 LIMIT 子句的时候会使用优先队列
              "usable": false, // 是否有使用
              "cause": "not applicable (no LIMIT)" // 没有使用的原因
            },
            "filesort_execution": [ // 文件排序执行
            ],
            "filesort_summary": { // 文件排序汇总信息
              "rows": 8, // 预计扫描行数
              "examined_rows": 8, // 参与排序的行数
              "number_of_tmp_files": 0, // 使用临时文件的个数，这个值为 0 代表全部使用 sort_buffer 内存排序，否则表示使用了磁盘文件排序
              "sort_buffer_size": 378, // 使用的 sort_buffer 的大小
              "sort_mode": "<sort_key, rowid>" // 排序方式
            }
          }
        ]
      }
    }
  ]
}
```

#### 总结

这个优化过程虽然看上去又长又乱，但实际上条理还是很清晰的，我总结了一下大概分为以下几个步骤：

![image-20200814094715129](https://i.loli.net/2020/08/14/89fWObqLHU4gKyF.png)

希望能帮助大家理解 MySQL 优化器，更好的解决查询性能的问题。