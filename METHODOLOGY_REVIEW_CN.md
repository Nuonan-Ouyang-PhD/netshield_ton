# ToN 方法学复核与修订说明

本次以仓库基线 `fe09ee0eca28dc666dd9c729ac266b8426c055b9` 为准，逐项核对
所指出的十个问题，并对上传的 `NetShield_ToN_Integrated_20_09_2026.zip`
做版本比较。当前可审阅结果包含代码修复、公开参数重建、共享服务软件反例、
独立 ledger 审计及论文表述修订。硬件重跑、真实 Wi-Fi 延迟标定和检测价值消融
不在本次已执行结果中。

## 核心判断

问题中有会改变软件结论的实质缺陷。尤其不能因为 waterfill 每轮至多少服务
2 B 就判定影响可以忽略：队列进入下一轮 selector，微小余量可能跨过动作门限。
公开参数重建已经观察到这一效应。

同时，软件的上传完成时间、硬件的结果返回时间、原始数据的独立审计是不同的
证据层次。修订稿保留 CRFA 硬件结果，修正软件的命名和比较方式，不把新的软件
模型包装成硬件验证。

## 十项意见的处理

| 项目 | 核查结果 | 已完成处理与剩余边界 |
|---|---|---|
| 1. Tick 仿真缺计算、Wi-Fi、core 和返回阶段 | 成立。原函数仅在 FIFO payload 清零时计完成。 | 原 A/B 指标改称 upload completion；另建显式分阶段模型。模型中的延迟是公开假定输入，不能代替实测 Wi-Fi。硬件仍按同一探针时钟的 creation→result return 评分。 |
| 2. waterfill 丢残余字节 | 成立，旧实现遇到 `remaining < active_count` 提前停止。 | 分配剩余整数 byte，按 round/tick 轮转残余优先级；保留原函数源码，单独生成修正敏感性。 |
| 3. Task A 的 12 seed 伪重复 | 成立。同步独立控制没有使用 seed 的决策路径。 | 新 Task A 只输出 36 个配置；历史 432 行完整保留并逐组证明每组只有一个 simulation outcome。未据这些重复标签计算置信区间。 |
| 4. 模拟 zero cap violations | 成立，它是 capped allocator 的实现不变量。 | 不再把该计数当独立测量；新增不调用 allocator 的 ledger 审计器，直接累加服务、核对字节守恒和事件时间。 |
| 5. admission 忽略 backlog | 成立。新流量能装入 C 不表示全队列当轮清空。 | 两个联合 admission 调用都显式传入已有队列；新字节预算为 `max(0,C-sum(Q))`。已有 backlog 自己超过 C 时仍明确不可行。 |
| 6. is_safe 使用独占速率 | 成立。单个 full 在 mid 估计 500 ms 不能保证三者同时按时。 | 更名为 isolated latency precheck；与 backlog admission、完整模型 deadline reservation 分开。 |
| 7. A/B timely 定义不同 | 时间分辨率和服务模型不同；在同步轮首释放、1 s 纯上传 deadline 下存在有限等价情形。 | 统一 inclusive elapsed-upload 判据，同时保留 A 的 round-end 上界与 B 的 tick-end 上界，明确二者都不是 core-result time。 |
| 8. 文章与代码对应不清 | 成立，包含终点命名、伪重复、历史输出与新源码、失效构建说明等。 | 增加源文件/结果映射，保留 legacy driver，更新构建和复现入口，论文直接说明历史 allocator 与修正模型的关系。 |
| 9. 竞争链路 safety 需新实验 | 已新增公开软件验证。 | 30 个确定性配置 × 4 策略＝120 次模型运行，保留每个请求和服务记录；真实共享链路 safety 仍需带阶段实测和误差余量的硬件评测。 |
| 10. alert/summary/full 的检测价值未建立 | 成立。固定 utility 和饱和的冻结分类分数不能识别信息增益。 | 删除由 evidence size 推导检测收益的暗示，补充未执行的配对内容消融协议。没有生成新的准确率、F1 或检测延迟数字。 |

## waterfill 修复的实测软件影响

使用正文公开的十项 payload、六位小数 utility 和保留的旧函数，重建全部
36 个 `(v,capacity)` 配置。在 action counts、core-request fraction、payload、
逐轮队列轨迹和最大队列五类字段上，36/36 与历史 CSV 相同。这是公开参数重建，
没有加载私有全精度 action file、runtime、模型或原始特征数据。

改用 work-conserving、轮转残余分配后，24/36 个逐设备队列轨迹改变，5/36 个
动作组合改变，后者均在 low capacity，`v=1,3,10,30,100`。

| Low capacity 的 v | 历史 full 请求/270 | 修正后 full 请求/270 | 历史完整状态周期 | 修正后完整状态周期 |
|---:|---:|---:|---:|---:|
| 1 | 66 | 90 | 4 | 3 |
| 3 | 66 | 90 | 4 | 3 |
| 10 | 81 | 90 | 10 | 3 |
| 30 | 87 | 90 | 28 | 3 |
| 100 | 90 | 90 | 未检出 | 3 |

`v=100` 的 full 数没变，但 summary 动作和 payload 改变。`v=1,3` 的 payload
由 9,191,424 B 变为 11,796,480 B。以上配置的 timely full-upload 数仍为零。
Mid/high 的动作组合没有改变；mid 的 full/none 动作仍是二周期。修正后某些
mid 记录的完整状态周期为 6，来自三个设备轮转分配余数字节；不能误读成
动作二周期消失。

CSV 和完整参数见
[PUBLIC_SELECTOR_COMPARISON.csv](supporting_material/methodology_validation/PUBLIC_SELECTOR_COMPARISON.csv)、
[PUBLIC_SELECTOR_AUDIT.json](supporting_material/methodology_validation/PUBLIC_SELECTOR_AUDIT.json)
及 [TASK_A_REPLICATION_AUDIT.csv](supporting_material/methodology_validation/TASK_A_REPLICATION_AUDIT.csv)。

## 共享服务模型给出的反例

新增模型使用 1 ms tick、恒定共享应用字节速率、设备内 FIFO、设备间整数
max-min 和单个 FIFO core。空闲 tick 的容量作废；返回路径只加入声明的延迟，
没有另建争用的返回字节队列。模型评估一次新请求 batch，不能直接证明稳态
吞吐、长期公平性或随机无线链路 SLO。

以下均为 `n=3`、`B=131072 B`、`C=262144 B/s`、deadline 1000 ms。
“假定阶段延迟”固定为 detector 40 ms、preprocessing 20 ms、uplink extra
15 ms、core 35 ms、return 10 ms，全部是敏感性输入。

| 条件 | 策略 | 新 full 准入数 | 最晚上传 ms | 最晚返回 ms | 按时新结果数 |
|---|---|---:|---:|---:|---:|
| 无 backlog、额外延迟为 0 | 独占链路预检查 | 3 | 1500 | 1500 | 0 |
| 无 backlog、额外延迟为 0 | 仅检查新字节 | 2 | 1000 | 1000 | 2 |
| 旧 backlog=B、额外延迟为 0 | 仅检查新字节 | 2 | 1500 | 1500 | 0 |
| 旧 backlog=B、额外延迟为 0 | backlog-aware | 1 | 1000 | 1000 | 1 |
| 无 backlog、假定阶段延迟 | 仅检查新字节 | 2 | 1060 | 1155 | 0 |
| 无 backlog、假定阶段延迟 | 完整模型 reservation | 1 | 560 | 620 | 1 |
| 旧 backlog=B、假定阶段延迟 | backlog-aware | 1 | 1000 | 1060 | 0 |
| 旧 backlog=B、假定阶段延迟 | 完整模型 reservation | 0 | — | — | 0 |

模型 reservation 对每个候选都重新预测全部已选任务。它在 30 个不同配置中共
接纳 93 个新请求，93 个都在同一个模型的 deadline 内返回；这一总数只能作为
模型符合性诊断，不能合并异质配置得出实验优越性。接纳机会和零接纳配置一起
报告，避免将“全部拒绝”误当更好的服务。一项回归测试还明确展示：原模型中
1000 ms 的结果，如果实际 return 额外增加 1 ms，就全部超时。

完整模型及逐事件结果见
[contention_validation](supporting_material/contention_validation/README.md)。

## 独立 ledger 复核和原硬件结论

独立审计器不调用 waterfill，不信任已有 zero-cap 或 timely 标志。
它重建逐轮服务合计、逐事件 byte 守恒、最后一次服务对应的上传终点、单 core
顺序和返回 deadline。对 CRFA 还逐一核对所有 measured 的 run/window/device
组合，防止 H-NONE 缺行导致生成分母被缩小，或换 key 后重复计数。

新软件记录有 1,112 个新请求、556 个旧队列请求，合计 1,668 行事件、1,637 行
事件/轮服务记录和 167 个使用过的服务轮；独立重建通过。CRFA 公开导出记录的
36 个 run、10,620 个服务轮、9,720 个 measured occurrence 也通过重建。

| CRFA 容量 | 生成 | 选中 full | 返回 full | 按时 full-core | nominal 按时 full-core |
|---|---:|---:|---:|---:|---:|
| Low | 3240 | 1080 | 1080 | 990 | 360 |
| Mid | 3240 | 2160 | 2160 | 2050 | 720 |
| High | 3240 | 3240 | 3240 | 3130 | 1079 |

这使原有 0.3056/0.6327/0.9660 生成分母输出及 91.7%/94.9%/96.6% frontier
attainment 的公开记录链保持成立。CRFA 服务表中所有 queue-before 为零；其
low/mid/high 分别选 1/2/3 个 full，C 恰为相应 full 总量，所以这个特定控制器
没有触发上述整数均分残余缺陷。原主活动中其他控制器的硬件表现仍应按实际
执行的冻结实现解释，不能预言打补丁后物理数值不变。

本次审计对象是**公开导出的逐探针服务和事件记录**。没有重新打开主活动
63,720 轮的私有原始日志，没有重测物理链路/NIC，也没有重算配对 bootstrap。
历史 raw audit 的 `PASS_WITH_ISSUES` 仍然有效。该边界写入报告。

## 第 10 点还需要的证据

目前能够支持的是 evidence-delivery feasibility 与指定工作负载下的实际
full-core 返回时限，尚不能量化 evidence level 的检测增益。
新增 [DETECTION_VALUE_PROTOCOL.md](supporting_material/contention_validation/DETECTION_VALUE_PROTOCOL.md)
明确标注 `NOT_EXECUTED`，要求同一 held-out episode 的三种真实表示、明确信息
字段和 padding、capture/episode 级划分与去重、冻结模型/阈值、生成分母保留缺失
结果，先测信息价值再测共享服务价值。真实表示生成器、可用原始内容与授权模型
尚未在该公共 checkout 中提供。

补齐代码和文字后，仍不能把这项研究写成已证明 full 比 summary/alert 更能检测
入侵。要形成该结论，需要执行协议并保留配对下游结果；也可以继续将论文贡献
限定在已经量化的网络证据交付问题上。

## 验证入口

```bash
python3 scripts/verify_methodology_revision.py
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s supporting_material/contention_validation -p 'test*.py' -v
```

18 个 allocator/admission/endpoint/独立审计测试和 9 个共享模型测试通过，包含
13,750 个整数分配用例。变异测试会拒绝“违规标志仍为零但服务量超额”、缺失或
重复服务、缺失 H-NONE 事件、错误返回时间和伪造 timely 标志。

120 个冻结文件、14 个既有 formal blocks、21 个带标签公式和摘要保持原样。
具体构建与验证记录见
[METHODOLOGY_VALIDATION_REPORT.md](submission/audit/METHODOLOGY_VALIDATION_REPORT.md)，
源文件到证据的映射见
[CODE_EVIDENCE_ALIGNMENT.md](submission/audit/CODE_EVIDENCE_ALIGNMENT.md)。
