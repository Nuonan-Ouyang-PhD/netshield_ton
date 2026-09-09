# NetShield ToN V1.3 submission candidate

This directory is the path-free private-review snapshot of the machine-validated
V1.3 manuscript candidate created on 9 September 2026.

## Contents

- `netshield_ton_manuscript_v1_3.tex` and `.pdf`: 12-page IEEE journal manuscript.
- `netshield_ton_supplementary_v1_3.tex` and `.pdf`: 24-page supplementary material.
- `figures/`: seven vector figures generated from frozen CSV/JSON results.
- `tables/`: complete Task A--D and timing tables.
- `evidence/`: only path-free formal summaries and methodology-repair results
  needed to audit the displayed numbers.
- `audit/`: number provenance, semantic-claim audit, and reference audit.
- `BUILD_REPORT.md` and `VALIDATION_REPORT_V1_3.md`: frozen build and final checks.
- `SHA256SUMS.txt`: integrity manifest for this directory.

## Evidence boundary

The formal campaign remains the 12-session, 216-arm, three-Raspberry-Pi RC1
campaign. Tasks A and D are offline replay/discrete-event conformance, Task B is
a software sensitivity, and only Task C reconstructs timing from accepted formal
hardware timestamps. No new Raspberry Pi experiment was run for V1.3.

The raw archive, raw event ledgers, packet-level material, model artifacts, machine
identities, SSH targets, and local paths remain outside Git. The canonical local
submission ZIP is also excluded by repository policy.

The full-raw reconstruction verdict remains `PASS_WITH_ISSUES` because two
historical invalid-attempt artifacts are unavailable. This does not change the
216/216 accepted-arm reconstruction, but it remains an explicit disclosure.

## Verify

From the repository root:

```bash
python3 scripts/verify_repository.py
python3 scripts/verify_methodology_repair.py
python3 scripts/verify_submission_v1_3.py
```

The manuscript and supplementary sources compile from this directory with
Tectonic 0.15.0. Repository visibility and release licensing remain separate
author decisions.
