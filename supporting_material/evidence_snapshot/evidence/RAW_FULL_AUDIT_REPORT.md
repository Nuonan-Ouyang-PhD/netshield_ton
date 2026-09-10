# ToN / NetShield V1.2 Full-Raw Independent Audit

**Verdict: PASS_WITH_ISSUES**

This is a read-only raw-to-metric rebuild of `NSF12_20260906_RC1`. It does not grant submission clearance, and it did not modify the paper or GitHub.

## Identity and accepted set

- Raw ZIP: `d19ae2a5f5697d0d662848c966b8743fa2ba945a24c0247e3a4c526f5bcda87b` (455169143 bytes); CRC PASS.
- Extracted inventory: 41123 files, 7499750382 bytes.
- Inner session ZIP receipts/CRC: 12/12 PASS.
- Accepted set: 12/12 sessions and 216/216 arms; exact protocol mapping: True.
- Accepted attempts: F12_S01 a01, F12_S02 a01, F12_S03 a02, F12_S04 a02, F12_S05 a01, F12_S06 a01, F12_S07 a02, F12_S08 a01, F12_S09 a01, F12_S10 a01, F12_S11 a01, F12_S12 a01.

## Raw rebuild

- Frozen R2 validator: 216/216 PASS.
- Delivered `VALIDATOR.json` semantic matches: 216/216.
- Delivered per-probe event metric report semantic matches: 216/216 arms (all three reports per arm).
- Measured event occurrences rebuilt: 58320; globally unique event keys: 61560; collisions: 0.
- Payload bytes and deterministic payload SHA/segment streams were independently reconstructed; conservation failures: 0.
- Raw-to-delivered mismatch rows: 0.

## Shared service

- Coordination rounds checked: 63720 (= 216 arms x 295 rounds).
- Violations of device grant<=demand, aggregate grant<=cap, payload<=grant, drain-phase service, or probe/core payload agreement: 0.

## E/F safety and capacity interventions

The checker reconstructed every candidate set from raw telemetry, the frozen action catalogue, queue state, and capacity, then replayed the frozen selection/degradation rules.

| Method | Capacity | Measured device-events | Shield safety interventions | Capacity-admission interventions |
|---|---:|---:|---:|---:|
| E | low | 3240 | 0 | 3240 |
| E | mid | 3240 | 0 | 2160 |
| E | high | 3240 | 0 | 0 |
| F | low | 3240 | 3240 | 0 |
| F | mid | 3240 | 0 | 2160 |
| F | high | 3240 | 0 | 0 |

- F post-shield candidate != admitted/final action: **2160** measured events.
- F unshielded base candidate != shield-safe candidate: **3240** measured events.
- E/F final action mix is identical in all 36 session-capacity pairs: True.
- Interpretation: low-tier equality arises through different paths (E capacity degradation versus F safety filtering); mid-tier equality arises through the same shared-cap admission degradation. These counts show interventions, not an observed performance improvement by the shield.

## Gates and exclusions

- Accepted pre-arm/attempt gate failures: 0.
- S03 a01, S04 a01, and S07 a01 are excluded wholesale as infrastructure-invalid attempts, never as performance-based exclusions.
- S04 and S07 have direct raw failure records in the supplied package. S03's storage reason is carried only by `ATTEMPT_INDEX.json` in this package.

## Frozen aggregate

- `AGGREGATE_EVENT_METRICS.json`: semantic-identical=True, byte-identical=True.
- `PUBLIC_NUMERIC_CANDIDATE.json`: semantic-identical=True, byte-identical=True.
- `FULL_MATRIX_WITH_STATUS.json`: semantic-identical=True, byte-identical=True.

## Independently confirmed special findings

- low C core completion mean=1.0; conditional on-time mean=0.0.
- low D conditional H_FULL/core on-time mean=0.0.
- Mid D/E/F common on-time-correct means: D=0.0, E=0.2938271604938272, F=0.2978395061728395.
- High C/D/E/F common on-time-correct means: C=0.9635802469135802, D=0.9592592592592593, E=0.9697530864197531, F=0.9651234567901235.
- Release-lateness and application-payload totals are recorded in `SPECIAL_FINDINGS.json` and the CSV ledgers.

## Issues

- S03 a01 storage-failure reason is present in ATTEMPT_INDEX but no direct failure/incident record is included in the raw session ZIP
- S07 pre-hardware launcher-abort records are not present in the supplied raw session ZIP

## Fatal findings

- None.

## Boundary

Audit complete. Submission remains HOLD pending separate review; no manuscript or GitHub update was performed.
