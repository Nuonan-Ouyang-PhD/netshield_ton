# Validation report — selective integration

Status: PASS for the current integration checks.

| Check class | Outcome |
|---|---|
| Preserved candidate scientific/build gates | 84/84 PASS |
| Integration-specific source/hash/layout gates | 21/21 PASS |
| Analytical regression groups | 13/13 PASS; 6555 cases |
| Frozen evidence/table/protocol/reference files | 54/54 SHA-256 identical to the FINAL baseline |
| Main / supplementary pages | 13 / 28 |
| Undefined citations/references | 0 / 0 |
| Overfull hbox/vbox | 0 / 0 |

## Unchanged empirical scope

Primary: 216 accepted arms, 58320 measured occurrences, 63720 reconstructed service rounds.
CRFA: 36 accepted arms, 9720 measured occurrences, 10620 service rounds; 55 indexed attempts,
19 infrastructure exclusions, and timing outcomes not used for acceptance.
Combined: 252 accepted arms, 68040 occurrences, 74340 service rounds. Zero cap violations
remain the recorded finding of the supplied audits; no hardware was run during this edit.

CRFA post-release timely-full/generated remains 0.3055556 / 0.6327160 / 0.9660494.
The mid paired contrast remains +0.3388889 with descriptive 95% session-bootstrap
[0.3305556, 0.3478395]. Selected-full eventual return remains 1.0 at all capacities.
These statistics were not re-estimated in this pass.

The primary raw-audit PASS_WITH_ISSUES and its two disclosed archival gaps remain unchanged.
Historical gate details are preserved at audit_history/BASELINE_VALIDATION_REPORT.md.

## Boundaries on new content

The probability and heterogeneous-payload results are analytical planning consequences,
not new measurement campaigns. The source explicitly requires the summary baseline,
independent within-round requests for the binomial model, and equal values for the
increasing-cost count rule. No post-hoc TOST, universal desynchronization advantage,
weighted greedy optimum, or unmeasured absolute-clock timing bound was imported.

## Reproducible checks

Run `bash build/rebuild.sh`. Individual logs: build/candidate_validation.log,
build/integration_validation.log, build/analytical_validation.log.
The frozen-baseline manifest is separate from the full delivery SHA256SUMS.txt.
The delivered files were also tested in a clean extraction (CLEAN_REBUILD_REPORT.md).
