# Exported-review reconciliation

This tool reconciles the returned audit reports; it does **not** rerun the
private raw-log audit, load detector models, contact Raspberry Pis, rehash
source feature arrays or create a corrected-hardware result.

## Reproduce the public checks

From the repository root, using only Python's standard library:

```bash
python3 supporting_material/experiment_extension/formal_record_reconciliation/reconcile.py verify-public
python3 -m unittest discover -s supporting_material/experiment_extension/formal_record_reconciliation -p 'test_*.py' -v
```

The public check recomputes the accepted arm cohort and method/capacity
aggregates from the 216-row sanitized CSV. It checks split-summary arithmetic,
interface-summary consistency and the committed product/source/index hashes.
It cannot reverify the private inputs whose digests are recorded as provenance.

## Export from the returned private reports

Keep the provided audit archive read-only. Point `--audit-root` to the folder
containing `formal_records.json`, `split_overlap.json` and
`pilot_model_interfaces.jsonl`. Point `--producer-dir` to its retained review
sources, without executing them:

```bash
python3 supporting_material/experiment_extension/formal_record_reconciliation/reconcile.py export \
  --audit-root "$TON_RETURNED_AUDIT_DIR" \
  --producer-dir "$TON_RETAINED_REVIEW_SOURCE_DIR" \
  --output "$TON_NEW_RECONCILIATION_DIR"
```

The destination must be new or empty. The public accepted index defaults to
`supporting_material/formal_campaign_audit/results/ATTEMPT_INDEX.json`;
`--accepted-index` selects an explicit retained copy. The producer directory
must contain `review_formal_records.py`, `check_split_overlap.py` and
`check_model_interface.py`. Only their bytes are hashed; they are never
imported or executed.

## Outputs

- `ARM_REVIEW.csv`: all 216 accepted arm summaries, including reruns S03/S04/S07
  a02; explicit counters and reported package-tree identity, without private
  source paths.
- `SPLIT_COUNTS.json`: reported row/overlap counts, fractions and source-file
  digests, with held-out efficacy explicitly unqualified.
- `INTERFACE_SUMMARY.json`: 27 interface rows summarized as nine archived
  observations with three new representations each. No raw observations,
  source IDs, predictions, device addresses or model artifacts are exported.
- `RECONCILIATION.json`: exact cohort aggregates, hashes, diagnostic statuses,
  the 1,512-source-file registry count and explicit evidence limitations.

The original producer creates `Counter` fields only when used. Only its five
known optional fields (`core_event_stages`, `core_required`, `timely_core`,
`missing_return`, `negative_latency`) are filled with zero when absent.
Mandatory fields cannot be omitted. Unknown row shapes, negative/noninteger
counters, duplicate/missing/wrong arms, inconsistent counts and unexpected
reported deployment identities are rejected before output creation.

Nonzero reported diagnostic counters are retained, flagged `FAIL`, and yield
a nonzero CLI exit after export. No arm is dropped. The observed allocation
deficit is a scientific quantity and is retained separately; it is not an
exclusion rule or proof of an actual corrected-hardware effect.

## Evidence interpretation

The returned arm report contains **63,720 service-round identifiers** and
**58,320 measured-origin events**. Each arm has 295 service rounds
(5 warmup + 90 measured-generation + 200 drain) and 270 measured events.
The reported core-required/timely counts are **24,012/14,416**, with no
reported missing return. The allocation deficit is **10,848 bytes across all
service phases**, entirely in C-low, C-mid, D-low and D-mid. These are counts,
not independently measured wall-clock durations.

The reported deployment hash is identical in the 216 rows. This does not
establish that the original reviewer cryptographically reverified every host
and deployment tree. Its source registry does not include deployment manifests
or the accepted index; the reconciliation adds the public index digest but
does not retroactively repair the original provenance chain.

Probe/core receipt-counter agreement and a zero reported receipt-cap count
are per-window checks. They do not establish primitive packet/chunk offsets,
NIC delivery, every expected device/window cell, grant-cap bounds or clock
epoch qualification. Those limitations are encoded in `RECONCILIATION.json`.

The split counts are the returned producer's exact-feature overlap counts,
not a fresh array-level audit. Matching rows are not independent captures or
distinct feature vectors. Capture lineage, near duplicates and exact model
training-input binding remain open.

The nine interface observations are archived pilot input rows, not nine Pi
experiments. The new alert bit and summary score derive from the same model
output, and full reuses the observation. Agreement is by construction and is
not accuracy, held-out efficacy, a historical wire-format equivalence result,
or evidence that larger payloads improve detection.
