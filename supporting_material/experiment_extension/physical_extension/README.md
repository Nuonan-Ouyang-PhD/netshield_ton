# Three-probe hardware extension

The original 216-arm primary campaign and 36-arm CRFA campaign retain their
own equipment identities and statistical scope. The table below lists only
the new campaigns. QUAL denotes the engineering qualification checks for the
two initial physical backlog conditions.

| Campaign | Planned arms | Registered attempts | Reconstructed arms |
|---|---:|---:|---:|
| [TON_EXT_ALLOC_4B8_FORMAL_20261123_01](TON_EXT_ALLOC_4B8_FORMAL_20261123_01/arms.json) | 8 | 8 | 8 |
| [TON_EXT_ALLOC_4B8_PILOT_20261122_01](TON_EXT_ALLOC_4B8_PILOT_20261122_01/arms.json) | 2 | 2 | 2 |
| [TON_EXT_STAGE_4B8_CAL_20261123_01](TON_EXT_STAGE_4B8_CAL_20261123_01/arms.json) | 16 | 5 | 4 |
| [TON_EXT_STAGE_4B8_CAL_20261123_02](TON_EXT_STAGE_4B8_CAL_20261123_02/arms.json) | 16 | 16 | 16 |
| [TON_EXT_STAGE_4B8_FORMAL_20261123_01](TON_EXT_STAGE_4B8_FORMAL_20261123_01/arms.json) | 36 | 36 | 36 |
| [TON_EXT_STAGE_4B8_PILOT_20261123_01](TON_EXT_STAGE_4B8_PILOT_20261123_01/arms.json) | 6 | 6 | 6 |
| [TON_EXT_STAGE_4B8_QUAL_20261123_01](TON_EXT_STAGE_4B8_QUAL_20261123_01/arms.json) | 2 | 2 | 2 |

Each directory contains source hashes, actions and queues for each role,
same-clock time differences, and paired contrasts. With Python 3.11 or later,
run `verify_results.py` with a campaign export directory as its argument to
recompute byte conservation, cycles and timely-return rates under both time
anchors.

[Content provenance review](CONTENT_INPUT_REVIEW.md) · [Storage amendment](storage.json) · [Acquisition code](acquisition/)

## Measured results

The formal allocator comparison contains four pairs. The original and
corrected versions each generated 1,080 events and admitted 264 and 360 Full
requests, respectively. Every Full result eventually returned; neither
version returned a Full result within one second. Unused serviceable bytes
per arm were 144 and 0, respectively.

The first shared-stage calibration campaign completed four arms. Its fifth
arm was aborted after a P2 management-link health check timed out. All five
attempts are retained separately. Each of the 16 conditions in the replacement
campaign contributes one measured first batch to the profile, whose extra
margin is zero. The independent pilot and formal campaigns have separate
registrations.

| Formal policy and initial backlog | First-batch events | Admitted H_FULL | First-batch timely Full results | Events over 90 rounds | Timely Full results over 90 rounds |
|---|---:|---:|---:|---:|---:|
| B0_P1_P2_P3_backlog_aware_bytes | 18 | 12 | 8 | 1620 | 1044 |
| B0_P1_P2_P3_causal_shared_stage | 18 | 0 | 0 | 1620 | 0 |
| B0_P1_P2_P3_isolated_precheck_new_bytes | 18 | 12 | 8 | 1620 | 1045 |
| B131072_P1_P2_P3_backlog_aware_bytes | 18 | 6 | 6 | 1620 | 1034 |
| B131072_P1_P2_P3_causal_shared_stage | 18 | 0 | 0 | 1620 | 0 |
| B131072_P1_P2_P3_isolated_precheck_new_bytes | 18 | 12 | 0 | 1620 | 0 |

When these hardware campaigns ended, the original frozen inputs did not
provide a qualified cohort for independent content-value or
communication-constrained timely-correctness tests. Their parent captures,
boundaries and independent acquisition groups remained unverified. The
original 896-row diagnostic was not treated as an independent test cohort.
The subsequent [held-out content study](../content_measurement/README.md)
reports the separate CICIoMT2024 experiment with verified capture provenance.

## Recompute the calibration parameters

Run `python3 -B verify_calibration.py` in this directory. The published
[16 sets of stage timings](calibration_relative.jsonl) shift the time origin
separately for the Core and each probe in every arm, and replace private clock
identifiers with roles. All nanosecond differences on the same clock are
preserved. The script uses the acquisition-time calculation function to
recompute all 16 parameter sets and compare them, field by field, with the
[deployed profile](physical_profile.json).
