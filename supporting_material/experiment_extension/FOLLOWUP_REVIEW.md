# Review of the private follow-up and recorded-field checker repair

## Revision and evidence scope

This review starts from `dc5269c4864e2c4416d6ce6d8390d741bbaad20b`, following
the earlier `b0ec63b` integration. The local execution claims are retained in
[`FOLLOWUP_STATUS.md`](FOLLOWUP_STATUS.md). The current review inspects those
claims, the public scripts/protocol/rounded counts, and the two supplied PDFs.
It does not execute the private model, rescan the corpus or reopen the original
hardware logs.

The supplied PDFs are byte-identical to the PDFs at `dc5269c`: main
`e27bd98ebae8b795202cc671825aeca0c478384c6b753700d3db11a920cd6c85` and supplement
`1f9cf1114ac12cfdc5e5bc9e5d5120d426ba1de982b4b6f0ad96a278b7aaba2d`.
The later editorial alignment and fresh build are documented separately in
[`PDF_BUILD_REPORT.md`](../../submission/audit/PDF_BUILD_REPORT.md).

| Material | Available public evidence | Limit of this review |
|---|---|---|
| Deployment and recorded windows/events | Checker source and local execution narrative | The new private checker output and its registered raw inputs are not published here; counts are reported local findings. |
| Model and corpus provenance | Local report of 31 source CSV hashes, source-model/export/training-manifest matches and finite-feature validation | The actual source models, corpus, provenance manifests and matching transcript are not attached. |
| Rounded overlap | `ROUNDED_OVERLAP.json` and scan source | Fractions can be recomputed; the whole-corpus scan cannot be rerun without its private input partitions. |
| Content diagnostic | Protocol, executable source, reported counts and consumer digest | Fitted consumer, occurrences, predictions and per-file result tables are absent from the public checkout. |
| Allocator runtime comparison | Patch and reported enumeration ranges | The comparison runner, per-case output and before/after runtime identities are not retained publicly. |
| Hardware extensions | Reported connection failures and zero new physical arms | No old/corrected physical effect or shared-stage calibration result is claimed. |

These distinctions preserve the progress of the local work without converting
reported private results into independently reproduced public results.

## What the private follow-up adds

The local report describes 216 accepted arms and four runtime manifests per
arm, giving 864 manifests. It reports 63,720 configured-cap service rounds and
58,320 measured origins with closed terminal byte balances. These extend the
earlier window/event review. The reported checks still do not independently
identify every chunk, bind remote per-file deployment receipts or attest each
event's clock boot epoch. Historical exclusions and `PASS_WITH_ISSUES` remain.

The provenance work also advances beyond the earlier nine-input stage: the
report links portable-model exports to source classifiers, the training
manifest and training/validation file digests. A verified file-digest chain
does not establish independent acquisition episodes or remove cross-split
feature overlap. The manuscript now distinguishes this reported artifact
binding from the unresolved capture/episode qualification.

## Rounded-signature matching

The public counts are arithmetically consistent with 5,141,673 total rows:

| Split | Rows | Matches to earlier splits | Fraction |
|---|---:|---:|---:|
| Train | 2,998,132 | 0 by traversal order | Not a within-training duplicate result |
| Validation | 996,486 | 282,390 | 28.3386% |
| Test | 1,147,055 | 709,971 | 61.8951% |

The scan rounds each of 39 ordered features to three significant decimal
digits, normalizes signed zero, and matches the complete vector without IDs
or labels. Validation is compared with training; test is compared with the
union of training and validation. Counts are matching rows, not distinct
captures or distinct feature vectors, and include exact matches.

This is exhaustive matching of rounded buckets, not an exhaustive distance
search for all near neighbours. Very close vectors across a rounding boundary
can be missed; sharing a bucket is a candidate-similarity criterion rather
than a validated measure of application equivalence. The 61.8951% fraction
describes the complete reported test split, not the 896 selected test rows.
No selected-subset overlap count is supplied. It is not a quantified model
accuracy inflation or a count of test rows proved to have trained the model.

The published numerical implementation can produce nonfinite rounded values
for extremely small finite inputs when its decimal scale overflows. This was
reproduced with synthetic subnormal values, not observed corpus values. There
is no evidence that it affected this scan. A future qualified runner should
validate both original and quantized values and record its numerical rule.

## Meaning of the 896-row diagnostic

The earlier retained protocol specifies a file-prefix diagnostic, keeping the
archived splits and selecting the first 128 rows per source-file group. The
local report says the test subset contains seven groups and 896 observations,
with three representations per observation, giving 2,688 prediction records.
Each path is reported to yield 768 TP, 128 TN, zero FP/FN and no missing result.
Those counts imply zero observed full-minus-alert correctness difference on
these prefixes. They do not establish population equivalence, noninferiority,
or the absence of useful information in full evidence.

### Information supplied to the consumer

The public code loads the light model. An encoder computes a thresholded local
prediction bit from all features, then serializes that bit with zero, four or
39 features. A common consumer is fitted from selected training rows using
class priors, a Bernoulli bit likelihood and Gaussian likelihoods for observed
features. Unobserved dimensions contribute no feature likelihood.

Inspection finds no test label, event ID, group ID or unencoded test feature
passed to the consumer. Test labels are used after prediction to score the
result. This checks the public calling logic; it does not independently
establish the provenance of the private model or each source feature.

Unlike the earlier nine-observation heavy-model interface exercise, this new
consumer can change its decision when feature likelihoods are added. A
synthetic code-level check produced different alert and summary/full outputs.
Thus the reported agreement on 896 rows is an observed diagnostic result,
not the construction-guaranteed agreement of the previous pilot. All three
reported paths are at the accuracy ceiling on the selected rows, leaving no
possible positive correctness gain on this subset.

### Costs and execution evidence

The diagnostic payloads are 1, 33 and 313 B: one bit stored as a byte, followed
by zero, four or 39 binary64 values. They omit the historical padding and
transport envelope. They are not replacements for the frozen hardware action
costs or measurements of Wi-Fi bytes. The encoder still runs the light model;
the one-byte representation does not establish negligible computation.

The program writes a consumer, occurrence table, prediction table and per-file
confusion counts to a private output directory. Those executed outputs are
not present here, so this review cannot independently verify the consumer
digest, unique event identities, pairing, per-file results or confusion counts.
The script also lacks a complete run manifest tying its dataset files to the
model-training provenance. Such binding may have been performed separately
in the reported local review; it is not demonstrated by this script alone.

No measured transport timestamps or independent parent-capture identities
are available for this diagnostic. No timely-correct-result rate or
capture-level confidence interval follows from it.

### Protocol timing

`CONTENT_PROTOCOL.md` has SHA-256
`1f41186e691da0861cf3bfaf04330ff5a1bd609ef1551282bd0cad05836fd1bf`.
The same digest was recorded in the prior `b0ec63b` integration, before this
follow-up was supplied. There is therefore a retained earlier commitment to
the design text. A complete execution freeze binding protocol, code, chosen
rows, model, input partitions and run start is not supplied. The review calls
this a diagnostic following the previously retained protocol, without claiming
a fully independently verifiable preregistration.

## Why the private-record checker was repaired

Synthetic fixtures executed against the actual `dc5269c` checker established
that it returned exit status zero even when `event_balance_errors` or
`grant_demand_service_errors` was nonzero. Its structural `assert` checks were
also disabled by `python -O`. Empty or repeated accepted-arm lists were not
rejected, and negative/fractional byte fields or incomplete terminal states
could pass checks that were insufficiently constrained.

These are demonstrated validator defects, not observations of those defects
in the historical raw data. The original source is preserved exactly at
[`qualify_private_records_dc5269c.py`](private_record_qualification/legacy/qualify_private_records_dc5269c.py).
The active checker uses explicit checks, binds the expected accepted cohort,
validates recorded identities and integer byte accounting, and returns a
nonzero status for errors or incomplete terminal follow-up. Its scope remains
recorded-field qualification; it cannot manufacture absent chunk, boot-epoch
or remote deployment receipts. The detailed contract and regression commands
are in [`private_record_qualification/README.md`](private_record_qualification/README.md).

The repair is tested on synthetic inputs only. A fresh local execution over
the retained private originals is required. The reported `dc5269c` outcome is
not silently replaced by a claim that the repaired checker has already passed
those records.

## Allocator and physical work

The reported comparison range gives `7^3 × 22 × 3 = 22,638` cases, which is
arithmetically correct. Agreement of the patched private runtime with the
reference on those cases is a local execution report; the public patch and
range alone do not independently recreate that execution. It also does not
measure closed-loop changes on hardware.

The local report records failed P2/P3 name resolution and SSH timeouts at
archived addresses. That establishes a failed qualification attempt, not a
diagnosis that the devices are powered off or permanently unavailable. Three
qualified probes are still needed for the planned paired physical studies.
No physical arm has been added by this follow-up or by the present review.

## Next execution and review record

Continue with [`CODEX_HANDOFF_CN.md`](CODEX_HANDOFF_CN.md). The immediate local
work is to rerun the repaired recorded-field checker and retain its new output;
recover and qualify the configured probes; preserve the actual diagnostic and
provenance artifacts with a path-free review export; and establish independent
capture lineage and a qualified split before the formal content study.

[`FOLLOWUP_VERIFICATION.json`](FOLLOWUP_VERIFICATION.json) records the public
verification run for this repair. Fixture test counts are software-validation
counts, not scientific sample sizes. The frozen hardware evidence, theory and
previous actual result artifacts remain intact.

The final public verification passed 53 preparation/reconciliation/checker
fixture tests, including 11 new private-record qualification test groups.
The retained 18 methodology/ledger tests and nine contention-model tests also
passed. The four repository validators passed, and the frozen-science check
preserved 120 file hashes, 14 formal blocks, 21 labeled equations and the
abstract. These checks do not upgrade the pending private rerun or either
physical extension to completed status.
