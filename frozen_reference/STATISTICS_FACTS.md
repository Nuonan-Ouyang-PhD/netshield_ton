# STATISTICS FACTS — 统计方法事实表

> 数据基线：实验仓 `netshield-real-experiments`，commit `a24b909`，
> tag `v0.4.7-analysis-rev2-session-level`（REV2）。
> 所有条目以代码实现（`netshield/analyze.py`、`scripts/generate_paper_figures.py`，
> 即 `a24b909` 版本）与产物文件为准。

## 1. 推断单元与配对结构

| 项 | 事实 | 依据 |
|---|---|---|
| 独立单元 | **session**（n=12，S01–S12） | `analyze.py::paired_comparison`（`a24b909`） |
| session 内聚合 | 三个容量 × 三设备先池化：混淆矩阵逐元素相加；E2E/违规窗口池化 | 同上 |
| 36 个 (session, capacity) cell | 仅作描述性报告（`n_capacity_cells=36` 列），不进入推断 | `paired_comparisons.csv` 每行 |
| 对比家族 | 15 个方法对 × 5 指标 = **75 项对比** | `paired_comparisons.csv` 75 数据行 |
| 指标 | timely_f1、fpr、mean_e2e_ms、deadline_violation_rate、queue_violation_rate | 同上 |

## 2. 非劣效检验（预注册主对比）

| 项 | 值 |
|---|---|
| 对比 | shielded-DPP (F) vs fixed-summary (B)，timely-F1 |
| 方向 | **F − B**（`mean_difference_F1_shielded_minus_summary`） |
| 非劣效 margin | **-0.02**（绝对值；协议 EXPERIMENT_PROTOCOL.md L83） |
| 判定准则 | Δ(F−B) > -0.02 即 meets |
| 效应量 | mean difference = **0.000**（12 session 全部差值为 0） |
| 95% CI | [0.000, 0.000]（session-cluster bootstrap，见 §4） |
| 结论 | meets_non_inferiority = **true** |
| 来源 | `data/non_inferiority.json`（含 n_sessions=12、sign_flip_method=exact） |

## 3. Exact sign-flip 检验

| 项 | 事实 |
|---|---|
| 方法 | **exact 枚举**：全部 2^n 符号翻转（n=12 → 2^12 = 4,096 枚举） |
| 双侧 p 定义 | \|翻转后均值\| ≥ 观测 \|均值\| 的枚举比例 |
| 方向 | 检验 mean(method_a − method_b) = 0；permutation 差值方向为 CSV `mean_difference = method_a − method_b` |
| 本次结果 | 75/75 对比 `sign_flip_method=exact`（n=12 ≤ exact_max_n=22，无需置换回退） |
| 最小可达 p | 0.00048828125 = 2/4096（12/12 同向时） |
| 回退路径（本次未触发） | n>22 时置换 100,000 次、seed=20260828；normal 近似仅显式请求 |
| 参数位置 | `analyze.py::sign_flip_test(diffs, method="exact", exact_max_n=22, seed=20260828)` |

## 4. Bootstrap 置信区间

| 项 | 事实 |
|---|---|
| 结构 | **session-cluster bootstrap**：以 session 为整块（本设计每 session 一块）有放回重采样 |
| 次数 | **10,000** 次（`n_bootstrap=10000`） |
| 种子 | **20260828**（`analyze.py::cluster_bootstrap_ci`，分析管线内所有 CI） |
| 置信水平 | 95%（2.5 / 97.5 百分位） |
| 图件 CI（Fig 1） | 10,000 次，seed=**20260904**（`generate_paper_figures.py` BOOT_SEED + 每 series 偏移后缀；与分析 CI 相互独立） |

## 5. Holm 校正

| 项 | 事实 |
|---|---|
| 方法 | 标准 Holm–Bonferroni step-down：排序后 ×(n−rank)，累计 max，截断于 1 |
| 校正范围 | **按指标分族**：每族 = 同一 metric 的 15 个方法对 p 值（5 族 × 15） |
| 不跨族 | timely_f1 族与 fpr 族分别校正（例：C 相关对比 Holm p=0.0073 = 15×0.000488） |
| REV2 修正历史 | REV1 曾有 Holm 单调性 bug（min→max）与 sign-flip 隐式切换，均已修复并归档（`audits/ANALYSIS_CORRECTION.md` §1, §7） |
| 实现 | `analyze.py::holm_correction` |

## 6. 显著性结果速查（Holm 校正后，α=0.05）

| 对比 | 指标 | 均差 | raw p | Holm p | 显著 |
|---|---|---|---|---|---|
| C vs F（及 C vs A/B/D/E，值同） | timely_f1 | -0.0665 | 0.000488 | 0.00732 | 是 |
| C vs F（及同族） | fpr | +0.2817 | 0.000488 | 0.00732 | 是 |
| C vs D | mean_e2e_ms | +33.1506 | 0.000977 | 0.01465 | 是 |
| C vs F | mean_e2e_ms | +28.2071 | 0.001465 | 0.02051 | 是 |
| C vs A / C vs B / C vs E | mean_e2e_ms | +20.3 / +20.1 / -22.4 | 0.068 / 0.084 / 0.042 | 0.820 / 0.929 / 0.546 | 否 |
| A/B/D/E/F 两两之间全部指标 | — | ≈0 | — | 1.0 | 否 |
| deadline/queue violation 全部对比 | — | ≈0 | — | 1.0 | 否 |

注意（写作红线）：
- 不得声称 C 的 E2E "显著高于所有方法"——仅对 D、F 显著；
- F 的 deadline-violation 率为 1.03e-4（1/9,720），不得写成"零违反"；
- D measured Deliv/Gen=1.004 须与全 95 窗 0.998 同时报告；
- E/F 动作 9,720/9,720 一致应表述为"shield 未改变可行决策"，不是"F 优于 E"。

## 7. 数据排除口径

| 项 | 事实 |
|---|---|
| 纳入 | 仅 `data/raw/main/S01–S12`（campaign `paper_eligible=true`） |
| 排除 | pilot S00、TIE00、HORIZON00、MG00、BASE00 全部 `paper_eligible=false`，不进入任何正式统计 |
| 窗口口径 | 仅 `window_phase=measured`（每设备 5 warmup + 90 measured = 95 总窗；warmup 剔除） |
| 输入快照 | `data/processed/analysis_input_S01_S12`（6 道门禁构建、字节级校验，SHA256_MANIFEST `4b065bd1…beff`） |
