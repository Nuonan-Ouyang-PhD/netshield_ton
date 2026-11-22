# Formal campaign and representation review

The starting clean checkout was 5aa0152e03dfa499388562f8bc235530d5111098.
The extension precheck passed 35 fixture tests. The following observations
come from the private RC1 runtime, accepted arm records and archived data.

## Deployed runtime and historical service

All 216 accepted arms record package tree
`be34cdd19441e66a0042b60f9fe75eb0277a8b9a9bb8eeb8f8f87b6b393d7085`
in deployment identities. The archived runtime reproduces that tree hash.
The formal launcher records core and probe process commands per arm.
Core Coordinator.decide selects candidates and uses _allocate_shared_cap;
probe.py builds the admitted event's payload and serves its FIFO.
core.py validates origin metadata and feature identity before calling
detectors.score on full features. The originating probe ledger records receipt.
The deployed allocator stops when integer division gives zero. Its archived
function granted 43,690 bytes to each of three equal 131,072-byte demands at a
131,072-byte budget.

The accepted index selects the reruns of sessions 03, 04 and 07.
Across 63,720 service rounds the sum of min(capacity, demand) minus grants
was 10,848 bytes. Core receipt counters agreed with probe delivery counters
in every paired device window. Queue recurrence residuals, final queue bytes,
receipt cap exceedances, duplicate device windows and duplicate measured
event keys were zero. Of 58,320 measured events, 24,012 required core
execution. All had a return timestamp. Of these, 14,416 returned within
one second of creation on the originating probe clock.

Coverage comprises per-window service records and terminal event ledgers.
These checks do not establish independent packet delivery, per-chunk offset
continuity or the counterfactual effect of correcting the allocator.

## Representation and data eligibility

The historical alert and summary use the same metadata fields: event ID,
device ID and local score, padded to their respective action sizes. In the
131,072-byte full bundle the feature record also carries the label, window
index and feature vector. Deterministic pseudorandom context and trailing
zero fill occupy the remaining space. Core scoring receives only the decoded
features. Payload size alone does not establish extra detection value.

An interface diagnostic invoked the hash-verified heavy model on nine archived
pilot observations and decoded three representations per observation. The
diagnostic encoders emit a predicted bit, a score, or the observation vector.
These encoders are new. The pilot measures interface execution only.

The archived v0.2.1 corpus has 18/6/7 source-file groups in train/validation/test.
Hashing all 39 feature values as big-endian binary64 in source order with
signed zeros normalized and labels excluded found 190,258 of 996,486
validation rows matching training rows and 497,391 of 1,147,055 test rows
matching training or validation. The training split contains 2,998,132 rows.
The released scorer rejects this cross-split overlap. Independent capture
lineage, near-duplicate qualification and binding this corpus to the model's
exact training inputs remain open. No held-out efficacy estimate is reported.

## Physical qualification

The historical launcher configuration reached P1. Both P2 and P3 failed
hostname resolution. Allocator regression is applicable. Physical calibration,
pilot and formal runs require a qualified three-probe deployment.
