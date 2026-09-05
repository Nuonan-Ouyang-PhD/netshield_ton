# PROVENANCE — NetShield ToN 真实数据交付包

## 锁定的数据基线

| 项 | 值 |
|---|---|
| 仓库 | `netshield-real-experiments`（本地路径 `/Users/nuonanouyang/ToN/NetShield_v0.4.2/netshield-real-experiments`） |
| 分支 | `fix/v0.4.7-formal-gates` |
| **统计基线 Commit** | **`a24b90936bae3e53b8bf18026fcd4c2f545b39f4`**（`a24b909`） |
| **统计基线 Tag** | **`v0.4.7-analysis-rev2-session-level`**（annotated，指向同一 commit，未移动） |
| 统计基线提交时间 | 2026-09-04T18:37:49+10:00 |
| **文档修订 Commit** | **`92c31087f7772399b24c32a7506b993fb040e87f`**（analysis-documentation：仅文档/打包/测试修正，统计数值零变化） |
| **文档修订 Tag** | **`v0.4.7-analysis-rev2-doc-clean`**（指向文档修订 commit） |
| 统计版本 | REV2（session 级配对，取代 REV1 36-cell 伪重复版本） |
| 统计基线提交信息 | `analysis: rev2 session-level pairing, strict ef-consistency, paper tables` |

## 本次文档修订内容（统计数值零变化）

1. Table 1 口径修正：`timely_f1_mean`/`fpr_mean` 标注为 108 device-run 非加权宏平均（非 9,720 窗微平均；C 微平均参考 F1 0.933589 / FPR 0.282292 已在 caption 注明）；
2. MaxQ 单位修正：表头 `MaxQ (MB)` → `MaxQ (MiB)`（bytes/2²⁰；C 8,301,290 B = 7.92 MiB，D 87,382 B = 0.08 MiB）；
3. 生成器 `scripts/generate_paper_tables.py` 同步修正并新增守护测试（宏/微平均交叉验证 + 单位守卫，见 `tests/test_paper_tables.py::check_table1_caption_and_units`）；
4. 清除交付文档中的注入水印标记；MANIFEST 改为 shasum 严格兼容格式（`shasum -a 256 -c` 零 warning）。

## 交付包内容与来源映射

| 包内路径 | 仓内来源（`a24b909` 工作树，产物目录 gitignored、本地保存） |
|---|---|
| `data/summary.csv` | `data/processed/main_formal_S01_S12/summary.csv` |
| `data/paired_comparisons.csv` | `data/processed/main_formal_S01_S12/paired_comparisons.csv` |
| `data/non_inferiority.json` | `data/processed/main_formal_S01_S12/non_inferiority.json` |
| `data/analysis_manifest.json` | `data/processed/main_formal_S01_S12/analysis_manifest.json` |
| `tables/table1_method_overview.csv/.tex` | `…/paper_tables/table1_method_overview.*`（文档修订版：caption 口径 + MiB 单位；数值与 `a24b909` 逐字节一致） |
| `tables/table2_primary_contrasts.csv/.tex` | `…/paper_tables/table2_primary_contrasts.*`（正文版，25 项 F 相关对比） |
| `tables/tableS1_full_contrasts.csv/.tex` | `…/paper_tables/appendix_full_contrasts.*`（附录版，75 项全家族） |
| `figures/fig1_capacity_interaction.png` | `…/paper_figures/fig1_capacity_interaction.png` |
| `figures/fig2_e2e_by_capacity.png` | `…/paper_figures/fig2_e2e_capacity_facets.png`（重命名，字节不变） |
| `action_consistency/ef_action_consistency_results.json` | 由 staging 输入 `data/processed/analysis_input_S01_S12` 于 2026-09-04 重新聚合生成 |
| `action_consistency/ef_action_consistency_terminal_output.txt` | `scripts/supplementary/ef_action_consistency.py`（`a24b909` 版）终端输出 |
| `ANALYSIS_CORRECTION_REV1_REV2.md` | `audits/ANALYSIS_CORRECTION.md` 副本（REV1+REV2 修正全记录） |
| `NUMBER_PROVENANCE.md` | 本包撰写：论文数字 → 文件 → 行号/字段登记表 |
| `STATISTICS_FACTS.md` | 本包撰写：统计方法事实表（margin/效应/CI/检验方向/Holm 范围/bootstrap 次数与种子） |
| `PROVENANCE.md` | 本包撰写：锁定基线、来源映射、复现命令、完整性声明与写作红线（本文件） |
| `MANIFEST_SHA256.txt` | 本包全部 18 文件 SHA-256 清单（MANIFEST 自身不自哈希；标准 shasum 格式，`shasum -a 256 -c` 零 warning） |

## 生成命令（在文档修订 commit 检出下可复现；统计部分与 `a24b909` 完全相同）

```
.venv/bin/python3 -m netshield.analyze --raw-root data/processed/analysis_input_S01_S12 --output data/processed/main_formal_S01_S12
.venv/bin/python3 scripts/generate_paper_tables.py
.venv/bin/python3 scripts/generate_paper_figures.py
.venv/bin/python3 scripts/supplementary/ef_action_consistency.py
.venv/bin/python3 -m unittest discover -s tests -p 'test_*.py'   # 62/62 OK
```

输入快照：`data/processed/analysis_input_S01_S12`
（`scripts/build_analysis_staging.py` 6 道门禁构建；
`SHA256_MANIFEST.txt` = `4b065bd10e382b1a73188b562de587f018f4e8cb19e60de14db7ca77feb6beff`；
61,560 probe + 61,560 core 行）。

## 数据完整性声明

- 本包所有数字均由 `a24b909` 代码在上述输入上确定性生成（统计数值与 `v0.4.7-analysis-rev2-session-level` 零变化，仅有文档/单位标注修正）；
- bootstrap 与置换均为固定种子（分析 CI：10,000 次、seed 20260828；图件 CI：10,000 次、seed 20260904）；
- 原始数据（`data/raw/main/S01–S12`）未被修改；REV1 旧输出归档于
  `data/processed/main_formal_S01_S12/superseded/rev1_36cell_pseudorep/`，不包含在本包中；
- 排除数据：pilot S00、TIE00、HORIZON00、MG00、BASE00（`paper_eligible=false`）；
- 本包不含旧稿文本、旧图、旧表或任何 REV1/pilot 数字。

## 论文写作红线（来自统计事实表 §6，供写作时自查）

1. 推断单位是 session（n=12），36 cell 只作描述；
2. C 的 E2E 仅对 D、F 显著（Holm 0.0146 / 0.0205），不得写成"显著高于所有方法"；
3. F 的 deadline-violation 率 1.03e-4（1/9,720），不得写成"零违反"；
4. D 的 measured Deliv/Gen=1.004 必须与全 95 窗 0.998 同时报告；
5. E/F 动作 9,720/9,720 一致 = "shield 未改变可行决策"，不是"F 优于 E"；
6. 非劣效结论必须同时报告：margin -0.02、效应 0.000、CI [0, 0]、n=12、exact。
