# Formal campaign RC1 audit snapshot

This directory contains a compact, path-free view of the completed NetShield
formal campaign. It is designed for repository integrity checks and reviewer
orientation. It does not contain raw logs, models, packet captures, host
identities, or the full campaign archive.

## Identity and state

| Item | Value |
|---|---|
| Protocol ID | `NSF12_20260906_RC1` |
| Protocol ZIP SHA-256 | `88d70b1ae62b294c522472f408f4c802a745c5a70e60ca387bee25c63f25379a` |
| Accepted design | 12 sessions × 18 arms = 216 arms |
| Accepted validator results | 216/216 `PASS` |
| Invalid attempts | 3, retained and excluded |
| Final archive SHA-256 | `846643a85ace5d840d9c0d7a41245c760989d1886ce0d8c62ca4873368564acf` |
| Collection state | `FORMAL_CAMPAIGN_EXECUTION_COMPLETE_PENDING_INDEPENDENT_REVIEW` |
| Submission | `HOLD` |

## Files

- [`results/campaign_status.json`](results/campaign_status.json) records the
  current gate state.
- [`results/activation_record.json`](results/activation_record.json) records the
  path-free author approval, frozen-tool identities, fixture evidence hashes,
  and second physical-disk backup gate.
- [`results/ATTEMPT_INDEX.json`](results/ATTEMPT_INDEX.json) is the authoritative
  accepted/invalid attempt index.
- [`results/FULL_MATRIX_WITH_STATUS.json`](results/FULL_MATRIX_WITH_STATUS.json)
  records all 216 planned rows and their final status.
- [`results/validator_summary.csv`](results/validator_summary.csv) has one row
  per accepted arm, with no duplicated restore copies.
- [`results/session_packages.csv`](results/session_packages.csv) records package
  and restoration receipts for all 12 sessions.
- [`results/endpoint_summary.csv`](results/endpoint_summary.csv) contains 144
  descriptive rows: 8 event-ledger endpoints × 3 capacities × 6 methods.
- [`results/contrast_summary.csv`](results/contrast_summary.csv) contains the 48
  prespecified descriptive F−E and F−D summaries.
- [`results/artifact_identity.json`](results/artifact_identity.json) binds the
  primary archive, independent backup, and protocol identities.
- [`METRIC_SCHEMA.md`](METRIC_SCHEMA.md) defines endpoint denominators, timing
  domains, censoring, and byte scopes.
- [`audit/STRUCTURAL_AUDIT.md`](audit/STRUCTURAL_AUDIT.md) explains what the local
  audit establishes and what remains open.
- [`MANIFEST_SHA256.txt`](MANIFEST_SHA256.txt) covers every committed file in
  this directory except the manifest itself.

## Interpretation boundary

The authoritative primary metrics are event-ledger endpoints. In particular,
`core_return_coverage` and `on_time_correct_core_coverage` use all generated
measured-origin events in their denominator. A zero for a local-only method at a
core endpoint means that method did not request core execution; it must not be
misread as zero local classification quality. Conditional endpoints can be null
when no event required that endpoint.

The aggregate contrasts are descriptive paired-session summaries. They are not
confirmatory tests. Non-inferiority is explicitly `not_evaluated`, and the old
`timely_f1` alias is retired.

`FULL_MATRIX_WITH_STATUS.json` retains the frozen protocol field
`protocol_row_status = PLANNED_NOT_AUTHORIZED` as provenance of the pre-approval
matrix. The later activation is recorded separately in
`activation_record.json`; each executed row uses `status = VALIDATED_PASS` and
binds its accepted run ID. The two fields describe different points in time.

## Invalid attempts

- `F12_S03/a01`: the primary SSD became unavailable.
- `F12_S04/a01`: the P3 power/throttling gate failed.
- `F12_S07/a01`: P2 lost `wlan0`, and raw-data collection timed out.

Each affected session was rerun as one complete `a02` block. No partial success
from an invalid attempt is included in the accepted 216-arm set.

## Reproduction boundary

This snapshot can verify repository structure and reported aggregate identities.
Rebuilding arm metrics from raw event ledgers requires the separately retained
full archive whose identity is recorded above. Access to that archive is a
controlled reviewer workflow.
