# NetShield ToN V1.3 Final Validation Report

Verdict: **PASS**

No scientific conflict requiring `STOP_AND_REPORT` was found.

## Frozen input and evidence gates

- Methodology-repair ZIP SHA-256: `cc9dcdd708db60ed3ab40f74d79d70d869e23795cbcf1304f4319a98a30fa66f` — PASS.
- Task A rows: 432/432 PASS; shared-cap violations: 0.
- Task B rows: 240/240 PASS; shared-cap violations: 0.
- Task C rows: 648/648 PASS.
- Task D rows: 20/20 PASS; analytical/simulation mismatches: 0; shared-cap violations: 0.
- Formal raw reconstruction: 216/216 accepted arms, 58,320 measured events, 0 raw-to-metric mismatch, and 0 violations across 63,720 shared-service rounds — PASS.
- Raw-audit verdict remains `PASS_WITH_ISSUES`; the S03-a01 and S07 archival gaps remain disclosed and are not converted into accepted evidence.

## Numerical gates

- Frozen `v=1` identity: 36 cells x 4 checks, 0 failures — PASS.
- Mid I-QPG fraction is 1/2 through `v=30000` and 0.622222... at `v=100000` — PASS.
- High full fraction is 1 for every tested `v` — PASS.
- Desynchronized independent mid core fraction is 2/3; simulated on-time range is 0.5000--0.5056 with mean 0.5028 — PASS.
- Coordinated mid core fraction is 1/3 — PASS.
- Aggregate release-lateness p50 values are P1 1972.34 ms, P2 763.90 ms, and P3 83.56 ms — PASS.
- The recurring P1/P2/P3 low-level OS/network cause remains `UNKNOWN` — PASS.
- Every headline number has a PASS row in `MANUSCRIPT_NUMBER_PROVENANCE_V1_3.csv` — PASS.

## Semantic and reference gates

- Forbidden superseded claim scan: 0 affirmative violations — PASS.
- Tasks A/B/D are labelled offline replay, software sensitivity, and discrete-event conformance — PASS.
- Task C alone is identified as reconstruction from accepted hardware timestamps — PASS.
- The 1-s quantity is labelled a post-release service SLO — PASS.
- No centralized-universally-superior, shield-superior-to-C-QPG, classifier-superiority, or physical-32-probe claim is made — PASS.
- Desynchronization's effect on the RQ2 interpretation and the `n=3` granularity limitation are disclosed — PASS.
- Citation keys: 17/17 resolved; unused entries: 0; references independently checked: 17/17 — PASS.

## Build and artifact gates

- Main PDF: 12 pages; supplementary PDF: 24 pages — PASS.
- Undefined citations/references: 0 — PASS.
- Missing referenced figures/tables: 0 — PASS.
- Fatal LaTeX errors: 0 — PASS.
- Overfull boxes: 0 — PASS.
- Rendered-page visual inspection: 36/36 pages — PASS.
- Preliminary clean-unzip validation: PASS.
- Preliminary all-file SHA-256 verification: 63/63 PASS.
- Final clean-unzip validation: PASS.
- Final all-file SHA-256 and machine-validation rerun: PASS.

The validated package is a submission candidate. It does not change the historical raw-audit disclosure or independently grant submission clearance beyond the stated evidence boundaries.
