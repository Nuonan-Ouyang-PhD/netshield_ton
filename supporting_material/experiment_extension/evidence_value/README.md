# Evidence-value scoring for an actual alert / summary / full ablation

The standalone scorer provides the **scoring and input-validation step**. It does not train a detector, run an encoder, contact a
Raspberry Pi, generate research observations, or assert that the experiment has
been completed. The tests create clearly labelled `SYNTHETIC_FIXTURE` data only
inside temporary directories and delete them afterward.

The current contract supports a **predeclared binary detector**, one frozen
model, one frozen threshold, and three frozen representation encoders. This is a
small, concrete fixed-model ablation. A study using different consumers/models
per representation, multiclass classification, calibration, AUPRC, or per-family
recall needs a separately specified adapter/analysis extension before seeing
held-out results; this scorer does not silently substitute for those analyses.

## 1. Run the scorer

From the repository root, using files exported by the real experiment adapter:

```bash
python3 supporting_material/experiment_extension/evidence_value/score_evidence_value.py \
  --protocol /absolute/path/to/frozen/protocol.json \
  --groups /absolute/path/to/frozen/groups.csv \
  --corpus /absolute/path/to/frozen/corpus.csv \
  --occurrences /absolute/path/to/frozen/occurrences.csv \
  --predictions /absolute/path/to/actual_run/predictions.csv \
  --output /absolute/path/to/actual_run/evidence_value_report.json
```

Python 3.10+ and the standard library are sufficient. No package installation is
needed. Exit status is zero only after validation and successful report creation;
contract errors return 2. Unknown fields, duplicate headers/JSON keys, invalid
numbers, unmatched rows and inconsistent metadata fail closed. An existing output
file is never overwritten. Validation failure does not create a report.

The optional `--bootstrap-seed` and `--bootstrap-samples` arguments are assertions:
they must equal the settings frozen in the protocol. They cannot change analysis
choices after results are known. Phase, primary metric, primary contrast,
comparisons, weighting, confidence level, draw count and seed are protocol fields.

Use a **separate frozen protocol and report for each phase**:

| Phase | Input observations | Permitted endpoint |
|---|---|---|
| `information_only` | Real predictions from the fixed detector and each encoder, without imposing transport loss | Correctness of available predictions, generated-denominator correctness bounds, actual representation bytes |
| `transport_measured` | Actual event creation and returned prediction timestamps, plus observation horizons | Measured timely-correct / generated at the frozen deadline, with unresolved-followup bounds |

Information-only rows must have blank timing and `wire_bytes` fields. The transport
phase accepts `time_source=measured` for real data; `simulated` is never accepted.
The CLI does not infer physical delay from payload size or an application budget.

## 2. Four independent inventories

CSV is UTF-8, has a header, and uses the exact field sets below. Column order may
vary. Empty cells explicitly mean unavailable where permitted; strings such as
`NA`, `null`, `nan` or `inf` are not substitutes. IDs must be stable and pseudonymous.
Do not construct the occurrence inventory by iterating over successful predictions.

### `groups.csv`

```csv
group_id,split
```

Each independent capture or episode group appears exactly once and belongs to
exactly one of `train`, `validation`, or `test`. All three splits must be
represented. Freeze the group definition before splitting. Multiple episodes
from a shared capture must not be called independent groups without a justified
study design; the scorer cannot establish statistical independence from ID names.

### `corpus.csv`

```csv
source_record_id,group_id,split,truth_raw,source_feature_sha256
```

Enumerate records in all three splits, including the training/validation data used
for the frozen detector and threshold. Each source record has one group and one
split. `truth_raw` must occur in the protocol's fixed raw-to-binary label mapping.

`source_feature_sha256` is the hash of the **raw observation / canonical feature
record before representation encoding**, with its serialization defined by the
data-preparation protocol. Hash the observation independently of its ground-truth
label; otherwise equal observations with different labels can evade a leakage
check. Exact feature hashes appearing in different splits are rejected.

A blank source-feature hash is allowed when unavailable. The report then exposes
hash coverage for every split and makes no complete leakage-free claim. Repeated
hashes within a split are counted. This check cannot find near duplicates, semantic
leakage, label leakage through encoders, or prove that declared hashes were computed
from the claimed bytes. The real adapter must calculate and retain those bytes or
a reproducible canonicalization procedure.

### `occurrences.csv`

```csv
occurrence_id,source_record_id,group_id,split,truth_label,source_feature_sha256
```

This is the complete, independently retained **generated held-out denominator**.
Every occurrence must map to a `test` source record and its group, source hash,
and mapped binary truth. Repeated source observations may have distinct occurrence
IDs; they do not create new independent capture/episode groups.

An occurrence ID identifies the same workload item across the three representation
executions. Transport creation/return times belong to each actual execution and
are therefore recorded separately in `predictions.csv`. Build/freeze the workload
inventory without inspecting test predictions and reconcile it with the acquisition
ledger. The scorer verifies inventory consistency and its frozen digest, but an
external acquisition ledger is needed to establish that no generated items were
omitted before this inventory was supplied.

### `predictions.csv`

```csv
occurrence_id,representation,split,truth_label,model_id,encoder_id,threshold_id,status,status_detail,predicted_label,positive_score,source_feature_sha256,representation_sha256,payload_sha256,information_bytes,padding_bytes,payload_bytes,wire_bytes,created_ns,created_clock_domain,result_ns,result_clock_domain,observed_until_ns,observation_clock_domain,time_source
```

There must be **exactly three rows per occurrence**, one each for `alert`,
`summary`, and `full`, even if no prediction was returned. Duplicate rows, missing
representation rows, extra occurrence IDs, altered truth/split/hash values or
wrong model/encoder/threshold IDs are errors. Each encoder ID is tied to its
representation; the model and threshold IDs are shared across all three levels.

| Status | Prediction fields | Meaning |
|---|---|---|
| `returned` | Finite `positive_score` in [0,1] and matching `predicted_label` | Final prediction available. In the transport phase it has actually returned to the event-originating clock domain. |
| `rejected` | Both prediction fields blank; nonempty `status_detail` | Confirmed terminal rejection, not a still-pending result. It counts as an unsuccessful generated occurrence. |
| `missing` | Both prediction fields blank | No final prediction available through the recorded observation horizon; the horizon can be unknown. |
| `censored` | Both prediction fields blank | Followup ended before a final prediction was observed. The recorded horizon is the last continuous observation point. |

The scorer computes the binary prediction from the frozen rule
`positive_score >= threshold` and requires the exported label to agree. Do not
supply logits as probabilities, fit a new threshold, or calibrate on the test set
just to satisfy the interface. Freeze the required probability-producing model
adapter using training/validation data first.

## 3. Byte and content accounting

- `information_bytes` is the serialized **unpadded representation length**. It is
  not Shannon information and not an inferred amount of security value.
- `padding_bytes` counts artificial padding. `payload_bytes` must equal information
  plus padding. Repetition/padding cannot be reported as additional observation
  information. Protocol-level transformations and serialization must be fixed.
  These are constructed/offered representation bytes, including known candidate
  payloads on rejected rows, not bytes actually transmitted or service granted.
- `representation_sha256` hashes the exact unpadded representation consumed by the
  frozen model adapter. `payload_sha256` hashes the actual application payload,
  including padding. A returned prediction requires both hashes and known lengths.
- For an unsuccessful/unknown record, all three length fields may be blank together
  if unavailable; their hashes must also be blank. Known lengths must still sum
  correctly. A known zero-length object, if hashed, must have SHA-256 of empty bytes.
- `wire_bytes` is measured, attributable **uplink evidence bytes including headers
  and retransmissions**, at the predeclared instrumentation layer. It excludes
  result-return bytes in this contract. Leave it blank when not measured; do not
  substitute payload bytes or guessed header overhead. A fully returned transport
  result with known wire bytes must have wire bytes at least as large as its payload.
  Failed/partial uploads can legitimately have smaller measured wire totals.

The report retains known subtotals, missing-cost counts, and null totals when any
cost is unknown. It never treats missing accounting as zero. Encoded alerts may
legitimately be identical across events; `representation_sha256` is deliberately
**not** the cross-split feature-leakage key.

Record hashes are validated for format and consistency, not recomputed from
unprovided feature/payload bodies. Model, encoder and threshold artifact files,
however, are opened and SHA-256 verified by the scorer. Bundle dependencies into
those artifact files/manifests as appropriate and have the real runner attest that
it actually used the frozen artifacts; scoring their hashes alone cannot prove
what an external process executed.

## 4. Clock domains, deadlines and observation maturity

Transport rows require integer nanosecond `created_ns` and a specific
`created_clock_domain`, such as a pseudonymous probe/session/boot identifier plus
`monotonic_ns`. A returned row requires `result_ns >= created_ns` in the **same
clock domain**. Use the probe's result-reception timestamp, not the core's wall
clock or an unsynchronized host timestamp. Relabelling clock IDs is not alignment.

`observed_until_ns`, when present, must be in that same domain, at or after
creation, and at or after a recorded returned result. Its meaning is continuous,
inclusive observation from creation through that horizon. A later batch shutdown
time is not a valid horizon if the probe/logger stopped earlier. An absent horizon
requires a blank `observation_clock_domain`. Returned rows can be resolved from
their valid result timestamp even if no later horizon was retained. A terminal
rejection requires a recorded horizon that establishes it was observed.

The deadline is inclusive:

```text
result_ns - created_ns <= deadline_ns
```

For missing/censored rows, no result observed through
`created_ns + deadline_ns` is a known timely-result failure. Followup ending before
that point, or an unknown horizon, leaves the timely outcome unresolved. The
report produces bounds and a null point estimate instead of inventing a miss.
A terminal rejection remains a failure even before the deadline; it is counted
separately from late results and matured no-result observations.

For (N) generated items with (s) known successes and (u) unresolved outcomes,
reported bounds are `[s/N, (s+u)/N]`; the point estimate is null unless `u=0`.
This applies to correctness and, in the transport phase, timely correctness.
A matured no-result event can have resolved timely correctness (zero) while its
eventual classification correctness remains unknown.

## 5. Frozen protocol

The following is an **invalid-until-populated schema template**, not an experiment
configuration or result. Replace placeholder paths/hashes and the example mapping
with the actual frozen values. Keep the same exact key structure.

```json
{
  "schema_version": "netshield.evidence_value.v1",
  "study_id": "REPLACE_WITH_FROZEN_STUDY_ID",
  "data_origin": "actual_runtime",
  "phase": "information_only",
  "independence_unit": "capture",
  "group_definition": "REPLACE_WITH_CAPTURE_OR_EPISODE_DEFINITION",
  "labels": ["benign", "attack"],
  "label_mapping": {"REPLACE_BENIGN_RAW_LABEL": "benign", "REPLACE_ATTACK_RAW_LABEL": "attack"},
  "dataset": {
    "id": "REPLACE_DATASET_ID",
    "version": "REPLACE_IMMUTABLE_VERSION",
    "groups_sha256": "REPLACE_64_LOWERCASE_HEX",
    "corpus_sha256": "REPLACE_64_LOWERCASE_HEX",
    "occurrences_sha256": "REPLACE_64_LOWERCASE_HEX",
    "population": "all_generated_held_out_occurrences"
  },
  "artifacts": {
    "model": {"id": "REPLACE_MODEL_ID", "path": "model.bundle", "sha256": "REPLACE_64_LOWERCASE_HEX"},
    "encoders": {
      "alert": {"id": "REPLACE_ALERT_ENCODER_ID", "path": "alert_encoder.bundle", "sha256": "REPLACE_64_LOWERCASE_HEX"},
      "summary": {"id": "REPLACE_SUMMARY_ENCODER_ID", "path": "summary_encoder.bundle", "sha256": "REPLACE_64_LOWERCASE_HEX"},
      "full": {"id": "REPLACE_FULL_ENCODER_ID", "path": "full_encoder.bundle", "sha256": "REPLACE_64_LOWERCASE_HEX"}
    },
    "threshold": {"id": "REPLACE_THRESHOLD_ID", "path": "decision_rule.json", "sha256": "REPLACE_64_LOWERCASE_HEX"}
  },
  "decision_rule": {
    "kind": "positive_score_greater_than_or_equal",
    "negative_label": "benign",
    "positive_label": "attack",
    "threshold": 0.5
  },
  "analysis": {
    "primary_metric": "correct_per_generated",
    "primary_comparison": ["full", "summary"],
    "comparisons": [["full", "summary"], ["summary", "alert"]],
    "weighting": "equal_group",
    "bootstrap": {"samples": 2000, "seed": 20261122, "confidence": 0.95}
  },
  "transport": null,
  "near_duplicate_audit": {"status": "not_performed", "method": null, "threshold": null, "artifact": null}
}
```

Artifact paths are relative to `protocol.json`, or absolute. The threshold artifact
must be a JSON object **exactly equal to `decision_rule`**, and its bytes must match
the declared SHA-256. Threshold 0.5 above is an illustrative choice, not a fitted
or recommended threshold; use the frozen validation-derived rule for the actual
model. Corpus/group/occurrence file digests are also checked before scoring.

For the separate transport protocol, set `phase` to `transport_measured`, normally
predeclare `primary_metric=timely_correct_per_generated`, and replace `transport`
with the following object using the actual predeclared deadline:

```json
{
  "deadline_ns": 1000000000,
  "anchor": "event_creation",
  "horizon_semantics": "continuous_observation_through_inclusive_horizon",
  "wire_accounting": "measured_uplink_evidence_headers_and_retransmissions"
}
```

A completed near-duplicate audit uses `status=completed`, a nonempty method, a
finite method-specific threshold, and an artifact descriptor `{id,path,sha256}`.
The scorer verifies that artifact's bytes and records the declared method and
threshold; it **does not execute or certify the near-duplicate analysis**. The
artifact must document feature scaling/serialization, distance or similarity,
search coverage, threshold selection, flagged pairs, and their split reassignment
or exclusion decisions. An exact-hash pass never substitutes for this work.

## 6. Report interpretation and paired bootstrap

Each representation reports generated, scored and correct counts; status counts;
known/unresolved generated-denominator correctness; and byte costs. TP/FP/FN/TN,
precision, recall, specificity, false-positive rate, accuracy and positive-class
F1 are calculated from **returned predictions only**, with that scope explicit.
Undefined quantities remain JSON `null`. Missing/rejected/censored records remain
in generated-denominator metrics and are not silently converted to a negative
classification. This prevents a coverage change from masquerading as improved
conditional detector accuracy.

Per-group metrics are reported separately. Pooled counts weight each occurrence.
The predeclared bootstrap estimand gives **each independent capture/episode group
equal weight**, computes its generated-denominator metric, and averages paired
treatment-minus-control differences. Thus a large capture does not automatically
receive more bootstrap weight than a small capture. This group-macro estimand may
differ from pooled correctness; it is neither across-class macro-F1 nor an average
of per-row F1. The reported F1 is always positive-class F1 from the displayed
confusion counts.

Every bootstrap draw resamples whole groups with replacement and uses the same
indices for both levels and all contrasts. The two-sided percentile interval uses
the frozen seed, draw count and confidence level (200–100000 draws supported).
There is no interval with fewer than two groups or any unresolved outcome in the
contrast's primary metric. Unresolved contrasts retain conservative identification
bounds and a null point estimate. Intervals are descriptive, have no multiple-
comparison correction, and do not by themselves establish causality or independent
groups. No new hardware uncertainty is inferred from deterministic software rows.

The JSON report records the scorer source digest, every input digest, protocol
digest, verified model/encoder/threshold artifact digests, fixed decision/mapping,
phase and data origin. It deliberately omits machine-local artifact paths. Preserve
those files with the real acquisition logs and preregistration identity.

## 7. Test the offline preparation

```bash
python3 -m unittest discover \
  -s supporting_material/experiment_extension/evidence_value/tests -v
```

Tests cover matching/completeness, label and artifact consistency, feature leakage
versus repeated encoded alerts, invalid numbers, byte accounting, clock mismatch,
wrong time order, inclusive deadlines, mature/immature/unknown horizons, rejection
and missing-data denominators, frozen bootstrap settings, unequal group sizes,
undefined metrics, one-group interval suppression, and fail-closed CLI output.

`--allow-synthetic-fixture` exists only for those temporary tests. Without it the
CLI refuses `data_origin=SYNTHETIC_FIXTURE`; with it, output remains labelled
`SYNTHETIC_FIXTURE`, and synthetic transport fields must say `time_source=SYNTHETIC_FIXTURE`
rather than `measured`. The flag is not part of a real experiment command.

## Run the training and inference adapter

The separate `run_content_study.py` command implements the information-only
lane. It requires Python 3.10+ and NumPy (tested with 2.3.5). Start with a
reviewed acquisition register and parent split as described in
`../source_lineage/README.md`. The register must establish the parent, source
boundaries and independence; the mapping checker verifies the supplied bytes
and assignments. The archived 31 CSV identities alone do not meet this
requirement. Keep the register, features, fit artifacts and prediction logs
on the private research volume.

Freeze a JSON run specification before fitting. Fields are:

| Field | Value |
| --- | --- |
| `study_id` | Independent study identifier |
| `dataset_directory` | Directory with the frozen dataset manifest and its three archived JSONL streams |
| `trace`, `mapping`, `split_assignment` | File paths resolved from the spec directory |
| `provenance_sha256` | Object keyed by those three field names with their reviewed file digests |
| `frozen_inputs_sha256` | Digests of `dataset_manifest.json`, `train.jsonl`, `validation.jsonl` and `test.jsonl` from the verified frozen source export |

The test module provides a complete executable example of the source and spec
formats. Archived stream names locate retained rows. All model splits come
from the new parent assignments. The adapter verifies file hashes, source
identity, row coordinates, source labels, feature width and trace counts.
New acquisitions require their own reviewed source evidence and frozen export.
Use a fresh output directory, including after an interrupted run.

```sh
python3 supporting_material/experiment_extension/evidence_value/run_content_study.py \
  /path/to/frozen/run_spec.json /path/to/new/private/run
```

The primary endpoint is full minus alert correct predictions per generated
occurrence, weighted equally by test capture. Every eligible test row enters
all three levels. A second contrast compares full and summary. The paired
bootstrap uses 2,000 draws, seed 20261122. Binary labels 0 and 1 represent
benign and attack. The overlap tables cover all split pairs, using exact
ordered vectors and three-significant-digit signatures. A shared signature
stops the run before fitting and leaves the match records for review.
Rounding can miss neighbours across bin boundaries. Both labels must occur in
each split and the test split must contain at least two parent captures.

The light logistic fit uses train-only standardization and 32 full-batch
gradient updates from zero, step 0.05 and L2 coefficient 0.0001 on the
weights. At logit zero the alert bit is positive. The common consumer fits
class priors, a Laplace-smoothed Bernoulli alert likelihood and diagonal
Gaussian feature likelihoods with a population variance floor of 1e-8.
Summary appends the first four features in frozen order; full appends all 39.
A common decision threshold maximizes balanced accuracy across the three
equally represented validation encodings over 0.25, 0.50 and 0.75. Ties
prefer the threshold closest to 0.5 and then the smaller one. These are
prospective adapter settings. The archived diagnostic used its original fit
and fixed threshold.

The adapter writes its inventories before inference, freezes numerical models,
encoders, threshold and protocol, and submits predictions to the existing
scorer. Private artifacts include a SQLite row index, the actual concatenated
payloads, per-call byte offsets and monotonic durations, predictions, scores
and file digests. Alert/summary/full use 1/33/313 unpadded application bytes.
A failed inference keeps its occurrence and status. Timing recorded inside
this process measures computation. Physical timely correctness requires the
separate measured transport protocol and actual probe clocks. The existing
scorer loads inventories into RAM; size the host for the complete qualified
cohort before execution.

To exercise the adapter on explicitly synthetic data:

```sh
python3 -m unittest discover -s supporting_material/experiment_extension/evidence_value/tests \
  -p test_content_study.py -v
```
