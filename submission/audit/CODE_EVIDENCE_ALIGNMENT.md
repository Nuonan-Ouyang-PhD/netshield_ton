# Code–evidence alignment audit

The supplementary transport counts aggregate the four case receipts in [TRANSPORT_RECHECK.json](../../supporting_material/experiment_extension/TRANSPORT_RECHECK.json). The 1,080-event denominator covers measured generations; the 1,010 segment receipts and 530 returns include all service rounds. These are private loopback checks.

## Audit stages and current interpretation

The two private 26-condition receipts bind the earlier and instrumented runtime trees separately. Four loopback transports exercised the probe-to-Core path with synthetic workload and accelerated pacing. The subsequent replacement-cohort physical extension completed 8 allocator and 36 shared-stage formal arms, in addition to separately registered qualification, calibration and pilot measurements.

The current consolidated status is
[physical extension record](../../supporting_material/experiment_extension/physical_extension/README.md).
The repaired private rerun and retained 896-row reconciliation are complete
within their stated scope. The subsequent source-row trace, executed physical
comparisons and separate CICIoMT2024 held-out content study have separate
evidence boundaries. `HARDWARE_CLOSEOUT_CN.md`, earlier `FOLLOWUP_REVIEW.md`
and the nine-observation stage
below remain historical records; the nine-input construction-based agreement
explanation does not apply to the later Gaussian/Bernoulli consumer's
empirical diagnostic results.

| Current artifact | Completed work | Remaining scope |
|---|---|---|
| [Retained review](../../supporting_material/experiment_extension/retained_review/) | Repaired checker execution receipt and 896-row preservation/pairing/subset reconciliation | Recorded-field scope; no newly acquired hardware or independent efficacy estimate |
| [Source row trace](../../supporting_material/experiment_extension/SOURCE_ROW_TRACE.json) | Reported local matching of 5,141,673 rows to 31 original CSVs; public totals agree with 18/6/7 source groups and previous split denominators | Private rows are not republished; CSV/row coordinates do not identify independent parent acquisitions |
| [Stage candidate](../../supporting_material/experiment_extension/stage_adapter/README.md) | Both executed 26-case private checks, four loopback checks, physical qualification, a complete 16-condition calibration, six pilot arms and 36 formal arms | The calibrated policy admitted no Full requests; overlapping empirical allowances do not establish a useful deadline guarantee |
| [Physical comparisons](../../supporting_material/experiment_extension/physical_extension/README.md) | Four allocator pairs and six shared-stage blocks, with public queue/endpoint exports and block-level analyses | Replacement-cohort scope; allocator timely-Full counts remain zero, while backlog-aware admission improves the stated backlog condition |
| [Capture mapping preparation](../../supporting_material/experiment_extension/source_lineage/README.md) | Executable mapping/evidence/split consistency checks | Actual parent evidence, sufficient independent groups, feature qualification and model fitting remain required |

The main paper reports the completed row trace, and the supplement separates
the initial nine coordinator-path checks plus one direct-function check from
later candidate revisions. The completed physical calibration covers all eight
forced-full subsets crossed with backlog 0/B while retaining three real
requests and H-NONE fallbacks per condition. Each condition contributes one
first measured batch to the deployed empirical profile. The independent pilot
and formal comparison cover six policy/backlog conditions. The earlier
calibration activity retains four completed arms and an aborted fifth attempt;
none supplies the complete replacement profile.

The methodological review below is retained as the historical baseline. A
subsequent supplied archive, `TON_EXT_AUDIT_20261122_avIClI`, adds a report of
local private-runtime inspection, arm-level outputs from a private-record
checker, an exact-feature split-overlap result, and a nine-observation model
interface diagnostic. The new stage and its source hashes are documented in
[`FORMAL_RECORD_INTEGRATION.md`](FORMAL_RECORD_INTEGRATION.md).

The new report supports a more specific account of the deployed allocator
and payload construction, and its 216 arm summaries can be reconciled with
the retained campaign results. The private runtime, model weights, underlying
service/event files, and corpus partitions were not attached to this archive;
their bytes were therefore not independently reopened in this integration.
The distinction between the reported local inspection and the publicly
repeatable summary reconciliation is explicit. The original raw audit's
`PASS_WITH_ISSUES` verdict remains in force. This stage adds no physical
campaign and no held-out evidence-value result.

## Historical baseline and source authority

This audit starts from repository commit
`fe09ee0eca28dc666dd9c729ac266b8426c055b9` and the supplied
`NetShield_ToN_Integrated_20_09_2026.zip`. The canonical manuscript is
`submission/netshield_manuscript.tex`; the supplied ZIP is a comparison input,
not a replacement source tree.

| Input | SHA-256 at the start of this audit |
|---|---|
| Repository main manuscript | `478d6e403406cc5f006be0b6aaebc79cf5b7821722aca6509bb3d995e0a2715d` |
| Uploaded main manuscript | `9cfa72e2a7141b6c80a591095617147b71e83bc04173f0953987e68866476a81` |
| Repository and uploaded supplementary source, identical | `2aa4b3f6c553d4735e7a7b3de5652d3f58771386688d144f33768b04f20a37d8` |
| Historical methodology script in the baseline commit | `6dc4608ba00ae27f9f13334371309eb49c945049b458d3cb922e1443e84fea3c` |

The uploaded main manuscript adds three explanatory graphics (system
overview, coverage/rotation mechanism, timing anchors), associated references,
and line-breaking/layout edits. It has no different hardware results. Those
layout changes are not silently merged into this methodological correction.
The uploaded file named `PREVIEW_netshield_manuscript_emulated_IEEEtran.pdf`
is not the canonical repository submission PDF.

## The three completion endpoints

| Evidence | Release anchor | Completion endpoint | Supported interpretation |
|---|---|---|---|
| Historical Task A synchronous replay | Origin round, all releases at its beginning | FIFO payload exhausted within the origin round | Same-round upload completion in a deterministic byte-service model |
| Historical Task B tick simulator | Modeled creation tick | Last payload byte exhausted, at most 1,000 ticks later | One-second upload completion; no detector, physical Wi-Fi, core inference, or return delay |
| Accepted hardware timing reconstruction | `created_probe_monotonic_ns`, or scheduled release for the separate sensitivity | `result_received_monotonic_ns` on the same probe clock | Observed core-result return from the specified anchor |

The manuscript now reserves **timely full-core result** for the hardware
endpoint. Archived Task A/B columns named
`post_release_on_time_core_result_coverage` and `on_time_core_results` are
historical schema names for upload-only outcomes, not evidence of inference
or result return. Their original values are preserved. The two simulation
predicates agree only for beginning-of-round releases with a one-round
upload deadline and zero processing overhead. A schedule-inclusive physical
deadline is a separate metric.

The phase sampler uses `random.sample(range(1000), 3)`: three distinct phases
drawn without replacement. The controller is independent in the sense of
using only local queue state; the sampled initial phases are not independent
with-replacement draws. The source description has been corrected accordingly.

## Review findings and changes

| User point | Finding | Resolution and evidence boundary |
|---|---|---|
| 1. Missing end-to-end stages | Confirmed for `simulate_tick_baseline`: it completes a FIFO payload, not a core result. | Correct the main and supplementary endpoint labels. Additional stage-delay simulations are conditional on declared assumptions; measured Wi-Fi/core timings cannot be invented from byte budgets. |
| 2. Integer waterfill remainder | Confirmed: `share == 0: break` can leave fewer than the number of unsatisfied devices unused. | A work-conserving correction is separated from the archived implementation and outputs. The old artifact is retained because exact queue identity depended on its byte accounting. |
| 3. Twelve Task A seeds | Confirmed: the independent synchronized path never invokes seeded joint-admission tie-breaking. | The archive has 36 configurations (12 weights × 3 capacities), each with 12 duplicate session/seed labels. Every group has exactly one queue trajectory. The 432 rows are not 432 independent experiments; no seed-based interval is justified. |
| 4. Simulated zero cap violations | Confirmed as a construction invariant of capped grants. | Relabel as software conformance. An independent ledger auditor must reconstruct grants and per-round totals without calling `waterfill`; full hardware verification requires primitive service records, not an aggregate zero column. |
| 5. Existing backlog | Confirmed: bounding new payload does not by itself make all queued work finish in the round. | State the ideal whole-queue drain condition `sum(Q_i + b_i) <= C`, separately from new-arrival admission and physical result-return feasibility. Corrected backlog-aware behavior is versioned separately. |
| 6 and 9. Shared-link safety | Confirmed: isolated `payload/link_rate` assumes access to the full service rate. | Rename its claim as an individual eligibility heuristic. Shared-service screening requires actual competing work, service discipline, backlog, and a delay model. New counterexamples and model experiments are distinct from the frozen S-CQPG hardware method. |
| 7. Different deadline predicates | Confirmed implementation difference, with a limited equivalence case. | Document origin-round upload completion versus elapsed-time upload completion and use explicit endpoints in corrected outputs. Neither old predicate measures a physical core return. |
| 8. Paper/code mismatch | Confirmed endpoint labels, replicate language, historical/fixed code identity, and uploaded layout differences. | This mapping identifies the authoritative source, archived outputs, corrected software, and hardware evidence separately. |
| 10. Value of evidence levels | Not established by the current results. Perfect scored replay correctness across paths cannot distinguish alert/summary/full detection benefit. | Label utilities as controller inputs; add a concrete pending evidence-content ablation protocol in the supplement. No claim of detection improvement or incident-resolution gain is added. |

## Frozen hardware results retained

The methodological corrections do not replace the accepted primary or CRFA
hardware evidence. CRFA on-time full-core/generated counts remain
990/3,240, 2,050/3,240, and 3,130/3,240 at low/mid/high capacity. The matched
middle-capacity primary C-QPG count remains 952/3,240. The descriptive paired
contrast remains +0.3389 with the originally reported interval; no hardware
rerun or new bootstrap calculation is implied by editing the prose.

The physical cap statements are attributed to the archived service
reconstruction, not to the simulator's allocator assertion. The public
primary result layer does not contain all primitive raw service ledgers.
The original `PASS_WITH_ISSUES` raw-audit disclosure and the nonconcurrent
CRFA comparison remain applicable.

The revision independently reconstructed the public CRFA export using
[`scripts/audit_service_ledgers.py`](../../scripts/audit_service_ledgers.py).
Its report,
[`CRFA_LEDGER_RECONSTRUCTION.json`](../../supporting_material/methodology_validation/CRFA_LEDGER_RECONSTRUCTION.json),
checks 36 runs, 10,620 service rounds, and 9,720 occurrences. Recomputed
post-release full-result counts are 990/2,050/3,130 and the reconstructed
application-grant cap has zero violations. That public CRFA reconstruction
checked exported per-probe service and occurrence records without reopening
the private raw archive or measuring physical link/NIC traffic again. The
later primary-campaign review described in
[`FORMAL_RECORD_INTEGRATION.md`](FORMAL_RECORD_INTEGRATION.md) is a separate
stage: it reports checks over private records and supplies arm summaries for
reconciliation. It does not replace the public CRFA reconstruction or make a
packet-level measurement claim.

## Corrected software and new counterexamples

The baseline script is retained as
[`legacy/run_methodology_repair_v1_3.py`](../../supporting_material/methodology_repair/legacy/run_methodology_repair_v1_3.py).
The maintained runner is
[`run_methodology_repair.py`](../../supporting_material/methodology_repair/run_methodology_repair.py),
with independently importable
[`simulation_primitives.py`](../../supporting_material/methodology_repair/simulation_primitives.py).
Archived CSV values are historical outputs, not regenerated values from the
corrected source. Reproduction must choose the intended version explicitly.

[`run_public_selector_audit.py`](../../scripts/run_public_selector_audit.py)
uses the ten published payload/utility entries, at their published
six-decimal precision, without loading private workload or timing fields.
The historical source reproduces all 36 configurations in action counts,
core-request fraction, payload, and queue trajectory/maxima. The
[`PUBLIC_SELECTOR_AUDIT.json`](../../supporting_material/methodology_validation/PUBLIC_SELECTOR_AUDIT.json)
and [`PUBLIC_SELECTOR_COMPARISON.csv`](../../supporting_material/methodology_validation/PUBLIC_SELECTOR_COMPARISON.csv)
show that work-conserving, round-rotated residual allocation changes
24/36 trajectories and 5/36 action mixes. All changed mixes are at low
capacity with `v = 1, 3, 10, 30, 100`. In particular, `v = 1` and `v = 3`
change from 66/270 to 90/270 full requests and from 9,191,424 to
11,796,480 payload bytes. Thus the two-byte allocator remainder cannot be
dismissed as behaviorally negligible. Corrected simulation results are
separate from the original hardware measurements.

[`TASK_A_REPLICATION_AUDIT.csv`](../../supporting_material/methodology_validation/TASK_A_REPLICATION_AUDIT.csv)
documents all 36 groups and their duplicate historical trajectories. This is
an artifact-level replication audit, not a new confidence analysis.

The new
[`run_contention_validation.py`](../../supporting_material/contention_validation/run_contention_validation.py)
evaluates 30 declared deterministic configurations under four admission
rules. Its
[`CONFIG.json`](../../supporting_material/contention_validation/results/CONFIG.json),
[`RUN_SUMMARY.csv`](../../supporting_material/contention_validation/results/RUN_SUMMARY.csv),
[`EVENT_LEDGER.csv`](../../supporting_material/contention_validation/results/EVENT_LEDGER.csv),
and [`SERVICE_LEDGER.csv`](../../supporting_material/contention_validation/results/SERVICE_LEDGER.csv)
keep assumptions, decisions, endpoints, and service accounting distinct.
The supplementary Shared-Service Counterexamples section reports exact
examples from these records. These runs are not a new physical campaign.

For three 128-KiB requests at a 256-KiB/s shared service, three isolated
500-ms estimates become 1,500-ms upload completion under simultaneous load.
With one 128-KiB old backlog, admitting two new requests again requires
1,500 ms; admitting one drains the total in 1,000 ms under zero stage delays.
Under the explicitly assumed homogeneous delay profile, an upload that
finishes at 1,000 ms returns its result at 1,060 ms. The model-reservation
rule previews the same deterministic execution model and may reject all new
requests; it is a feasibility demonstration, not an optimal or fair physical
safety controller.

## Evidence-value evaluation still required

The supplementary protocol requires matched representations from the same
held-out episodes; a declared content transformation for alert/summary/full;
source-capture/episode splits and duplicate checks; fixed detector/threshold
comparisons; and separate equal-delivery and shared-deadline experiments.
Relevant outcomes include per-family recall, false-positive rate,
precision/recall, calibration, and incident-localization delay alongside
bytes and observed result-return latency. Resampling units must be independent
captures or episodes. These inputs and paired outcomes are not present in
the published aggregate tables, so this remains an unexecuted validation
requirement rather than a new result.
An operational checklist is retained in
[`DETECTION_VALUE_PROTOCOL.md`](../../supporting_material/contention_validation/DETECTION_VALUE_PROTOCOL.md)
with status `NOT_EXECUTED`.

## Later private-record report and content-interface diagnostic

The later audit is integrated through the following public artifacts. Their
scope is deliberately narrower than rerunning the private experiments.

| Artifact | What can be checked from the supplied material | Remaining boundary |
|---|---|---|
| [Arm review](../../supporting_material/experiment_extension/formal_record_reconciliation/results/ARM_REVIEW.csv) and [reconciliation](../../supporting_material/experiment_extension/formal_record_reconciliation/results/RECONCILIATION.json) | Reaggregate 216 accepted primary arms: 63,720 service rounds, 58,320 measured events, 24,012 core-required events and 14,416 timely returns; compare with retained endpoints. | Each arm's 295 rounds includes 5 warm-up, 90 measured and 200 drain rounds. Counts pool six methods and three capacities. The underlying 1,512 private source files are not attached. |
| [Runtime review](../../supporting_material/experiment_extension/FORMAL_RECORD_REVIEW.md) | Read the reported allocator behavior, package identity and historical payload/consumer description alongside the private-record checker source. | The runtime tree and deployment manifests are not available for this integration to rehash; reported local inspection is not a new public proof of their bytes. |
| [Split counts](../../supporting_material/experiment_extension/formal_record_reconciliation/results/SPLIT_COUNTS.json) | Recalculate 190,258/996,486 = 19.09% validation-versus-training and 497,391/1,147,055 = 43.36% test-versus-earlier-splits exact feature overlap. | The 39-feature signature excludes labels and identifiers. Raw partitions and actual-model training lineage are absent; this is neither a near-duplicate scan nor an estimate of accuracy inflation. |
| [Interface summary](../../supporting_material/experiment_extension/formal_record_reconciliation/results/INTERFACE_SUMMARY.json) | Recount nine source observations and 27 representation/decode rows; inspect the script's 18 explicit predictor calls for nine successful cases. | The three labels agree by construction; truth labels and timing fields are absent. This does not execute the proposed information-value ablation or measure detection gain. |

The frozen hardware payloads, the compact heavy-model bit/score/features
interface pilot, and the prospective light-bit/feature-subset Gaussian naive
Bayes diagnostic specify three different encoders and consumers. Their
records and byte costs must not be substituted for each other. The newer
diagnostic also leaves independent capture lineage, near-duplicate
qualification and clean held-out efficacy unresolved. Earlier preparation
records that say models were not executed remain accurate for their own
stage; the later interface exercise is recorded separately rather than
rewriting that history.

## Replacement-cohort measurements

The [hardware extension](../../supporting_material/experiment_extension/physical_extension/README.md) provides action and queue trajectories, origin-clock endpoints and input identities per physical block.

The [matched content measurements](../../supporting_material/experiment_extension/content_measurement/) identify ten parent captures, both fitted stages and the threshold, and all 216 physical representation transmissions.
