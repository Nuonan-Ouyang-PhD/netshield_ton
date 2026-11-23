# Methodology review and corrections

This is the original methodology-correction record. It describes the evidence
available at that stage, before the subsequent hardware and held-out content
studies. For those later results, see the
[physical comparisons](supporting_material/experiment_extension/physical_extension/README.md)
and the separate
[CICIoMT2024 content and transport study](supporting_material/experiment_extension/content_measurement/README.md).

The review used repository baseline
`fe09ee0eca28dc666dd9c729ac266b8426c055b9`, checked the ten issues below, and
compared the uploaded `NetShield_ToN_Integrated_20_09_2026.zip` with that
version. Work completed at this stage included code corrections, reconstruction
from public parameters, shared-service model counterexamples, independent
ledger checks, and manuscript revisions. It did not include hardware reruns,
measured Wi-Fi delay calibration, or a detection-value ablation.

## Findings

Several defects changed the software results. In particular, the waterfill
defect could leave at most 2 B unserved per round, but its effect could not be
dismissed on that basis. Queue state enters the next selector decision; a small
residual can cross an action threshold. Reconstruction from the public
parameters demonstrated this effect.

The revision also separated three kinds of evidence: software upload
completion, hardware result return, and independent checks of underlying
records. It retained the CRFA hardware findings, corrected the software
endpoint names and comparisons, and identified the new models as software
evaluations.

## Response to the ten issues

| Issue | Finding | Correction and remaining scope at this stage |
|---|---|---|
| 1. Tick simulation omits computation, Wi-Fi, Core processing and return | Confirmed. The original function recorded completion when the FIFO payload reached zero. | Renamed the A/B endpoint to upload completion and added a separate model with explicit processing stages. Its delays are disclosed assumptions, not measured Wi-Fi values. Hardware scoring retained creation-to-result-return timing on the originating probe clock. |
| 2. waterfill leaves residual bytes unserved | Confirmed. The old implementation stopped early when `remaining < active_count`. | Allocated the remaining integer bytes and rotated residual priority by round/tick. Retained the original function and reported the corrected sensitivity separately. |
| 3. Task A's 12 seeds are pseudoreplicates | Confirmed. The synchronized independent controller has no decision path that uses the seed. | The corrected Task A reports 36 configurations. All 432 historical rows were retained; each configuration was shown to have only one simulation outcome. No confidence interval was based on the repeated labels. |
| 4. Simulated zero cap violations | Confirmed. This count is an implementation invariant of the capped allocator. | Stopped treating it as an independent measurement. Added a ledger checker that does not call the allocator and instead sums service, checks byte conservation, and reconstructs event timing. |
| 5. Admission ignores backlog | Confirmed. Fitting new traffic within C does not ensure that all queued work clears in that round. | Both joint-admission calls now receive the existing queues. The new-byte budget is `max(0,C-sum(Q))`; backlog that already exceeds C is recorded as infeasible. |
| 6. is_safe assumes exclusive service | Confirmed. A 500 ms estimate for one Full request at the middle budget does not ensure that three simultaneous requests finish on time. | Renamed it to isolated latency precheck and distinguished it from backlog admission and deadline reservation in the complete model. |
| 7. A/B timely predicates differ | Their time resolutions and service models differ. They have a limited equivalence case for synchronized round-start release and a 1 s upload-only deadline. | Used an inclusive elapsed-upload predicate while retaining A's round-end upper bound and B's tick-end upper bound. Neither endpoint is a Core result-return time. |
| 8. Manuscript and code do not align clearly | Confirmed. Problems included endpoint names, pseudoreplicates, historical outputs paired with new source, and obsolete build instructions. | Added a source/result map, retained the legacy driver, updated build and reproduction instructions, and explained the relationship between the historical allocator and corrected model. |
| 9. Shared-link safety needs further evaluation | Added public software evaluation. | Ran 30 deterministic configurations × 4 policies = 120 model runs, retaining request and service records. Physical shared-link safety still required hardware evaluation with measured stage delays and an allowance for model error. |
| 10. Detection value of alert/summary/full is unestablished | Confirmed. Fixed utilities and saturated correctness on the frozen replay cannot identify information gain. | Removed implications that evidence size establishes detection benefit and added an unexecuted paired-content protocol. No new accuracy, F1 or detection-delay results were produced at this stage. |

## Software effects of the waterfill correction

Using the ten public payload sizes, six-decimal utility values and retained
original function, we reconstructed all 36 `(v,capacity)` configurations.
All 36/36 matched the historical CSVs in action counts, core-request fraction,
payload, per-round queue trajectories and maximum queue. This reconstruction
used public parameters; it did not load the private full-precision action
file, runtime, models or raw feature data.

With work-conserving service and rotating residual allocation, 24/36
per-device queue trajectories changed and 5/36 action combinations changed.
All action changes occurred at low capacity, for `v=1,3,10,30,100`.

| v at low capacity | Historical Full requests/270 | Corrected Full requests/270 | Historical full-state period | Corrected full-state period |
|---:|---:|---:|---:|---:|
| 1 | 66 | 90 | 4 | 3 |
| 3 | 66 | 90 | 4 | 3 |
| 10 | 81 | 90 | 10 | 3 |
| 30 | 87 | 90 | 28 | 3 |
| 100 | 90 | 90 | Not detected | 3 |

At `v=100`, the Full count was unchanged, but summary actions and payload
changed. At `v=1,3`, payload increased from 9,191,424 B to 11,796,480 B.
The timely Full-upload count remained zero in these configurations.
Action combinations at the middle and high budgets were unchanged; the
middle-budget Full/none action cycle still had period two. Some corrected
middle-budget records had a full-state period of 6 because residual-byte
priority rotated among three devices. This did not remove the period-two
action cycle.

The CSVs and complete parameters are in
[PUBLIC_SELECTOR_COMPARISON.csv](supporting_material/methodology_validation/PUBLIC_SELECTOR_COMPARISON.csv),
[PUBLIC_SELECTOR_AUDIT.json](supporting_material/methodology_validation/PUBLIC_SELECTOR_AUDIT.json)
and [TASK_A_REPLICATION_AUDIT.csv](supporting_material/methodology_validation/TASK_A_REPLICATION_AUDIT.csv).

## Shared-service counterexamples

The added model uses 1 ms ticks, a constant shared application-byte rate,
per-device FIFO queues, integer max-min service across devices, and one FIFO
Core. Unused tick capacity expires. The return path adds only the stated
delay; it has no separate contending return-byte queue. The model evaluates
one batch of new requests. Its results do not establish steady-state
throughput, long-run fairness, or an SLO over a stochastic wireless link.

All cases below use `n=3`, `B=131072 B`, `C=262144 B/s`, and a 1000 ms
deadline. The assumed stage delays are detector 40 ms, preprocessing 20 ms,
uplink extra 15 ms, Core 35 ms, and return 10 ms. All are sensitivity inputs.

| Condition | Policy | New Full admissions | Latest upload, ms | Latest return, ms | Timely new results |
|---|---|---:|---:|---:|---:|
| No backlog; extra delay = 0 | Isolated-link precheck | 3 | 1500 | 1500 | 0 |
| No backlog; extra delay = 0 | New-byte check only | 2 | 1000 | 1000 | 2 |
| Existing backlog=B; extra delay = 0 | New-byte check only | 2 | 1500 | 1500 | 0 |
| Existing backlog=B; extra delay = 0 | Backlog-aware | 1 | 1000 | 1000 | 1 |
| No backlog; assumed stage delays | New-byte check only | 2 | 1060 | 1155 | 0 |
| No backlog; assumed stage delays | Complete-model reservation | 1 | 560 | 620 | 1 |
| Existing backlog=B; assumed stage delays | Backlog-aware | 1 | 1000 | 1060 | 0 |
| Existing backlog=B; assumed stage delays | Complete-model reservation | 0 | — | — | 0 |

For each candidate, model reservation predicts completion again for every
already selected task. Across 30 configurations, it admitted 93 new requests;
all 93 returned within the deadline in that same model. This pooled count is
a model-conformance diagnostic. Pooling heterogeneous configurations does not
establish a performance advantage. Admission opportunities and zero-admission
configurations were both reported, so rejecting all requests could not be
mistaken for better service. A regression case also showed that results
returning at 1000 ms in the nominal model all miss the deadline if the actual
return stage adds 1 ms.

The complete model and event-level results are in
[contention_validation](supporting_material/contention_validation/README.md).

## Independent ledger checks and retained hardware findings

The independent checker does not call waterfill or trust stored zero-cap or
timely flags. It reconstructs per-round service totals, per-event byte
conservation, the upload endpoint from final service, single-Core ordering,
and return deadlines. For CRFA, it also checks every measured
run/window/device combination. This catches missing H-NONE rows that would
shrink the generated-event denominator and duplicate events recorded under
different keys.

The new software records contained 1,112 new requests and 556 requests already
queued: 1,668 event rows, 1,637 event/round service rows, and 167 used service
rounds. Independent reconstruction passed. The public CRFA exports also
passed reconstruction across 36 runs, 10,620 service rounds and 9,720 measured
occurrences.

| CRFA capacity | Generated | Selected Full | Returned Full | Timely Full-Core | Nominal-anchor timely Full-Core |
|---|---:|---:|---:|---:|---:|
| Low | 3240 | 1080 | 1080 | 990 | 360 |
| Mid | 3240 | 2160 | 2160 | 2050 | 720 |
| High | 3240 | 3240 | 3240 | 3130 | 1079 |

These public records retain support for the original outputs of
0.3056/0.6327/0.9660 per generated event and frontier attainment of
91.7%/94.9%/96.6%. Every queue-before value in the CRFA service table was zero.
CRFA selected 1/2/3 Full requests at the low/middle/high budgets, and C equalled
the corresponding total Full payload. This particular controller therefore
did not trigger the integer equal-share remainder defect. Other controllers'
results in the primary campaign remain observations of their frozen
implementations; the corrected implementations cannot be assumed to produce
the same physical measurements.

This review checked the **public per-probe service and event exports**. It
did not reopen the primary campaign's private raw logs for 63,720 rounds,
remeasure the physical link or NIC, or recompute the paired bootstrap. The
historical raw-audit verdict, `PASS_WITH_ISSUES`, remained in force.

## Issue 10: evidence missing at that stage

At this stage, the evidence supported delivery feasibility and measured
Full-Core return deadlines under the specified workload. It did not quantify
the detection gain from different evidence levels.
The added [DETECTION_VALUE_PROTOCOL.md](supporting_material/contention_validation/DETECTION_VALUE_PROTOCOL.md)
was marked `NOT_EXECUTED`. It required three real representations of the same
held-out episodes, declared information fields and padding, capture/episode
splits and duplicate checks, frozen models and thresholds, and retention of
missing results in the generated-event denominator. Its design measured
information value before shared-service value. The required representation
generators, usable raw content and authorized models had not been supplied in
the public checkout at that stage.

Code and wording corrections alone could not establish that Full detects
intrusions better than summary or alert. Such a conclusion required paired
downstream results from an executed protocol. The paper could also retain its
contribution within the already quantified network evidence-delivery problem.

## Verification recorded at that stage

```bash
python3 scripts/verify_methodology_revision.py
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s supporting_material/contention_validation -p 'test*.py' -v
```

18 allocator/admission/endpoint/independent-checker tests and 9
shared-model tests passed, including 13,750 integer-allocation cases. Mutation
tests rejected excess service despite a zero violation flag, missing or
duplicate service, missing H-NONE events, incorrect return times, and forged
timely flags.

The 120 frozen files, 14 existing formal blocks, 21 labelled equations and
abstract were unchanged. The build and validation record is in
[METHODOLOGY_VALIDATION_REPORT.md](submission/audit/METHODOLOGY_VALIDATION_REPORT.md).
The source-to-evidence map is in
[CODE_EVIDENCE_ALIGNMENT.md](submission/audit/CODE_EVIDENCE_ALIGNMENT.md).
