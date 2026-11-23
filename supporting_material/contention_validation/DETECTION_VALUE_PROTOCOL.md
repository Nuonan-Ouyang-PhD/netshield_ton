# Evidence-level value protocol — NOT EXECUTED

This file specifies an additional experiment. It contains no new detection
scores, measured Wi-Fi values, hardware-run claims, or approved success
thresholds. Implementing the representations and obtaining authorized
episode-level data and frozen model artifacts are prerequisites.

## Why the current data cannot answer this question

`supporting_material/formal_campaign_audit/METRIC_SCHEMA.md` defines
classification for the final admitted execution and separately records
evidence transfer, local readiness and returned core results. This is useful
for auditing the executed path. It is not a same-occurrence counterfactual
comparison between alert, summary and full evidence at a common downstream
consumer.

The manuscript reports perfect classification on the scored frozen replay,
feature-vector overlap across frozen partitions, and the exclusion of
Recon-PortScan. That saturated replay cannot establish an incremental
accuracy gain from richer evidence. A larger serialized payload also need
not contain more discriminative information if the extra bytes are padding
or repetition. Evidence-level utility must therefore be tested with the
actual decoded information exposed to the consumer.

## Freeze a task before evaluating transport policies

Choose one primary downstream task that all three representations can
meaningfully support, for example attack-episode detection at the core or
cross-probe incident correlation. Specify its labels, prediction unit,
positive class, time horizon and error costs before viewing test outcomes.
Do not silently substitute local detector correctness when remote incident
resolution fails.

For each held-out event or attack episode, construct the actual three
representations from the same underlying observation:

- **Alert:** enumerate available fields, such as probe identity, timestamp,
  label or score. Record what is omitted.
- **Summary:** specify aggregation window, feature names, quantization,
  cardinality and missing-field behavior. Preserve its true serialized size.
- **Full:** specify the raw or feature-level observation actually available
  to the core. Distinguish distinct information bytes from padding, framing
  and repeated feature vectors.

Hash each encoded representation and its encoder version. The consumer
must receive only those fields at that evidence level; fetching omitted
features from a shared dataset would invalidate the comparison.

## Split and freeze data and models

Keep correlated occurrences from the same capture, device/session group or
attack episode together in train, validation or test. Audit exact and near
duplicate features across groups. Report any residual overlap. Select
thresholds and model hyperparameters on validation data, then freeze them
before evaluating the held-out test episodes.

If one consumer architecture can process all levels through explicit masks,
freeze its model and operating threshold for the primary comparison. If
different encoders or architectures are unavoidable, preregister them and
describe the result as a system-level comparison of representation plus
consumer, rather than an isolated effect of byte count. Keep training
budgets and test episodes matched and report compute cost.

## Separate information value from transport value

Run two linked evaluations on the same held-out episodes:

1. **Information-only replay:** provide each representation without network
   loss or delay. Measure the chosen downstream task to identify whether
   richer information changes the outcome at all.
2. **Shared-service replay or hardware run:** deliver each representation
   through the declared controller under the same workload/capacity schedule.
   Retain queueing, local compute, core waiting/inference, and returned-result
   timestamps. Score task output that actually reaches the specified endpoint
   within the deadline; missing outputs remain in the generated denominator.

Randomize method order or use a predeclared balanced crossover for a new
physical study. Preserve all attempted runs and independent infrastructure
exclusions. Do not reinterpret the existing nonconcurrent primary and CRFA
campaigns as randomized comparisons.

## Required outputs

At a minimum, retain an event ledger with:

`episode_id, occurrence_id, split, probe, evidence_level, encoder_hash,
representation_hash, information_bytes, padding_bytes, wire_payload_bytes,
model_hash, threshold_id, ground_truth, prediction, score, generated_time,
local_compute_start, local_compute_end, enqueue_time, upload_complete,
core_start, core_end, result_received, deadline, terminal_state`.

Use one originating-clock domain for elapsed end-to-end metrics, or a
validated clock-alignment procedure with error bounds. Never subtract
unrelated host monotonic clocks. A separate raw service ledger must allow
byte conservation and per-round cap reconstruction.

Report the primary task metric, false-positive/false-negative counts and
all generated/scored/missing counts for each representation. Include
paired per-episode differences, precision/recall at the frozen threshold,
and an uncertainty method whose resampling unit is an independent episode
or capture group. Include timely correct outcomes per generated episode,
elapsed time from the task's declared onset anchor, and payload/compute
cost. Do not call a selection-gap bound an Age-of-Information result.

Only after these measurements exist can the manuscript quantify how
alert, summary and full evidence trade detection or investigation value
against communication and delay. Until then, its established contribution
is evidence-delivery feasibility and measured full-result deadline
attainment under the frozen workload.
