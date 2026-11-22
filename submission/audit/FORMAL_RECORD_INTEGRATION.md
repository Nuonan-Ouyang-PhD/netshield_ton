# Formal-record and content-interface integration audit

This report preserves the integration completed at `b0ec63b` from the earlier
supplied archive. The then-prospective content protocol was subsequently
reported executed as a descriptive diagnostic at `dc5269c`; the later evidence
and checker repair are documented in
[`FOLLOWUP_REVIEW.md`](../../supporting_material/experiment_extension/FOLLOWUP_REVIEW.md).
Statements below about absent follow-up outcomes describe this earlier stage,
not the current overall project status.

## Scope and audit stages

This note integrates the supplied `TON_EXT_AUDIT_20261122_avIClI` archive with
the retained NetShield submission. The supplied
[`FORMAL_RECORD_REVIEW.md`](../../supporting_material/experiment_extension/FORMAL_RECORD_REVIEW.md)
reports local inspection of the private RC1 runtime and accepted records.
The material available for this integration consists of that report, checker
source, arm summaries, split counts, and interface records. It does not
contain the private runtime tree, model weights, corpus partitions, or the
1,512 underlying service/event files.

The integration independently reads the checker logic, recounts the supplied
summaries and interface records, recalculates fractions, and reconciles the
accepted arm identities and endpoints with the repository. It does not rerun
the private record scan or model inference. This distinction applies to every
result below. No new physical measurements, counterfactual hardware outcomes,
or held-out detection-efficacy estimates are added.

The earlier `PRECHECK.json` and offline verification concern preparation:
they declare that models and new scientific experiments were not executed
at that stage. They are not overwritten to summarize the later interface
exercise. Likewise, the original
[`RAW_AUDIT_SUMMARY.json`](../../supporting_material/evidence_snapshot/evidence/RAW_AUDIT_SUMMARY.json)
retains its **`PASS_WITH_ISSUES`** verdict. The newly reported checks do not
resolve the absent direct S03/a01 storage-failure record or the absent S07
pre-hardware launcher-abort records identified in that audit.

## Accepted records and denominators

The supplied `formal_records.json` has 216 distinct accepted primary arms.
The public reconciliation is retained in
[`ARM_REVIEW.csv`](../../supporting_material/experiment_extension/formal_record_reconciliation/results/ARM_REVIEW.csv)
and
[`RECONCILIATION.json`](../../supporting_material/experiment_extension/formal_record_reconciliation/results/RECONCILIATION.json).
The scope is 12 sessions × 6 methods × 3 capacities; CRFA's separate 36-arm
extension is not included in these totals. Accepted reruns for sessions 03,
04 and 07 remain whole accepted attempts, without combining partial records
from excluded attempts.

Every reported arm has 295 service-round indices. Together with the frozen
[formal configuration](../../supporting_material/formal_campaign_audit/configs/formal_v1_2_low.json),
this accounts for **5 warm-up + 90 measured + 200 drain rounds**, or
63,720 service rounds across 216 arms. This is not 63,720 measured-origin
events. Three probes each generate 90 measured occurrences per arm, giving
**58,320 measured occurrences**. Drain rounds provide follow-up service and
do not add measured-origin events.

| Method | Arms | Service rounds, including warm-up/drain | Generated measured events | Core-required events | Timely core returns | Unallocated demanded service, B |
|---|---:|---:|---:|---:|---:|---:|
| A: fixed local | 36 | 10,620 | 9,720 | 0 | 0 | 0 |
| B: fixed summary | 36 | 10,620 | 9,720 | 0 | 0 | 0 |
| C: fixed full | 36 | 10,620 | 9,720 | 9,720 | 3,122 | 8,544 |
| D: I-QPG | 36 | 10,620 | 9,720 | 5,652 | 3,108 | 2,304 |
| E: C-QPG | 36 | 10,620 | 9,720 | 4,320 | 4,094 | 0 |
| F: S-CQPG | 36 | 10,620 | 9,720 | 4,320 | 4,092 | 0 |
| **Pooled** | **216** | **63,720** | **58,320** | **24,012** | **14,416** | **10,848** |

These totals pool different methods and capacity conditions; the pooled
return count is not a new performance estimate for one controller. A and B
do not request core execution, so their zero core counts do not establish
zero local detection quality. In the supplied checker output all 24,012
core-required measured events have a return timestamp. A timely return means
`0 <= result_received_monotonic_ns - created_probe_monotonic_ns <= deadline_ns`
on the originating probe's clock; the campaign deadline is one second.
This is post-release timing, distinct from the schedule-inclusive sensitivity.

## What the record checker establishes

The archived
[`review_formal_records.py`](../../supporting_material/experiment_extension/review_formal_records.py)
joins core and probe records by device and window. It compares probe delivery
bytes with core receipt counters, checks queue recurrence and terminal queue
bytes, counts duplicate core windows and within-device measured-event keys,
and evaluates the same-probe result-return endpoint. Across the supplied arm
summaries, receipt disagreements, queue residuals, terminal queue bytes,
receipt-cap exceedance rounds, duplicate core windows, duplicate measured
event keys, window-order errors, unmatched core windows and negative latencies
are all zero. A missing-return counter is omitted when zero under the
checker's `Counter` serialization convention.

Its application-cap check sums core receipt counters within each service
round. This is an additional reported crosscheck of application delivery
records; it is not the simulator's capped-allocation invariant. The original
private files are still needed to reproduce these per-window checks. The
public integration only reaggregates the resulting arm summaries and compares
them with the retained endpoints.

The producer uses the last cap field read for each round; it does not separately
validate cap-field agreement, `grant <= cap`, or `grant <= demand`. Its timing
predicate uses each event's recorded deadline without independently checking
uniform deadlines or clock epochs. These limits remain even when all reported
anomaly counters are zero.

The checker also accumulates
`max(0, min(shared_cap_bytes, summed_demand_bytes) - summed_grant_bytes)`
per service round, totaling **10,848 B**, with 8,544 B in fixed-full arms and
2,304 B in I-QPG arms. The local runtime review reports that the deployed
integer allocator stops when the equal share is zero; its three-equal-demand
example grants 43,690 B per probe from a 131,072 B budget, leaving 2 B.
This ties the defect to reported historical runtime behavior. It does not
measure the effect of a corrected allocator on physical decisions, queue
trajectories or timeliness. The separately labeled public software regression
remains the evidence for corrected-model behavior.

These checks do not reconstruct per-chunk offsets, independently measure
packets or NIC traffic, verify transport overhead or retransmissions, or
establish an absolute-clock alignment correction. A union of round indices
and successful joins is not, by itself, an independent census of every
expected raw device window. Complete record-level replay requires the private
inputs and their acceptance metadata.

## Identity and provenance boundary

All 216 supplied arm summaries contain the same package-tree identity:

`be34cdd19441e66a0042b60f9fe75eb0277a8b9a9bb8eeb8f8f87b6b393d7085`.

The local review reports recomputing that hash from the archived runtime.
This is a reported local-inspection result. Neither runtime bytes nor that
rehashing transcript are attached, so the integration does not independently
reprove the deployed package or model identity.

The supplied `private_sources` registry contains **1,512 SHA-256 entries**:
seven per arm, comprising one core-window file, three probe-window files and
three event-ledger files. These are recorded file identities, not 1,512
attached files. The checker reads each deployment manifest and the accepted
attempt index outside the helper that populates this registry. Consequently,
the registry does not itself bind the deployment manifests, accepted index,
runtime tree, model weights or corpus. Public summaries omit private paths;
their hashes and reaggregation are distinct from verification of those absent
source bytes.

## Exact-feature overlap in the archived partitions

The supplied `split_overlap.json`, summarized in
[`SPLIT_COUNTS.json`](../../supporting_material/experiment_extension/formal_record_reconciliation/results/SPLIT_COUNTS.json),
reports the following counts. The proportions below are recalculated from
those counts, rather than from a new scan of private corpus rows.

| Partition | Rows | Rows matching any earlier partition | Fraction | Comparison |
|---|---:|---:|---:|---|
| Train | 2,998,132 | 0 by construction | Not an independence result | First partition visited |
| Validation | 996,486 | 190,258 | 19.0929% | Training |
| Test | 1,147,055 | 497,391 | 43.3624% | Union of training and validation |

The archived
[`check_split_overlap.py`](../../supporting_material/experiment_extension/check_split_overlap.py)
hashes the ordered 39-feature vector as big-endian binary64 values, normalizing
signed zero and excluding identifiers and labels. It performs **exact feature
matching**, without rounding to three significant digits. Counts refer to rows
matching earlier splits, not distinct feature vectors or independent captures.
The test total does not separate matches to training from matches only to
validation. The train zero says nothing about within-training duplicates.

This result prevents treating these full partitions as a new disjoint
held-out feature evaluation. It does not prove which rows trained the actual
deployed model, quantify accuracy inflation, establish independent episode
lineage, or replace a near-duplicate audit. The raw corpus and its training
lineage are absent here. Source-file group counts in the local narrative are
not independently enumerated by this output and must not be called independent
capture counts.

The checker assumes numeric inputs: its `x or 0.0` expression also maps other
false-like values to zero and does not explicitly reject nonfinite values.
The supplied archive shows no malformed corpus row. This is an input-validation
limitation, not an observed explanation of the overlap. A new qualified scan
should validate exactly 39 finite numeric values and normalize numeric zero
only. The released evidence-value scorer's cross-split exact-overlap guard
would reject a complete input manifest containing these reported matches.

## Nine-case interface exercise

The supplied `pilot_model_interfaces.jsonl` has **27 representation/decode
records from nine source observations**: three source-line positions for each
of the P1/P2/P3 file labels, with alert, summary and full for each observation.
The public recount is in
[`INTERFACE_SUMMARY.json`](../../supporting_material/experiment_extension/formal_record_reconciliation/results/INTERFACE_SUMMARY.json).
The script derives the device label from the source filename; this is not
evidence of execution on three physical probes.

The archived
[`check_model_interface.py`](../../supporting_material/experiment_extension/check_model_interface.py)
calls the heavy classifier once to obtain a probability, then emits either
the thresholded bit, that same probability, or the feature vector. The alert
consumer reads the bit; the summary consumer thresholds the probability;
only the full consumer calls the classifier again on the decoded vector.
For nine successful observations this implies **18 explicit application-level
predictor calls**, not 27 independent inferences. This count describes the two
visible prediction call sites; it does not count any internal loader work.

All three decoded labels agree for every observation: five observations
produce label 0 and four produce label 1. That agreement follows from the
construction and is not evidence that more information improves detection.
The encoder also computes the heavy prediction before producing alert and
summary, so this exercise cannot establish their lower inference cost.

The rows record one model identity,
`9bbeea6b4da914b3fa41033bc989e8241979e973a1e17750894697fa17179bfa`,
and nine distinct hashes of complete source lines. Source-line hashes are not
the feature-only split signatures; they do not prove feature independence.
The script invokes a model-identity validator, but that private implementation
and model bytes are absent here. This integration checks the archived source
and records rather than executing or independently hashing the model.

There are no truth labels, correctness fields, creation/return times, clock
domains, observation horizons, inference durations or transport measurements
in these rows. The result is an interface diagnostic, with no accuracy,
information-value, or timely-correct-result estimate. Encoded JSON lengths
are 16 B for alert, 13 or 20 B for summary, and 209–246 B for full. They are
new unpadded representation lengths, not historical action costs or measured
wire bytes. Identical alert encodings across observations are expected for
binary predictions and are not, by themselves, source-feature leakage.

## Three content definitions remain separate

| Context | Representation and consumer | Supported status |
|---|---|---|
| Historical physical campaign | The local runtime review reports the same event/device/local-score metadata in alert and summary, padded to their configured lengths. The 131,072 B full bundle also contains a feature record, pseudorandom context and zero fill. The reported core consumer uses the decoded feature vector. | Historical application service costs and reported runtime semantics. Actual runtime/payload bytes were not attached for a new decode in this integration. No detection gain follows from the padded sizes. |
| Supplied interface pilot | Heavy-model prediction bit / heavy-model probability / full features as compact JSON; consumers read the bit / threshold the score / rerun heavy inference. | Nine observations and 27 archived decoded rows. No labels, efficacy estimate or measured timing. |
| Supplied prospective `CONTENT_PROTOCOL.md` | A light-logistic prediction bit; that bit plus four binary64 features; or that bit plus all 39 features, nominally 1/33/313 B. A proposed training-only diagonal Gaussian naive Bayes consumer combines feature likelihoods with an alert-bit likelihood. | A different proposed diagnostic. No matching trained consumer, prediction table, first-128-per-group outcomes or rounded near-duplicate scan is supplied. |

The label field reported inside a historical full bundle is not proof that
the core classifier consumed ground truth. Conversely, the narrative assertion
that scoring uses only features is not independently reverified without the
runtime source. The manuscript should attribute this detail to the retained
runtime inspection.

The prospective content protocol retains the archived splits and proposes
file-prefix diagnostics and rounded feature signatures. It has no external
timestamp evidence here establishing when it was frozen relative to outcomes.
Even if run later, retaining overlapping partitions would yield a descriptive
diagnostic rather than clean held-out generalization. The executed exact-match
scan must not be relabeled as the proposed rounded near-duplicate analysis.
Independent parent-capture lineage and a qualified evidence-value evaluation
remain open requirements.

## Integration verification

The current
[`FORMAL_INTEGRATION_VERIFICATION.json`](../../supporting_material/experiment_extension/FORMAL_INTEGRATION_VERIFICATION.json)
records 42 passing preparation/reconciliation fixture tests: the prior 35 plus
seven new reconciliation test groups. The actual supplied summaries were
exported and the path-free public results passed `verify-public`. These fixture
tests and summary checks are distinct from scientific experiments.

The retained 18 simulation/ledger tests and nine contention-model tests also
passed, as did the four repository submission/campaign/methodology validators.
The frozen-science verifier preserved 120 file hashes, 14 formal blocks, 21
labeled equations and the abstract, and reconstructed the retained public
selector, software and CRFA evidence. The source-matched PDFs have 14 and 33
pages; all 47 pages were rendered and reviewed, as documented in
[`PDF_BUILD_REPORT.md`](PDF_BUILD_REPORT.md).

No private original ledger, model or corpus was executed in this integration.
The local review at `75a29eda2105b926ab00699b138037e50b13eb9e` and its
[`FORMAL_RECORD_REVIEW.md`](../../supporting_material/experiment_extension/FORMAL_RECORD_REVIEW.md)
remain the attributed source for the private inspections. The updated
[`CODEX_HANDOFF_CN.md`](../../supporting_material/experiment_extension/CODEX_HANDOFF_CN.md)
continues from this stage without treating the remaining physical and qualified
content studies as complete.

## Supplied input identities

The following hashes were computed directly from the supplied archive files
used in this integration. Basenames below identify inputs, not private host
locations. Hashes of sanitized public exports are recorded separately by the
reconciliation workflow; they must not be substituted for these input hashes.

| Supplied input | SHA-256 |
|---|---|
| `formal_records.json` | `b7871e59d6e22badcf7d53c9cac2fcf92d8670f8261773ccde021467275fe543` |
| `review_formal_records.py` | `85ae801b44e534659d29f6ac2f9986553625d788265ccffc473fd2d4fecbd7ce` |
| `FORMAL_RECORD_REVIEW.md` | `41299e7c3ca58d429ce93745c85904ba4e711c0ed886141d90efca29c893d01d` |
| `split_overlap.json` | `b10759543c95823d61dbc2819827595692e3875b2720a31bbe862d6f1ac5366e` |
| `check_split_overlap.py` | `27231498d5f5df8cb7c53ba705029e8ade11b3282fe760f1dae414de3c907676` |
| `pilot_model_interfaces.jsonl` | `99ced64a9b73a3ecead7b720eeccc3f2a685d75028825e2c38fc4afc95f9b9d0` |
| `check_model_interface.py` | `c564ecfcdc54fba6166541d4c87e991a47af9ed0ed13eb74695fa63b643ef50b` |
| `CONTENT_PROTOCOL.md` | `1f41186e691da0861cf3bfaf04330ff5a1bd609ef1551282bd0cad05836fd1bf` |
| `PRECHECK.json` | `47630355546573354740b93cf9a900e06862e44493a070e7ad93d2b7f06df573` |
