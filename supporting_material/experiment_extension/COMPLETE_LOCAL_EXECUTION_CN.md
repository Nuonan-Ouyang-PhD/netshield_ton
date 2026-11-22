# 给本地 Codex 的一次性完整执行指令

你在 Nuonan Ouyang 的 NetShield ToN 项目中工作。仓库是
https://github.com/Nuonan-Ouyang-PhD/netshield_ton ，审阅 PR 是 #3，分支是
`fix/methodology-evidence-20261122`。从该分支最新提交继续，必须包含
`72cc05df530727a48f89f4ed99b05da1c4c3fbe0` 及其后本次完整收尾修订；记录实际
取得的 commit 和工作树状态，不以本文提到的旧 hash 代替实际 HEAD。

## 1. 这次任务的终点与执行方式

这是一次持续执行到可交付状态的任务。已授权的本地开发、修复、校准、pilot、
正式采集、分析、论文修改、编译和审阅分支同步，直接依照下面的证据要求完成。
不要在修完一个函数、通过一组测试、写出一份计划或完成一个 pilot 后结束并问
“是否继续”。实现问题在这一轮解决；一个研究分支缺真实输入时，继续其他可执行
分支，最后一次汇总结果和确切的外部依赖。

成功终点是：每个能够执行的分支都有实际产物、来源、检查和论文中的对应位置；
确实依赖缺失设备或原始采集来源的分支有准确的阻塞状态。不能把未取得的数据
补成预期值，也不能用“计划已生成”“测试通过”替代真实实验完成。

保留全部历史 216 个主活动臂、36 个 CRFA 臂、原始日志、既有纳入决定及原理论。
新活动、新模型、新数据划分使用独立目录和 ID。保护未提交修改，必要时建隔离
worktree。只把可公开的代码、脱敏汇总和论文推到同一审阅分支；保留 draft，不合并
`main`。私有模型、特征、原始设备日志、SSH 配置和机器身份留在受控本地目录。

## 2. 已完成的事项：按已有产物接续

以下事项已经有记录，不因本次更新状态或文件名再次重跑：

- 修复版检查器对原 216 臂的真实私有重审已是 `PASS_RECORDED_FIELDS_ONLY`：
  864 份 manifests、63,720 轮、58,320 个 measured events；24,012 个需要 Core
  的事件全部返回，14,416 个按时、9,596 个迟到。旧报告和旧检查器继续保留。
- 896 行诊断及 2,688 条预测已逐字节保全并对账。每层 768 TP、128 TN、零 FP/FN；
  子集 366 行精确匹配、544 行舍入匹配，后者包含前者；895/863 是不同向量数，
  不是独立采集数。公共七组汇总不能重建私有特征的精确交集。
- 模型导出、源模型、训练/验证文件已建立文件级关联；corrected allocator 已有
  22,638 个离线比较回执，公开重算也匹配 original/corrected 的有序结果哈希。
- 5,141,673 行已按源组、冻结行号和 39 个有序特征追到 31 份逐 PCAP CSV。
  `SOURCE_ROW_TRACE.json` 是这次已执行扫描的保留记录。缺的是父采集关系，
  不是再次计算一遍 CSV hash 或再次复述行数。
- shared-stage 的候选 Probe/Core 接入已有私有合成测试回执。原回执实际包含
  9 个 `submit/decide` 条件和 1 个直接 `select` 条件；保留其实际范围。
  本次控制器/适配器若发生代码修正，需要对新私有运行时副本执行新的集成检查，
  不能把旧回执改标为新源码通过。

先阅读当前 `PREPARATION_STATUS.json`、`retained_review/PUBLIC_REVIEW.md`、
`stage_adapter/README.md`、`source_lineage/README.md`、`PROTOCOL.md`、
`hardware/README.md` 和 `evidence_value/README.md`。较早的 follow-up 报告是历史记录，
不是当前待办清单。运行一次当前统一入口，输出到新工作目录：

```bash
python3 scripts/verify_experiment_extension.py --output "$TON_WORK_DIR/PRECHECK.json"
```

`TON_WORK_DIR` 及后续变量由你依据实际本地项目、挂载卷和既有配置发现并赋值，
不要让用户逐个填写模板。先创建真正的新输出目录。仅当相关输入或实现变了，
才重做受影响的检查；不要为增加“通过数”重复计算同一组旧结果。

## 3. 一次确定本地材料、设备与真正外部依赖

从现有项目记录找到：归档 RC1、corrected allocator 副本、stage 副本、实际
launcher/config、原始 workload/model bundle、冻结 train/validation/test、31 份
源 CSV、采集说明/PCAP/采集登记、已配置设备身份及现有 SSH 目标。记录实际路径
与逻辑名称的私有映射。不要把某个文件“存在”当作它就是已执行版本。

只对已知项目设备做一次有界连接复查。可查现有 SSH 配置、已知主机密钥、已有
设备清单及可用的既有 DHCP 记录，使用超时和单次连接尝试。身份必须与原探针
角色对应；不能忽略主机密钥变化、猜测地址或反复扫描网段。P1 的身份响应不能
代替 P2/P3 的资格。记录 DNS、TCP/SSH、身份、时钟 epoch 和运行环境分别在哪一步
失败，不把超时解释为断电。

若本地已有能力恢复正确配置、启动已授权服务或修复项目部署，就在本轮完成。
若设备需要现场通电/联网或可信身份确认，整理成一次明确的外部事项，继续离线
分支，不进行无限重试。真实外部依赖最终只按以下类别报告：

| 类别 | 需要的实际输入 | 不足以代替它的材料 |
|---|---|---|
| 三探针连接 | P2/P3 可验证的连接与对应设备身份，必要的现场供电/网络恢复 | P1 成功、配置中存在旧地址、重复 SSH 超时 |
| 父采集来源 | CSV/PCAP 分片到原始 capture/episode 的权威关系、边界与证据文件 | 文件名相似、分片编号不同、feature/hash 相同或不同 |
| 足够的独立观测 | 父关系确定后，足以形成主任务所需 train/validation/test 的真实独立采集 | 将同一次采集改名、按行切开、只删除重复行 |

第三项是第二项核实后可能出现的实际结论。若所有可用 benign 数据都来自同一父采集，
或独立组/类别不足，记录 `BLOCKED_INSUFFICIENT_INDEPENDENT_ACQUISITIONS`。
此时需要真实新采集或有适当来源说明的新数据；不得通过重新命名分片让门禁通过，
也不要无限查找同一批文件以回避这个结论。

## 4. 先把真实运行时接入、采集和分析链一次做完整

公开的 `plan_hardware.py` 只生成计划，**不会启动设备**；`score_evidence_value.py`
只核验并评分，**不会训练模型或执行 encoder**。你必须在实际私有运行时上完成相应
执行器与适配，不能只运行这两个工具后宣布实验完成。

基于现有 launcher 实现最小的扩展执行入口，绑定实际 Core、Probe、配置、模型和
采集路径。它应读取计划中的每个 arm，完成真实部署身份核对、共同状态重置、
backlog 建场、启动/结束、drain、原始日志保留及 attempt 登记。使用真实字段，保留
调用链和版本差异；不要凭公共 patch 猜造私有 API。运行器每次执行前检查：

- 计划标记为 `QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER`，适用的资格文件、
  冻结清单和部署哈希一致，campaign/arm/attempt 没有复用历史身份；
- 当前 phase、输入和允许差异与计划相符，正式冻结先于首个正式执行；
- 实际探针/Core 状态和所有需要的记录字段可以取得，而不是只在 config 中写了值。

为新活动实现原始记录到 `hardware/raw_ledger_schema.json` 的无损字段映射，并保留
原文件、记录位置和哈希。新活动的期望 arm/轮/事件清单来自新计划与 attempt 登记；
不要把它交给默认绑定原 216 臂 cohort 的旧审计入口然后修改期望值来通过。

独立分析实际 chunk 偏移与唯一服务字节，核对每探针队列连续性、每轮合计预算、
重复发送、取消/在途、最终队列及事件去向。grant 与实际服务分开记录。复用已有
独立审计器能正确支持的字段；新字段适配和实际分析函数在本轮实现、测试并运行。
原始数据没有的量留空，不能由 config 或 allocator 的自报结果补齐。

保留同一 originating probe 时钟中的 creation、result receipt、连续 observation
horizon 和 boot/clock ID；Core 等待及推理使用 Core 自身时钟。scheduled release
另作敏感性锚。实际检测/编码耗时、排队、完整输入到达、Core start/end 和返回都保留，
不能跨机器直接相减 monotonic 值推导 Wi-Fi 单向时延。报告实测端到端时长或阶段
分解时不能重复相加重叠区间；控制器有意保守叠加的经验估计须另作说明。

按实际返回端点 `result_ns - created_ns <= deadline_ns`（含等号）分类。全部生成事件
保留在分母，包括 H-NONE、拒绝、迟到和失败。缺失返回只有在可靠观察跨过 deadline
后才可判 deadline miss；未成熟观察保留 censored/bounds。基础设施异常、缺失配对、
中断和重试全部登记，慢或错误的科学结果不能成为排除理由。

## 5. Allocator：完成真实 old/corrected 对照

受影响的归档 allocator 已经确认；无需再把它当未知问题重新启动审计。以已核对的
original 和 corrected 副本为起点，确认本轮真实部署差异仅为 allocator、已声明的
整数余数优先级及必要版本/接口记录。新采集仪表须两版相同。保留 launcher 相位、
nominal/creation 锚、selector、utility、模型、工作负载和服务语义。

主比较为三探针 synchronized independent I-QPG，low `131072 B/round`，`v=1`，
两版组成每个完整物理 block。是否加入 mid 对照须在 pilot 前冻结；选择后一直保留。
使用 5 warm-up、90 measured、最多 200 drain 的已确认窗口语义。先验证真实状态重置
与完整采集，再执行独立 pilot；根据其变化与预设精度/资源目标确定固定正式 block 数。
这个决定由你在看正式结果前写明并冻结，不需要逐步询问用户。

真实资格完成后生成并执行 pilot 计划，以下变量由实际计划决策填写：

```bash
python3 supporting_material/experiment_extension/hardware/plan_hardware.py \
  --study allocator --phase pilot --blocks "$TON_ALLOC_PILOT_BLOCKS" \
  --order-seed "$TON_ALLOC_ORDER_SEED" --campaign-id "$TON_ALLOC_PILOT_ID" \
  --qualification "$TON_ALLOC_QUALIFICATION" --output "$TON_ALLOC_PILOT_PLAN"
```

活动 ID 使用 `TON_EXT_ALLOC_` 前缀。planner 成功退出可以只是生成了 blocked 草案，
启动前必须读取其 `execution_qualification`，不能只检查进程 exit 0。

pilot 后依第 7 节冻结和执行正式活动。统计 old/corrected 的未利用可服务字节、action
轨迹、队列演化、按时 Core 返回/全部生成及配对差；统计单位是新物理 block。
66/270→90/270 的软件预测不是实测的通过标准，零差、反向差和迟到全部保留。

## 6. Shared-stage：接入、16 条件校准、pilot、正式比较连续完成

在独立 RC1 副本应用当前 `stage_adapter` 代码和 patch，保留实际原始与修改后树哈希，
检查私有 Probe/Core 的数据流和时钟语义。新的候选实现若已修改，执行当前真实集成
入口，不复用旧 10-case 回执作为新源码证明：

```bash
python3 supporting_material/experiment_extension/hardware/test_stage_runtime_adapter.py \
  "$TON_STAGE_RUNTIME" "$TON_WORK_DIR"
```

当前升级 runner 包含 26 个全部经 `submit/decide` 的合成条件；必须在实际新私有副本
运行后，才可给新源码记录这项结果。旧回执的 9 个该路径条件加 1 个直接 selector
条件不能合并、改标或作为新 26 项通过的证明。这仍是合成控制流检查。

随后完成实际 backlog 建场与采集资格：三探针保持共同
H-FULL/H-NONE 语义、同一优先级、相同 allocator 和计算/记录开销。B-backlog 是
P1/P2/P3 真实旧请求的剩余尾段 `43691/43691/43690 B`，要与 Core 已接收前缀、
事件身份和完整 payload hash 对上。首个 measured batch 前 Core 无执行中推理或
完整输入待处理作业，但旧未完成上传请求仍然存在。只在首批前建场一次，后续自然
演化；零 backlog 对照使用同样的准备/屏障机制。

前瞻校准使用 **全部 8 种 H-FULL 选中子集（空集、三种单选、三种双选、全选）×
backlog 0/B，共 16 条件**。它覆盖固定三探针请求下的 dispatch、未选中 H-NONE
计算、编码、共享上传、旧请求尾段、Core 工作、返回和状态陈旧成本。校准的选中子集
不能被误当成删除其他探针请求；空集条件也须实测实际 fallback/屏障开销。校准有
自己的 campaign 和原始记录，不能由同模型假设延迟、后来的正式完成时间或成功样本
筛选产生。

```bash
python3 supporting_material/experiment_extension/hardware/plan_hardware.py \
  --study shared_stage --phase calibration --blocks "$TON_STAGE_CAL_BLOCKS" \
  --order-seed "$TON_STAGE_CAL_ORDER_SEED" --campaign-id "$TON_STAGE_CAL_ID" \
  --qualification "$TON_STAGE_CAL_QUALIFICATION" --output "$TON_STAGE_CAL_PLAN"
```

真实执行全部预定校准条件。profile 只使用每个校准 arm 的**首个 measured batch**，
该行的 `analysis_stratum` 必须是 `first_measured_generation_batch`，逐探针实际
backlog、选中子集和 Core 初态均与计划匹配。每个冻结 block 的 16 条件完整进入，
不能漏掉慢条件、未返回的旧/新任务或以“成功行”替代完整校准。返回未完整或采集
不足时，保留实际失败并解决相应资格问题，不能生成看似完整的 profile。

后续 89 个 measured batch 的真实队列自然演化，原始记录全部保留，可作描述；
不再将它们套入初始 0/B 工况，也不在每轮人为恢复同样 backlog。将上述首批同域
原始时戳经有来源定位的适配器生成 capture records，再使用当前真实入口：

```bash
python3 supporting_material/experiment_extension/stage_adapter/build_profile.py \
  --records "$TON_STAGE_CAPTURE_RECORDS" --plan "$TON_STAGE_CAL_PLAN/plan.json" \
  --field-map "$TON_STAGE_FIELD_MAP" --margin-ns "$TON_STAGE_MARGIN_NS" \
  --output "$TON_STAGE_PROFILE"
```

输入 schema 以当前 `stage_adapter/README.md` 为准，由你从实际原始记录生成，不能让
用户手工填测量值。各条件独立取组件最大值，不把全选超预算所经历的多轮耗时套给
双选条件。proposal allowance 使用 probe 本地往返区间，return allowance 使用
同一 probe 本地的决策后结果返回区间；这些量有意包含重叠阶段，是保守接纳估计，
不是互斥的实测时延分解或跨机器单向网络时延。固定估计规则及 margin 的选择依据；
组件最大值加 margin 是经验参数，不是确定性物理上界。未覆盖的工况、时钟或有机 backlog 不能
假称已校准；依当前控制器规则拒绝新接纳并记录具体原因，保留已有任务的实际服务。

随后执行独立 pilot 和正式活动。两者都保持 **3 个策略 × 2 个初始 backlog = 6 条件**：
`isolated_precheck_new_bytes`、`backlog_aware_bytes`、`causal_shared_stage`。所有策略
接收同一候选集，旧任务、被拒新任务和 fallback 都有记录。首个 measured batch 是
初始 backlog 机制的主分析，全部 90 轮是预先声明的持续运行次分析。控制器每次加入
候选后重查所有先前接纳任务，不能使用未来完成时间或测试标签。

pilot 用于修复实现、仪表和工况资格及冻结参数；若因 pilot 修正控制器或校准范围，
版本化后在本轮完成受影响的独立补校准/pilot。正式冻结后不得因拒绝率、miss 或改进
不足而调 margin、删 arm、换 endpoint 或重试。正式比较报告实测覆盖/及时性取舍，
不作普遍 deadline guarantee，也不把此候选写为原 S-CQPG 的不变重跑。

## 7. 硬件正式冻结与执行：完成一次两遍绑定

所有硬件正式阶段都使用同一具体流程：

1. 基于真实 pilot 决定固定完整 block 数和精度/可行性理由。填写
   `sample_size_rule_template.json` 的真实值，状态为 `FROZEN_SAMPLE_SIZE_RULE`，
   绑定独立 pilot ID 与报告哈希。不能把 seed 数作为样本量，也不能看到显著性才停。
2. 填写真实 `qualification_template.json` 的 facts 和 evidence，所有 true 都有可读
   实际证据及 SHA-256。正式 freeze 尚未存在时，生成第一份 formal 草案是允许的；
   它应仍被阻塞，不能开始采集。
3. 从该计划复制确切 study、campaign、blocks、order seed、控制条件及 protocol/
   planner/schema/sample-rule/pilot 身份到 `formal_freeze_template.json`。其中
   `condition_order_sha256` 使用 `plan.json` 给出的值，不擅自换成 CSV 文件的 hash。
   `qualification_evidence_sha256` 绑定所有适用证据，但不包含 receipt 自身。
4. 在真实 campaign registry 登记首次正式执行前的冻结，设置
   `FROZEN_FOR_FORMAL_EXECUTION`，把此文件及哈希加入 qualification；使用同样
   参数生成到另一个新目录，确认精确绑定全部通过。
5. 冻结实际 runtime、模型、workload、校准、计划、资格与分析输入，真实部署前后
   用同一逻辑名称和文件验证身份。`freeze_inputs.py` 接收的是文件，不接收目录；
   runtime 树须先用实际 tree manifest/snapshot 文件表示。

正式 planner 的实际命令如下，`TON_STUDY` 为 `allocator` 或 `shared_stage`：

```bash
python3 supporting_material/experiment_extension/hardware/plan_hardware.py \
  --study "$TON_STUDY" --phase formal --blocks "$TON_FORMAL_BLOCKS" \
  --order-seed "$TON_ORDER_SEED" --campaign-id "$TON_FORMAL_ID" \
  --qualification "$TON_QUALIFICATION" --sample-size-rule-file "$TON_SAMPLE_RULE" \
  --output "$TON_FORMAL_PLAN"
```

若 allocator 设计事前包含 mid 对照，两次生成均加 `--include-mid-control`。同样以真实
文件调用冻结入口，并为每个其余依赖重复 `--input NAME=FILE`：

```bash
python3 supporting_material/experiment_extension/freeze_inputs.py freeze \
  --input runtime_manifest="$TON_RUNTIME_MANIFEST" --input plan="$TON_FORMAL_PLAN/plan.json" \
  --input qualification="$TON_QUALIFICATION" --manifest "$TON_INPUT_FREEZE" \
  --label "$TON_FORMAL_ID"

python3 supporting_material/experiment_extension/freeze_inputs.py verify \
  --input runtime_manifest="$TON_RUNTIME_MANIFEST" --input plan="$TON_FORMAL_PLAN/plan.json" \
  --input qualification="$TON_QUALIFICATION" --manifest "$TON_INPUT_FREEZE"
```

示例只展示参数形式；实际冻结包含所有已声明输入，验证时的逻辑名称集合必须完全
相同。然后由第 4 节真实执行器逐 arm 执行计划，保留所有 attempt、原始结果、日志和
偏离，完成全量独立审计、按 block 配对分析与预声明区间。

## 8. 独立内容实验：从父来源到真实训练、推理和评分一次做完

与设备分支并行追溯父 capture/episode。先读取实际采集记录和 provider 的提取/
分片说明，将每个已追溯 CSV 对应到真正父采集。不要按文件名或编号直接宣布独立。
当前公开检查及准备入口为：

```bash
python3 supporting_material/experiment_extension/source_lineage/prepare_capture_split.py verify-public

python3 supporting_material/experiment_extension/source_lineage/prepare_capture_split.py prepare \
  --mapping "$TON_CAPTURE_MAPPING" --splits "$TON_CAPTURE_SPLITS" \
  --output "$TON_CAPTURE_PREPARED"
```

映射与 split 文件由你依据真实来源生成；schema 见 `source_lineage/README.md`。它们
必须完整覆盖所用来源，父关系的证据文件和哈希可读可核。工具能检查声明和绑定，
不能替代你核实父关系，也不能证明某个填写的 ID 真的独立。相关探针、同父采集的
分片及重复事件整体留在同一组、同一划分。

若来源满足独立划分条件，继续完成下列实际工作，不在“mapping完成”处交接：

- 冻结一个二分类主任务、预测单位、raw→binary 映射、三种表示、可用观测窗口、
  主比较、分母和统计规则。用训练数据确定标准化、特征选择及近重复规则；保留
  exact 和近重复的搜索覆盖、阈值、分组/处理决定。近重复审计报告必须实际生成，
  不能只在 protocol 中填 `completed`。
- 建立新的训练/验证/测试版本。所有训练相关产物，包括 alert 编码前的 light
  detector、特征变换、共同 consumer 和阈值，都在新的 train/validation 上拟合
  并记录来源。只有有可核实训练来源且与新 test 父采集分离的既有模型才可复用。
  旧模型留作历史；不能仅给旧模型换一份测试清单就称独立 held-out。
- 实现并执行真实 encoder/model runner：encoder 可以看该时刻可用的原观察，
  看不到标签；consumer 只能看到对应 decoded 表示和冻结模型，不能凭 ID/路径
  取回被省略特征或真值。采用共同 model/threshold 时支持缺失字段；如果必须
  采用不同 consumer，先正式扩展契约并声明系统比较，不伪填相同 model ID。
- 生成独立于成功预测的完整 `groups.csv`、`corpus.csv`、`occurrences.csv`，并对
  每个 occurrence 实际产生 alert/summary/full 三条预测或明确失败状态。保留
  每次模型调用、unpadded representation/payload 字节和哈希、有效字段、padding、
  计算与版本信息。仅创建 predictions 表不是执行模型的证据。

首先执行 `information_only`，输出 schema 按现有 scorer 的严格字段集，随后评分：

```bash
python3 supporting_material/experiment_extension/evidence_value/score_evidence_value.py \
  --protocol "$TON_VALUE_PROTOCOL" --groups "$TON_VALUE_GROUPS" \
  --corpus "$TON_VALUE_CORPUS" --occurrences "$TON_VALUE_OCCURRENCES" \
  --predictions "$TON_VALUE_PREDICTIONS" --output "$TON_VALUE_REPORT"
```

真实运行不使用 `--allow-synthetic-fixture`。报告全部生成/scored/missing、三层
TP/FP/FN/TN、precision/recall/F1、payload 与计算成本、各独立组和 pooled 结果。
按冻结设置用相同独立组做配对重抽样；独立组不足或观察未成熟时不造区间。保留
零差、负差和失败，不为了出现 full 优势换任务、换测试子集或改阈值。

之后对同一冻结任务与 qualified held-out 工作负载执行真实通信约束阶段。实际
测量每种表示在 originating probe 的 creation/return/horizon，并保留全部生成
分母，单独冻结 `transport_measured` protocol 后调用同一 scorer。主要指标是
按时且正确返回/全部生成；conditional F1、选中率与条件及时率分别给出。
不能把历史硬件及时率乘另一批数据 accuracy 声称测得联合收益；软件服务模型结果
也不能作为 `time_source=measured` 送入该入口。

如果权威父来源或足够独立采集确实不存在，将该分支停在准确的输入状态，保留
已经完成的来源核对和可用 runner；不得把896行诊断包装成正式实验，也不新增
同样的文件前缀诊断来代替缺失依赖。继续完成其他分支和最终论文交付。

## 9. 同一轮完成论文、PDF、完整源码包与最终交付

每个真实结果通过相应审计后，立即更新主文/补充材料、code–evidence 对照和数字
来源，区分旧数据重审、新真实离线模型实验、新物理实验与合成测试。新效果声明
只能来自实际对应结果；未执行的部分使用准确状态。保持旧理论与未受影响数字，
不要为统一术语静默改变历史锚、分母、方法名或运行版本。

完成两份 PDF 编译和页面检查，使用真实构建记录及当前输入/PDF hash：

```bash
bash scripts/build_submission.sh
python3 submission/validate_submission.py
python3 scripts/verify_submission.py
python3 scripts/verify_campaign_audit.py
python3 scripts/verify_methodology.py
python3 scripts/verify_methodology_revision.py
python3 scripts/verify_experiment_extension.py --output "$TON_WORK_DIR/FINAL_VERIFICATION.json"
```

使用当前 `submission/BUILD_INSTRUCTIONS.md` 要求的真实 IEEEtran 环境。同步实际
新构建 metadata，更新 submission 清单，并检查新增结果页面及全篇版面；编译器
不在当前环境时先完成可行安装/既有构建方式，无法取得时清楚保留最后合格 PDF，
不能把旧 PDF 说成新源码的产物。

最终一次性交付：

1. 实际实验结果、所有尝试与阻塞状态、来源及分析代码；私有完整证据留本地。
2. 当前主文/补充 PDF，可在完整仓库重建的 LaTeX 源码及所需图表/依赖。
3. 一个可直接下载的审阅 ZIP：PDF、完整可编译源码、中文结果/限制说明和校验表。
   不只给外置盘绝对路径。公共代码与可公开结果推送同一个 PR，核对远端 HEAD。
4. 简短中文收尾表：每项实际执行到哪、得到什么、影响哪些论文结论、还缺什么
   真正外部输入。所有已完成项从后续待办删除。

任何未完成项只写它的真实依赖和可直接恢复的阶段/输入，不再拆成一轮轮“修一个
检查器—写一份报告—询问是否继续”。仅当新结果揭示实际实现问题时修复相关范围，
验证后继续本次工作。完成全部可执行事项后再给最终报告。
