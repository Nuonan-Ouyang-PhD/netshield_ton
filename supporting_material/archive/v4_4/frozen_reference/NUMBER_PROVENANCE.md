# NUMBER PROVENANCE — 论文数字来源登记表

> 数据基线：实验仓 `netshield-real-experiments`，commit `a24b909`，
> tag `v0.4.7-analysis-rev2-session-level`（REV2，session 级统计）。
> 本表登记论文可用的每个数字 → 来源文件 → 行号/字段。
> 文件路径均相对 `data/processed/main_formal_S01_S12/`（交付包内 `data/` 目录）。
> 所有值为机器读取原样登记，未做四舍五入（论文引用时自行取位）。

## 1. 实验规模事实

| 论文数字 | 值 | 来源文件 | 位置 |
|---|---|---|---|
| 正式 session 数 | 12 (S01–S12) | `data/analysis_manifest.json` | 输入路径列表（S01…S12） |
| 调度臂 | 6 (A–F) × 3 容量 × 12 session = 216 臂 | 同上 | 216 个输入路径 |
| 设备运行数 | 648 (216 × 3 probes) | `data/summary.csv` | 648 数据行 |
| measured 窗口总数 | 58,320（648 × 90；warmup 5 窗/设备已剔除） | `data/summary.csv` | `windows` 列求和 |
| 每方法 measured 窗口 | 9,720 | `data/summary.csv` | 按方法聚合 `windows` |
| staging 输入 | probe 61,560 行 + core 61,560 行（含 warmup 5×648=3,240/侧） | `data/analysis_manifest.json` | `probe_records`、`core_records` 字段 |
| 统计单元 | session，n=12；36 个 (session, capacity) cell 仅描述 | `data/paired_comparisons.csv` | 全行 `n_paired_sessions=12, n_capacity_cells=36` |

## 2. Table 1（方法总览）— 来源 `tables/table1_method_overview.csv`（每行一方法）

| 数字 | A | B | C | D | E | F | 字段 |
|---|---|---|---|---|---|---|---|
| n_runs | 108 | 108 | 108 | 108 | 108 | 108 | `n_runs` |
| timely_f1_mean（108 run 宏平均） | 1.0000 | 1.0000 | 0.9332 | 1.0000 | 1.0000 | 1.0000 | `timely_f1_mean` |
| fpr_mean（108 run 宏平均） | 0.0000 | 0.0000 | 0.2845 | 0.0000 | 0.0000 | 0.0000 | `fpr_mean` |
| mean_e2e_ms | 672.9 | 673.1 | 693.2 | 660.1 | 670.8 | 665.0 | `mean_e2e_ms` |
| deadline_violation_rate | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | **0.000103** | `deadline_violation_rate` |
| queue_violation_rate | 全 0.000000 | | | | | | `queue_violation_rate` |
| delivered_gen_ratio_measured | n/a | 1.000 | 0.667 | **1.004** | 1.000 | 1.000 | `delivered_gen_ratio_measured` |
| delivered_gen_ratio_full (95 窗含 warmup) | n/a | 1.000 | 0.667 | **0.998** | 1.000 | 1.000 | `delivered_gen_ratio_full` |
| max_queue_mb (单位 MiB) | 0.00 | 0.00 | **7.92** | **0.08** | 0.00 | 0.00 | `max_queue_mb`（bytes/2²⁰） |

Table 1 LaTeX 同源：`tables/table1_method_overview.tex`。
口径注：timely-F1/FPR/E2E/violation rates 均为 108 个 device-run 的非加权宏平均（macro mean，即表内 `*_mean` 字段），
不是 9,720 窗混淆矩阵池化的微平均；C 的微平均参考值为 F1 0.933589 / FPR 0.282292（caption 已注明）。
E2E 为 108 个 run 均值的均值；violation rate 为逐 run 违规率（violations/windows）后再平均。
MaxQ 为 648 run 中的最大字节积压（8,301,290 B = 7.92 MiB，C；87,382 B = 0.08 MiB，D），单位为 MiB（1 MiB = 2²⁰ B）。
D 的 measured 1.004 由 warmup 积压排水所致（warmup 期 D 低容量 gen 9,732,096 B / deliv 6,586,344 B，
measured 期 deliv 超出 gen +3,145,680 B），全 95 窗比值 0.998。

## 3. 主要对比（Table 2 正文版）— 来源 `tables/table2_primary_contrasts.csv` + `data/paired_comparisons.csv`

25 行 = 5 指标 × 5 个对 F 的对比。关键行（CSV 行号指 `table2_primary_contrasts.csv`）：

| 论文事实 | 值 | table2 CSV 行 | paired_comparisons.csv 行 |
|---|---|---|---|
| C vs F timely-F1 均差 | -0.06649298546983169 | 23 | 42 |
| C vs F timely-F1 95% CI | [-0.07008322686884641, -0.06263820685879933] | 23 | 42 |
| C vs F timely-F1 raw p / Holm p | 0.00048828125 / 0.00732421875 | 23 | 42 |
| C vs F FPR 均差 | +0.2817162281160578 | 3 | 43（fpr） |
| C vs F FPR 95% CI | [0.26799149970762515, 0.296214314521937] | 3 | 43 |
| C vs F FPR Holm p | 0.00732421875 | 3 | 43 |
| C vs F mean E2E 均差 | +28.207131292283947 ms | 13 | 44 |
| C vs F mean E2E 95% CI | [19.193972632613207, 36.5629893222222] | 13 | 44 |
| C vs F mean E2E raw p / Holm p | 0.00146484375 / 0.0205078125 | 13 | 44 |
| C vs D mean E2E 均差 | +33.150594023250996 ms | tableS1 39 | 39 |
| C vs D mean E2E Holm p | 0.0146484375 | tableS1 39 | 39 |
| B vs F timely-F1 均差（非劣效主对比） | 0.0 | 25 | 67 |
| B vs F deadline-violation 均差 | -0.00010288065843621399 | 10（L7–11 对 E/C/A/B/D 全部五方法均为该值） | 70 |
| B vs F deadline-violation 95% CI | [-0.00030864197530864197, 0.0] | 10 | 70 |
| E vs F mean E2E 均差 / Holm p | +5.813498040843608 / 1.0 | 12 | 24 |
| D vs F mean E2E 均差 / Holm p | -4.943462730967052 / 1.0 | 16 | 75 |
| A/B/D/E vs F timely-F1/FPR | 均差 0.0，p=1.0 | FPR L2/4/5/6，timely L22/24/25/26（按 E/A/B/D 序） | 对应行 |
| queue-violation 全部对比 | 均差 0.0，p=1.0 | 17–21 | 对应行 |

方向约定：`mean_difference = method_a - method_b`（列名见 CSV 表头）。
Table 2 LaTeX：`tables/table2_primary_contrasts.tex`；完整 75 项：`tables/tableS1_full_contrasts.csv/.tex`（= 仓内 `appendix_full_contrasts.csv/.tex`）。

## 4. 非劣效结论 — 来源 `data/non_inferiority.json`（全字段）

| 字段 | 值 |
|---|---|
| comparison | shielded_dpp vs fixed_summary (timely F1) |
| mean_difference_F1_shielded_minus_summary | 0.0 |
| non_inferiority_margin | -0.02 |
| meets_non_inferiority | true |
| holm_adjusted_p_value | 1.0 |
| n_sessions | 12 |
| sign_flip_method | exact |

## 5. C 分容量退化（描述性）— 来源 `data/summary.csv` 按方法×容量池化混淆矩阵重算

| 容量 | C timely-F1 | C FPR | tp/fp/fn/tn |
|---|---|---|---|
| high | 1.0000 | 0.0000 | 2600/0/0/640 |
| low | 0.9375 | 0.2797 | 2452/179/148/461 |
| mid | 0.8634 | 0.5672 | 2251/363/349/277 |

其他五方法在三个容量下 F1=1.0、FPR=0（tp=2600, fp=0, fn=0, tn=640 各容量）。
C 在全部 12 个 session 的 session 级池化 F1 均 < 1.0（0.9238–0.9447），
这是 sign-flip p=0.000488（12/12 同向）的数据基础。
C 的证据年龄违规（oldest_queue_age > 10 窗）：low 2916/3240 = 90.0%、
mid 2376/3240 = 73.3%、high 0/3240；合计 5292/9720 = 54.4%
（`data/summary.csv` `queue_age_violations` 列按容量聚合）。

## 6. 动作一致性 — 来源 `action_consistency/ef_action_consistency_results.json` + `.txt`

| 事实 | 值 |
|---|---|
| E vs F 键集合 | 完全一致（9,720 窗） |
| E vs F 动作差异数 | 0 |
| D vs F 键集合 | 完全一致（9,720 窗） |
| D vs F 动作差异数 | 5,940（设计预期：independent-DPP 无共享接纳） |
| D→F 差异类型 top | H_NONE→H_SUMMARY 2736；H_FULL→H_SUMMARY 1872；M_SUMMARY→H_SUMMARY 792；H_NONE→H_FULL 540 |
| D vs F 生成字节 | 747,307,008 B vs 654,704,640 B（D 高 14.1%）——`data/summary.csv` `generated_bytes` 聚合 |

## 7. F 唯一 deadline violation 细节（如论文需要）— 来源 staging 原始窗口（S09/high/F/P3/w80）

| 字段 | 值 |
|---|---|
| 位置 | S09, high, P3, measured window 80 |
| decision_latency_ms | 1315.090898（deadline 1000.0） |
| evidence_completion_ms | 1578.689249 |
| evidence_receipt_rtt_ms | 1311.904469（邻窗 ~66/63 ms） |
| action | H_FULL；queue_bytes=0；温度/RSSI/重传正常 |
| 同窗 P1/P2 | decision_lat 132.8 / 97.5 ms，无违规 |
| 定性 | 单窗口瞬时传输抖动，非持续拥塞 |

## 8. 图件 — 来源 `figures/`

| 图 | 文件 | 内容 |
|---|---|---|
| Fig 1 | `fig1_capacity_interaction.png` | 容量×方法交互：session 均值 ± 95% bootstrap CI（10,000 次，seed=20260904），三 panel（timely-F1/FPR/E2E） |
| Fig 2 | `fig2_e2e_by_capacity.png` | 12 个 session 均值 E2E 箱线图，按容量分面 |

## 9. 复现命令（实验仓 `netshield-real-experiments`，分支 `fix/v0.4.7-formal-gates`，`a24b909`）

```
.venv/bin/python3 -m netshield.analyze --raw-root data/processed/analysis_input_S01_S12 --output data/processed/main_formal_S01_S12
.venv/bin/python3 scripts/generate_paper_tables.py
.venv/bin/python3 scripts/generate_paper_figures.py
.venv/bin/python3 scripts/supplementary/ef_action_consistency.py
.venv/bin/python3 -m unittest discover -s tests -p 'test_*.py'   # 62/62 OK
```
