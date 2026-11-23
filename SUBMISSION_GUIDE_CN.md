# NetShield ToN 投稿文件指引

本次最终整理以 `75d529c9f52612c050832da269a7caf4f7b73539` 的实测结果为基础。
论文将积压感知 admission 的物理结果放入 Results；最终文件以本包的校验清单和
GitHub PR #3 对应的最终提交为准。

## 提交时使用的文件

| 用途 | 本包中的文件 |
|---|---|
| 主稿 | `submission/netshield_manuscript.pdf` |
| 补充材料 | `submission/netshield_supplementary.pdf` |
| Cover letter 文本 | `submission/cover_letter.md`；可复制正文到投稿系统的对应文本框 |
| LaTeX 源码 | `submission/netshield_manuscript.tex`、`submission/netshield_supplementary.tex` 及同目录的 `figures/`、`tables/` |
| Overleaf 独立导入包 | GitHub `review_package/NetShield_ToN_Overleaf.zip`；也随完整交付提供 |
| 公开实验结果与复算 | `supporting_material/experiment_extension/physical_extension/` |
| 构建与核验说明 | `submission/BUILD_INSTRUCTIONS.md`、`submission/audit/SUBMISSION_FINALIZATION.md` |

两份当前 PDF 都位于 `submission/`。`supporting_material/archive/` 和冻结快照中的
旧版本用于溯源，不是本次提交的主稿或补充材料。

## 本轮实证范围

- Allocator：2 臂 pilot 和 4 对正式比较，共 8 个正式物理臂。
- Shared-stage：独立的 16 条件物理校准、6 臂 pilot 和 36 个正式物理臂。
- 两条硬件线共 44 个正式物理臂；计入资格、校准、pilot 及中止尝试，共登记
  75 次尝试，74 臂完成重建。
- 校准策略在所测条件下全部拒绝 Full 请求，是已完成的负结果。
- 独立内容价值研究仍缺合格的父采集身份和边界；本包不包含新的独立检测收益或
  通信约束及时正确率结论。

原 216 臂主活动、36 臂 CRFA 活动与本轮替换设备组分别记账。
完整包包含公开证据、采集/分析代码与核验材料；私有原始记录和第三方数据的
访问范围见 `RIGHTS_AND_ACCESS.md` 与 `REPRODUCIBILITY.md`。

## 修改、构建与文件校验

Overleaf 导入后选择 pdfLaTeX，将 `netshield_manuscript.tex` 设为主文档；
生成补充材料时切换为 `netshield_supplementary.tex`。
本地完整源码的构建入口为 `bash scripts/build_submission.sh`。

完整 ZIP 的 `SHA256SUMS_REVIEW.txt` 核验包内文件；Overleaf 包内有单独的
`SHA256SUMS_OVERLEAF.txt`。任何进一步编辑或重新编译都会产生新的文件摘要，
请相应保留新的构建记录。

GitHub 更新保留在 PR #3 的审阅分支；论文投稿由作者完成，PR 状态不代表期刊投稿状态。
