# Validation report — 15 September 2026 revision

| Check family | Actual result | Scope |
|---|---:|---|
| Maintained candidate validator | 84/84 PASS | Frozen summary metrics, CRFA counts/fairness/cap gates, protocol fields, citations and build checks |
| New revision validator | 40/40 PASS | Baseline hashes, original formulas/statements, abstract, references, figure geometry, current page/layout checks |
| Inherited analytical checker | 13/13 groups; 6,555 cases PASS | Exact arithmetic and small-case enumeration, not new empirical runs or a replacement for general proofs |
| Frozen scientific inputs | 60/60 hashes unchanged | 28 evidence + 22 tables + number provenance + 2 protocols + 7 original figures |
| Prior bibliography preservation | 29/29 entries unchanged | Normalized entry text; reordered by citation sequence |
| Formal statement preservation | 7/7 unchanged | Theorem, corollary and proposition statements |
| Existing labelled equations | 20/20 unchanged | QPG placement changed, expression unchanged |
| Supplement preservation | 28/28 original page rasters identical | Compared at 108 dpi; added page 29 contains index and full trace |

Evidence of execution: `build/candidate_validation.log`,
`build/analytical_validation.log`, `build/analytical_checks.json`,
`build/revision_validation.log`, `build/revision_checks.json`,
`build/supplement_preservation.json`.

The candidate validator's numerical checks are unchanged. Its limited editorial
changes are documented in `build/EDITORIAL_VALIDATOR_CHANGES.diff`. Historical
validators are archived, not rerun under obsolete page/reference expectations.

No hardware experiment, empirical bootstrap or external raw-archive re-audit was
performed. The first 28 supplement pages and the original evidence already existed.
The supplied results-layer provenance and historical raw-audit caveats are preserved.
