# 三探针硬件扩展

原 216 臂主实验与 36 臂 CRFA 保留各自的设备与统计口径。下表仅登记新活动。QUAL 为两种初始物理积压的工程资格检查。

| 活动 | 计划臂 | 登记尝试 | 重建完成臂 |
|---|---:|---:|---:|
| [TON_EXT_ALLOC_4B8_FORMAL_20261123_01](TON_EXT_ALLOC_4B8_FORMAL_20261123_01/arms.json) | 8 | 8 | 8 |
| [TON_EXT_ALLOC_4B8_PILOT_20261122_01](TON_EXT_ALLOC_4B8_PILOT_20261122_01/arms.json) | 2 | 2 | 2 |
| [TON_EXT_STAGE_4B8_CAL_20261123_01](TON_EXT_STAGE_4B8_CAL_20261123_01/arms.json) | 16 | 5 | 4 |
| [TON_EXT_STAGE_4B8_CAL_20261123_02](TON_EXT_STAGE_4B8_CAL_20261123_02/arms.json) | 16 | 16 | 16 |
| [TON_EXT_STAGE_4B8_FORMAL_20261123_01](TON_EXT_STAGE_4B8_FORMAL_20261123_01/arms.json) | 36 | 36 | 36 |
| [TON_EXT_STAGE_4B8_PILOT_20261123_01](TON_EXT_STAGE_4B8_PILOT_20261123_01/arms.json) | 6 | 6 | 6 |
| [TON_EXT_STAGE_4B8_QUAL_20261123_01](TON_EXT_STAGE_4B8_QUAL_20261123_01/arms.json) | 2 | 2 | 2 |

各目录含原始材料哈希、每个角色的动作与队列、同钟时差和配对差。用 Python 3.11 或更新版本，以活动导出目录作为参数运行 verify_results.py，可复算字节守恒、周期及两个时间锚下的及时率。

[内容实验的来源核对](CONTENT_INPUT_REVIEW.md) · [存储修订](storage.json) · [采集源代码](acquisition/)

## 本次实测结果

Allocator 正式对照共 4 对。original 和 corrected 各有 1,080 个生成事件；两版分别接纳 264 和 360 个全证据请求，全部最终返回，1 秒内返回数均为 0。每臂未利用的可服务字节分别为 144 和 0。

Shared-stage 校准前一次活动完成 4 臂，第 5 臂在一次 P2 管理链路健康检查超时后中止。该活动的 5 次尝试单独保留。新活动的 16 个条件各贡献一个首批实测样本，profile 的额外 margin 为 0。独立 pilot 和正式活动分别登记。

| 正式策略及初始积压 | 首批生成 | 接纳 H_FULL | 首批按时全结果 | 90 轮生成 | 90 轮按时全结果 |
|---|---:|---:|---:|---:|---:|
| B0_P1_P2_P3_backlog_aware_bytes | 18 | 12 | 8 | 1620 | 1044 |
| B0_P1_P2_P3_causal_shared_stage | 18 | 0 | 0 | 1620 | 0 |
| B0_P1_P2_P3_isolated_precheck_new_bytes | 18 | 12 | 8 | 1620 | 1045 |
| B131072_P1_P2_P3_backlog_aware_bytes | 18 | 6 | 6 | 1620 | 1034 |
| B131072_P1_P2_P3_causal_shared_stage | 18 | 0 | 0 | 1620 | 0 |
| B131072_P1_P2_P3_isolated_precheck_new_bytes | 18 | 12 | 0 | 1620 | 0 |

正式独立内容价值与通信约束及时正确率均无合格测试队列。仍需将冻结输入对应至可核验的父采集、边界及足够独立的采集组。没有在原 896 行诊断样本上另行宣称分组独立性。

## 复算校准参数

在本目录运行 `python3 -B verify_calibration.py`。公开的 [16 组逐阶段时序](calibration_relative.jsonl) 为每臂的 Core 和每台探针分别平移时间原点，并以角色代替私有时钟标识。同一时钟上的全部纳秒差保持原值。脚本用采集时的计算函数复算 16 组参数，并逐项与[部署使用的 profile](physical_profile.json) 核对。
