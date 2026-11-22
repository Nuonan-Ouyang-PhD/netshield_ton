# 给本地 Codex 的完整执行指令：NetShield ToN 定向补实验

## 当前继续位置：9cc64ed 私有重审与诊断对账已完成

从 PR #3 的 `fix/methodology-evidence-20261122` 最新版本继续。`9cc64ed`
保留了从 `b8a978b` 执行的真实私有重审、诊断对账与新 PDF；其后公开核验修复
另有提交，记录实际取得的 commit 和工作树状态。先读
[retained_review/README.md](retained_review/README.md)、
[retained_review/PUBLIC_REVIEW.md](retained_review/PUBLIC_REVIEW.md)、
[private_record_qualification/README.md](private_record_qualification/README.md)
和 [PREPARATION_STATUS.json](PREPARATION_STATUS.json)。此前的
`FOLLOWUP_STATUS.md`、`FOLLOWUP_REVIEW.md` 是较早阶段记录，不是当前待办清单。
保留已集成的论文与 PDF。

### 已完成工作的准确状态

- 修复版 checker 已使用默认公开 accepted index，在全新路径重审真实私有记录，
  结果为 `PASS_RECORDED_FIELDS_ONLY`：216 arms、864 manifests、63,720 服务轮、
  58,320 measured origins。24,012 个需要 Core 的事件全部返回，其中14,416按时、
  9,596迟到。公开摘要的 checker/index 身份与计数已核对。旧报告与旧检查器保留；
  不再把这次重跑列为 pending。逐 chunk、远端逐文件部署回执和逐事件 boot epoch
  仍有缺口，历史 `PASS_WITH_ISSUES` 没有被覆盖。
- 本地报告已将 portable export 关联到三个源模型、训练清单及 train/validation
  文件，并核对31个源特征 CSV。不要再把这项工作写成完全未开始；需要保留
  可核查的对应记录，不能把文件哈希一致当成 capture/episode 相互独立。
- 三位有效数字整向量同桶匹配已报告为 validation `282390/996486`、test
  `709971/1147055`，包含 exact duplicates。它会漏掉跨舍入边界的近邻，不能
  宣称完成全面 near-duplicate qualification，也不能把总体比例套到896行子集。
- 新内容诊断在七个测试文件的前128行上保留896个观测、2688条预测，每种表示
  为768 TP、128 TN、0 FP/FN。它使用 light bit 与训练拟合的共同 NB consumer，
  不同于先前九输入 heavy-model 接口诊断。新结果的零差是所选样本上的观察，
  不是由构造保证，也不证明总体等效或 full 无信息价值。
- consumer、occurrences、predictions、逐文件结果和原 overlap 已逐字节保全，
  实际输入、模型、协议和源码哈希已关联。对账核对了896个唯一事件、三种表示
  一一配对与原始 test 文件前缀。该子集366行与 train/validation 精确匹配，
  544行按三位有效数字匹配，后者包含前者；子集有895个不同精确向量、863个
  不同舍入向量。这些是行/向量计数，不是独立 capture 数。已有保全与子集审计
  不再列为 pending。回溯哈希不能补证初次执行的时间或完整事前冻结。
- `CONTENT_PROTOCOL.md` 的同一 hash 已保存在更早阶段；诊断已有执行及对账，
  不能继续标为未执行草案。正式独立 held-out 与通信约束实验尚未完成。
- corrected runtime allocator 的22638组合一致性已有实际回执。公开函数重算
  original/corrected 的有序结果流，也分别匹配两份 case digest。它不替代
  old/corrected 物理配对。P1已返回身份，P2/P3资格失败，新增物理臂仍为0。

### 立即继续的工作

1. **使用当前公开入口验证交接版本。** 执行下方统一验证命令及
   `python3 supporting_material/experiment_extension/retained_review/verify_export.py`。
   已完成的私有重审和896行对账无需为更新文档再次运行。若输入或检查器发生
   实质变化，再使用新输出路径重新资格检查；保留原始产物和两代报告。
2. **继续恢复三探针实验资格。** 根据实际已有配置核查供电、网络、名字解析及
   SSH，记录真实连接结果；不猜地址、不把超时直接解释成设备已关机。条件满足
   后按下方协议执行 allocator 配对；shared-stage 先做可部署的 causal controller、
   独立 calibration 和 pilot，再冻结正式块数。保留原launcher/时间锚以隔离效应。
3. **建立合格内容实验的输入。** 优先追溯父capture/episode与实际训练样本，建立
   独立的新划分并审计重复。仅删掉已命中的测试行不足以证明独立；不能根据
   是否出现full优势挑测试子集。先固定表示与消费者、阈值、主比较、独立组
   和统计规则，再进行真正的paired content实验及通信约束输出测量。
   未来qualified runner须显式检查数值/标签/事件身份、两类训练支持、量化结果
   有限性及输入与模型manifest绑定，不能依赖可被优化模式关闭的assert。

新物理活动、诊断、重审和synthetic fixture使用各自身份。保留全部历史252臂、
原始数据、主稿理论与共同生成分母。某项缺真实依赖时只阻塞该项，继续其他
可执行工作；已有授权适用于下方完整协议，无需逐步重新确认。

## 任务与授权

项目是 Nuonan Ouyang 的 ToN NetShield，仓库为
https://github.com/Nuonan-Ouyang-PhD/netshield_ton 。
从 PR #3 的 `fix/methodology-evidence-20261122` 分支最新版本继续。
已发布的方法学修订基线是
`e9a2d335e75d1f34efb71c6a0fa2cf4b085660f5`；其后的 experiment_extension
准备工具也必须获取，不能只停在这个基线提交或旧 main。

我授权你在本项目现有本地数据、私有运行时和已配置实验设备的范围内完成
源代码核查、原始记录重审、适配器开发、离线实验，以及满足本协议条件的
校准、pilot 和正式硬件扩展。常规可逆实现、修复和已授权实验无需逐步询问。
先做能做的工作；缺少某项真实输入时，只阻塞依赖它的阶段，继续其他部分。
不要只给计划、建议或空模板后结束，也不要用模拟数据填补缺失实测结果。

先读工作区适用的 AGENTS.md。保护当前未提交修改；必要时从最新审阅分支
创建独立 worktree。记录起始 commit 和工作树状态。保留全部历史 216+36=252
硬件臂、原始日志、已接受结果和纳入决定。新增活动使用全新的目录和 ID。
不要合并 main，不要将私有原始数据、模型、SSH 配置或机器身份推到公共仓库。

## 0. 读取已完成工作并运行入口验证

依次阅读：

- `submission/audit/CODE_EVIDENCE_ALIGNMENT.md`
- `submission/audit/METHODOLOGY_VALIDATION_REPORT.md`
- `supporting_material/methodology_repair/CORRECTIONS.md`
- `supporting_material/methodology_validation/PUBLIC_SELECTOR_AUDIT.json`
- `supporting_material/contention_validation/README.md`
- `supporting_material/experiment_extension/PROTOCOL.md`
- `supporting_material/experiment_extension/evidence_value/README.md`
- `supporting_material/experiment_extension/hardware/README.md`

执行：

```bash
python3 scripts/verify_experiment_extension.py --output /实际的新工作目录/PRECHECK.json
```

现有 120 次 contention 运行是有明确假设的确定性软件实验，93/93 的模型内
reservation 结果不能作为物理 safety 证据。Task A 是 36 个确定性配置，
不是 432 个独立实验。旧 Task A/B 终点是上传完成；硬件 result return 是另一
终点。保留这些修正及版本边界。不要重新生成或覆盖历史 CSV 来“消除”差异。

## 1. 定位真实材料并核对实际部署路径

先检查当前项目、已挂载研究数据卷和现有 ToN_NetShield 项目目录；
以实际存在的路径和项目记录为准，不得猜造路径、设备 IP 或登录凭据。
优先用 rg 搜索代码和已有 manifest。
定位：实际 Core/Probe/launcher/allocator；原活动运行时 snapshot 和执行配置；
action profile；模型、阈值与训练数据 provenance；原始 workload/capture；
alert/summary/full 编码与消费代码；主活动 primitive service/event ledger；
已有设备连接配置。仅使用当前授权项目中实际存在的材料。

可运行只读发现工具：

```bash
python3 supporting_material/experiment_extension/discover_assets.py \
  --root checkout=. --root runtime=/实际运行时目录 \
  --root evidence=/实际证据目录 --output /新工作目录/ASSET_INVENTORY.json
```

它只给候选文件和哈希，不能证明文件就是执行版本。创建实际运行时调用链
核查表，关联 launcher → selector/admission → allocator → service ledger →
Core inference → originating Probe result receipt，并与旧活动 manifest 核对。
确认余数 bug 是否真的存在于已部署路径；分别记录“确认受影响”“确认是
另一实现”“来源尚不能确定”。不要以公开重放吻合替代真实源码核查。

重审已有主活动原始 ledger：从 primitive grant 重建每轮总服务、每探针队列
连续性、事件字节守恒、缺失/重复身份和 deadline。公共 CRFA 导出已独立复核，
不等于私有主活动全部 primitive ledger 已复核。现有
`scripts/audit_service_ledgers.py` 只适用于其明确支持的输入 schema；若原始
schema 不同，写无损适配器并保留原记录定位，不能拿总表或 cap_violation=0
替代原始重建。日志字段不足时清楚记录缺口，不修改原日志。

## 2. 先完成真实内容审计和离线价值消融

审计实际三种表示，输出 decoded 字段清单、观测时间范围、有效内容/封装/
padding/重复字节和实际序列化长度。确认 full 是否真的提供新增信息。
三种表示必须源自同一底层观测，遵守相同的可用时间；full 不能偷偷读取
决策时刻之后的数据。若目前只传同一特征向量的不同填充长度，明确报告
现状；在独立新版本实现有实际内容区别的表示后才能测试对应价值，不能
事后宣称旧实验已经证明了它。

默认先选择一个真实数据支持的二分类下游任务，例如攻击事件识别。
现成 scorer 支持预先声明的二分类映射；若选择跨探针关联、定位或时间线
任务，必须另写并验证任务适配器和 scorer，不能把分类结果冒充该任务效果。

在看测试结果前固定任务、预测单位、raw-label→binary 映射、模型/阈值、
三种 encoder、主要比较和分析规则。训练/验证/测试按独立 capture/episode
组隔离，相关探针和重复事件留在同一组。审计 exact 与 near duplicates；
记录近重复度量、训练期确定的标准化、阈值、检索覆盖率和残留重叠。
exact hash 没有重复不能证明不存在 near duplicates。不能证明独立的旧
perfect replay 可作受限诊断，不能替代独立 held-out 的新实验。

若现有consumer不能有效处理三种表示，可以在这个独立新活动中，仅使用
训练/验证数据实现或训练支持缺失字段/mask的共同consumer，再冻结并测试。
保留训练来源和预算；新模型不替换历史活动的冻结模型，也不把新模型结果
归到原252臂。共同模型必须预先支持这些输入，不能把未处理的缺失字段
引起的异常直接解释为证据内容差异。

实现真实 encoder/model adapter：encoder 得到源观测但不接收 ground truth；
consumer 只能得到该级 decoded 表示、冻结模型与配置。禁止通过事件 ID、
路径或共享数据集回查被省略特征或真值。保留每次模型执行、输入表示和输出
的身份/哈希。若使用不同 consumer，解释为表示+consumer 的系统比较并匹配
训练预算。当前 scorer 限单一冻结 model/threshold；不同 consumer 需要先按
预先声明的设计扩展并验证 scorer，不能给不同模型填同一个虚假的 hash。
仅创建 prediction CSV 或填 model_hash 不算已执行模型。

先在无网络损失/排队的条件下，对同一批 held-out 事件执行三种表示。
按 evidence_value/README 的严格 schema 生成 protocol、groups、corpus、
occurrences 和 predictions；每个生成事件均保留 alert/summary/full 三条明确
状态记录，包括缺失或失败。统计和 bootstrap 的单位是独立组，不能是无效
seed 或重复事件；其次数、seed、主比较和主要指标写入冻结 protocol。

```bash
python3 supporting_material/experiment_extension/evidence_value/score_evidence_value.py \
  --protocol /真实输入/protocol.json --groups /真实输入/groups.csv \
  --corpus /真实输入/corpus.csv --occurrences /真实输入/occurrences.csv \
  --predictions /真实输入/predictions.csv --output /新结果/value_report.json
```

报告 pooled 计数、各组结果、TP/FP/FN/TN、precision/recall/F1、generated/
scored/missing、配对差异、有效信息与 payload/计算成本。明确 group-macro 与
pooled 的不同口径。零分母为 null，缺失预测不能变成 TN。负结果和无差异
同样保留；不得挑选有利样本、改任务或调测试阈值以制造 full 更好的结果。

随后再按冻结任务评估受通信约束的实际任务输出。相同 held-out 事件进入
共同服务模型或新硬件，两种证据身份明确分开。主要联合指标是按时且正确
返回/全部生成，并报告选中率及条件及时率；拒绝/缺失仍在生成分母。
共同服务模型的时间仍属于software sensitivity；不能写成measured后交给
现成scorer的transport_measured入口。该入口只接受真实同域测量；软件时间
使用单独明确标注的分析输出。
不把旧硬件及时率与另一批数据的 accuracy 相乘后声称测得了应用收益。

## 3. 条件性 allocator 硬件回归

只有真实部署路径确认有相同 bug，才执行这个针对性对照；确认实现不同则
记录证据并跳过该依赖阶段。旧/新运行时仅改变 allocator 及声明的余数轮转
优先级。固定 workload、模型、selector、launcher、时间锚点、设备和服务规则。
不要在同一对照中顺便修 launcher 相位而混淆 allocator 效应。

主配置：原三台探针、low=131072 B/round、v=1、旧/新 allocator。
mid=262144 B/round、v=1 可作为预先声明的对照。按真实运行时支持的冻结
协议采用 5 warm-up+90 measured，保留 drain 和全部测量起源事件的后续结果。
生成全新物理 session/block ID；独立 block 内匹配 workload，平衡方法顺序。

使用 hardware/plan_hardware.py 生成 allocator 的 pilot/formal 计划；该工具
不支持 allocator calibration，前置工作是实际源码核验和离线回归检查：

```bash
python3 supporting_material/experiment_extension/hardware/plan_hardware.py \
  --study allocator --phase formal --blocks 预先固定的正整数 \
  --order-seed 预先固定的整数 --campaign-id 全新活动ID \
  --qualification /真实审查/qualification.json \
  --sample-size-rule-file /冻结计划/sample_size_rule.json --output /新计划目录
```

若已预先选择 mid 对照，添加 --include-mid-control。先按 README 生成和完成
独立 qualification/pilot，不填写虚假的通过记录。blocks 根据独立 pilot 的
变异和预设精度目标冻结，不能沿用“12 seed=12独立实验”。
检查 action、pre/post queue、实际 grant、未利用容量、payload 和真实结果返回。
公开模型 low,v=1 的66/270→90/270是待对照的模型预测，不是硬件成功阈值。
分别报告动作周期和完整队列状态周期。

## 4. 条件性共享链路/处理阶段物理验证

目标是评估竞争、积压和处理阶段下的真实行为。如果实际运行时和设备可用，
实现并资格验证这个扩展；缺少依赖时继续其他阶段，保留论文当前的个体
预筛选定位。不能把未执行的新 filter 写为已验证贡献。

对照限定为共同 H-FULL/H-NONE 请求，明确这不是原 S-CQPG 不变版本的重跑。
三探针，B=131072，mid C=262144 B/round，deadline=1000ms；
两种初始积压0/B × 三种策略（原isolated+new-byte、backlog-aware、可部署的
causal shared-stage admission），每个匹配实验块6个条件。
初始每探针 FIFO 分布、事件年龄/剩余字节、core idle/no-pending 入场条件按
hardware协议冻结并实测核对。首个 measured batch 为初始backlog机制主分析；
全部90个 measured 轮的轨迹可作预先声明的次分析（首轮仍属于主分析），
不能假装每轮都有同样初始积压。

先做独立 stage calibration，再 pilot，再冻结正式设计。新 controller 只能
读取决策时可得的当前队列、请求和core状态；考虑真实共享服务纪律、阶段
耗时、信息陈旧及余量，并在加入候选后重新检查此前已接纳任务。
固定预测参数和 margin 后再正式测试。不能使用未来完成时间/测试标签，
不能把当前模拟器的同模型oracle当已验证控制器。校准分位数不是确定性
最坏界；结论使用实测达成率和拒绝代价，不作无依据的硬deadline保证。

正式计划命令同上，改 --study shared_stage；calibration/pilot/formal 使用
独立ID和数据。遵循生成器的条件顺序和资格要求，记录部分循环的不平衡。
当前planner只支持预先固定的完整block数，按独立pilot和精度目标确定；
若要顺序停止设计，需另行实施并验证统计方法，不能沿用普通固定样本区间。
不得看到显著性后停采。
记录所有尝试和预先定义的基础设施排除，不丢弃慢但有效的实验。

## 5. 时间戳、原始记录和独立验证

保留 scheduled release、actual creation、detector/preprocess、enqueue、上传
完成、core receive/start/end、originating probe result receipt、observation
horizon、时钟域和事件ID。主要created→return必须同一个probe时钟。
core推理时长用core自己的时钟。跨主机monotonic不能直接相减得到Wi-Fi单向
延迟；需要已验证对时和误差界才可计算。声明created是否已包含detector等
阶段；未包含就不声称包含，不重复相加重叠阶段。

及时性按实际端点 <= deadline（含等号）重算。未过截止时间的缺失结果是
censored，输出bounds/null；已过截止时间才可判定deadline miss。每个生成
事件必须有明确终态或审查时状态，拒绝全部时timely/generated为0，不能靠
空的选中分母得到100%。warm-up、measured、drain身份和起源队列保持清楚。

按hardware schema保留primitive service事件，独立重建每轮cap、队列连续、
字节守恒、关联身份与结果端点，不依赖allocator自报零违规。适配器变换要
保留原记录定位和输入哈希。出现真实违反或负结果时原样保留并解释。

## 6. 冻结、交付和论文集成

正式运行前保存真实源代码snapshot、runtime/model/encoder/workload/数据split/
校准/资格报告/采样与分析计划，并用freeze_inputs.py冻结身份；运行前后verify。
完整保存实际执行版本、命令、环境、全部attempt、偏离记录及原始数据。
哈希只能证明内容身份，不替代真实部署核验或输入资格。

新结果分成：既有数据重审、新离线真实模型实验、新物理实验、软件假设实验、
synthetic fixture；不要混为同一种证据。交付以下实物及简明中文结论：

- 真实资产/运行时调用链/三表示内容审计；原始ledger重审报告。
- 冻结协议与manifest、真实adapter/controller源码和测试。
- 完整生成事件、模型输出、service、attempt、时间锚点、按组/按block结果。
- 实验资格、有效/无效/缺失计数、paired统计、数值来源和限制。
- 清楚的状态矩阵：每项EXECUTED、NOT_APPLICABLE或BLOCKED及实际原因。

在真实结果通过审计后，直接将证据支持的结果写入主文/补充材料，更新
code–evidence/number provenance，编译两份PDF并检查引用、表格和版面；
无新结果的部分保持明确pending，不编造数字。保持旧理论和未受影响的
结果，任何必要理论改动单列理由和验证。仅推送可公开代码/汇总/论文到
审阅分支或新的draft PR，不合并main、不公开私有材料。最后告诉我：实际
做了什么、得到什么、哪些结论变化、还有什么真实依赖未满足。

请从获取审阅分支、读取协议和发现本地材料开始，持续做到所有可执行工作
完成；需要真实输入的阻塞要具体到材料或接口，不要重新问我是否同意常规
下一步。
