# 定向补实验执行记录

起点为 PR #3 的 07ce1520166a29feae96766bfbd51dbc9788a1f9。本轮的实际物理采集数为零。

| 分支 | 已执行 | 资格或结果边界 |
|---|---|---|
| 私有 RC1 | 在独立副本上经真实 Coordinator.submit/decide 检查 26 种合成条件；增加逐阶段采集后再次执行同一套检查，两个回执分别绑定各自的运行时 | 同一套检查在两个源码状态下执行，条件数仍为 26。 |
| 传输与建场 | 用本机回环 TCP、真实 Core/Probe 序列化与重组、模拟探针输入和加速等待，分别检查 backlog 0、131072 B 及两个 allocator。每组 5 个预热轮、90 个测量轮、4 个测试 drain 轮，重建每组 270 个测量事件。后台工况逐设备核对旧请求尾段、Core 前缀和完整 payload 身份 | 测试用时、模型输出与回环及时率只用于调试。试验中使用的探针角色都位于同一台主机。 |
| 实际设备 | 在已登记地址上各做一次有界连接，保留私有输出；P1 的身份、型号、序列号、架构、内核与归档一致，可取得 boot epoch。电源位为零，NTP 同步标志返回 no。P2 的三个已登记名称无法解析、三个地址连接超时；P3 的一个名称无法解析、一个地址连接超时 | 恢复 P2/P3 的可信连接，确认 P1 时钟同步，再做三机共同资格。当前无法判断 P2/P3 电源状态。 |
| Allocator | 生成两个低容量条件的私有启动输入，取原 F12_S01 的冻结 workload 和 seed。两版使用同一套仪表，原版与修正版的运行时身份分别保留 | 设备资格、物理 pilot、区组数与正式协议冻结、采集及配对效应均待执行。没有物理效应估计。 |
| Shared-stage | 为八种选中子集与两种初始 backlog 生成全部 16 个独立启动配置，共用冻结 F12_S02 workload。未取得资格的计划在启动器建立任何设备连接前被拒绝 | 真实部署、16 条件物理校准、profile、独立 pilot 和 6 条件正式比较均待执行。 |
| 新划分与消融 | 复用已关闭的源行溯源。查阅原提供方两个说明文件和数据集目录说明。提供方描述了合并和切分 PCAP 的步骤。当前能核到 31 份逐 PCAP 特征表；对其中每份文件到独立父采集、起止边界的权威映射仍缺失 | 独立采集数未知。合格新划分、跨划分 exact/near 审计、基于该划分重新拟合、三种表示比较及物理通信约束下的及时正确率均待执行。 |

已关闭的 216 臂私有重审、896 行诊断和 5,141,673 行私有源行扫描沿用原回执。新工作对原硬件结果或论文效应量没有提供新的估计。正文更新位于 Shield separation，补充材料更新位于 Source-Row Trace and Shared-Stage Implementation Status。

## 复核与恢复

- 两份 26 条件逐项回执位于 stage_adapter/private_integration.json 和 stage_adapter/final_runtime_26.json。旧 10 项回执单独归档。软硬件状态与四组回环文件哈希见 CLOSEOUT_RECEIPT.json。
- 在全新归档 RC1 副本的顶层应用 stage_adapter/physical_capture_hooks.patch，再复制 stage_adapter/stage_admission.py 到 netshield/。从该副本新建 corrected 版本并应用 hardware/instrumented_allocator.patch。两版都用私有 RC1 的 identity_manifest 生成并校验派生身份。候选树的期望 SHA-256 在 hardware/candidate_identity.json。
- 私有回归入口为 hardware/test_stage_runtime_adapter.py RUNTIME SCRATCH，以及 hardware/test_private_transport.py RUNTIME NEW_DIRECTORY BACKLOG。后者接受 --study allocator。每次均使用全新目录。正式实验必须使用设备资格、独立物理时钟和冻结计划。
- hardware/prepare_bundles.py 读取真实 RC1 的配置、动作、三个工作负载文件及 seed，生成每条件独立启动输入。hardware/execute_hardware.py 启动前重建计划、核对输入集合、运行时变体和各设备文件身份。仅在资格实际满足后使用 --freeze-only 写入输入冻结，再运行启动器。私有启动输入均位于外置盘；既有活动及工作负载原件保持冻结。
- hardware/reconstruct_attempt.py 读取 Core 原始记录与三个 Probe 的原始归档，输出带原文件 SHA 和行号的事件、服务、chunk 与 admission 记录，以及首批和全部测量轮的结果界限。完整路径还需用真实设备回包确认。中断或不完整尝试保留原始日志、退出与收集状态，不能用完整成功样本替代。启动器按新 campaign 排他登记，不自动重试。正式物理配对、置信区间与纳入决定须基于已冻结的真实 pilot 和实际 attempt 登记。
- 私有 merged/split 说明来源与公开数据说明一致。[UNB CICIoT2023 数据集](https://www.unb.ca/cic/datasets/iotdataset-2023.html)
