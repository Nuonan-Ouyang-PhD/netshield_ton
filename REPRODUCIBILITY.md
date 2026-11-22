# Dataset and Reproducibility Guide

This document is the reproducibility entry point for the NetShield ToN review
package. It records the public dataset source, the exact boundary of the
published workload, commands that can be run from this repository, and the
material that remains controlled because it contains private physical-testbed
evidence.

## 1. Public dataset source

The paper identifies its workload as a frozen **CICIoT2023-derived
feature-vector replay**. CICIoT2023 is maintained by the Canadian Institute
for Cybersecurity at the University of New Brunswick.

- Dataset description: [CIC IoT dataset 2023](https://www.unb.ca/cic/datasets/iotdataset-2023.html)
- Dataset download form: [CIC IoT Dataset 2023 download](https://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/)
- Dataset citation: E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian,
  R. Lu, and A. A. Ghorbani, “CICIoT2023: A real-time dataset and benchmark
  for large-scale attacks in IoT environment.”

The official page describes `PCAP`, extracted `CSV` features, examples, and
supplementary collection/feature-extraction material. Download access is
handled by the official form; the repository does not mirror third-party
dataset files.

### Download procedure

1. Open the official dataset description page.
2. Select **Download the dataset** at the bottom of that page.
3. Complete the official download form and save the supplied archive locally.
4. Extract it outside this Git checkout, for example:

   ```text
   /path/to/data/CICIoT2023/
   ├── CSV/
   ├── PCAP/
   ├── Example/
   └── Supplementary material/
   ```

Do not commit the downloaded archive or extracted third-party data to this
private review repository. Before redistribution, follow the dataset
provider's current citation and use conditions.

## 2. What the formal experiment actually consumes

The formal experiment is **not packet replay** and is not an uncontrolled
deployment of CICIoT2023. The accepted campaign uses a frozen feature-vector
workload and frozen runtime artifacts. The following objects were fixed before
the campaign:

- feature-vector workload and occurrence plan;
- detector/action table and utility values;
- feature order and detector execution profiles;
- payload sizes and low/mid/high application-byte budgets;
- window plan, warm-up policy, measured-event count, and deadline rule;
- session seeds and accepted-attempt mapping.

The public repository contains the resulting path-free summaries and the
offline analysis source/results, but it does **not** contain the original
third-party dataset, private model files, or the raw feature-vector material
used to instantiate the physical campaign. Therefore:

> Downloading CICIoT2023 alone does not reproduce the paper's 216-arm physical
> campaign. A full exact rerun additionally requires the authorized frozen
> workload/model/runtime bundle and the private hardware protocol inputs.

This distinction is intentional and is part of the paper's evidence boundary.

## 3. Reproducible levels from this repository

### Level 1 — Repository and result-integrity checks

From the repository root:

```bash
python3 scripts/verify_campaign_audit.py
python3 scripts/verify_methodology.py
python3 scripts/verify_submission.py
python3 submission/validate_submission.py
python3 scripts/verify_methodology_revision.py
```

These checks validate committed hashes, row counts, result identities, claim
and number provenance, citation consistency, and private-path exclusion. They
do not claim that a physical experiment was rerun.

### Level 2 — Offline sensitivity, timing reconstruction, and scaling analysis

The complete private-input analysis uses only the Python standard library but
requires the separately retained audit/runtime inputs named in the historical
`RUN_METADATA.json`. The corrected driver writes a new directory and cannot
overwrite the frozen results. See the current
[correction note](supporting_material/methodology_repair/CORRECTIONS.md):

```bash
export TON_AUDIT_ROOT=/path/to/ToN_FullRaw_Audit_20260908
export TON_RUNTIME_ROOT=/path/to/NSF12_20260906_RC1/runtime
export TON_RAW_ZIP=/path/to/ToN_Raw_Sessions_12x_20260908_under512MB.zip
export TON_OUTPUT_DIR=/path/to/new/corrected_results
export TON_OUTPUT_ZIP=/path/to/new/corrected_results.zip
python3 supporting_material/methodology_repair/run_methodology_repair.py
```

The parameter sweep, desynchronization study, and scaling validation are
offline replay/software simulation. Timing is reconstructed from accepted
formal hardware records. The run
metadata records seeds, environment, input SHA-256 values, and scope guards.

The archived Task A labels do not represent independent stochastic runs:
432 rows are 36 parameter configurations repeated under 12 identifiers. The
corrected driver evaluates each configuration once. Task A/B software
timeliness means last-byte upload completion, with different declared time
resolutions; only Task C reconstructs the hardware result-return endpoint.

### Level 2a — Public corrected models and independent ledger checks

These commands require no private workload, action profile, or model:

```bash
python3 scripts/run_public_selector_audit.py
python3 supporting_material/contention_validation/run_contention_validation.py
python3 scripts/audit_service_ledgers.py \
  --software supporting_material/contention_validation/results \
  --crfa supporting_material/crfa_hardware
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s supporting_material/contention_validation -p 'test*.py' -v
```

The public selector reconstruction uses the rounded payload/utility table
below and does not invent detector timings. The contention study uses
explicitly assumed stage delays and a fixed-rate service model. Its 30
deterministic cases are each run with four policies; neither case counts nor
duplicate seed labels are treated as a sample size for confidence intervals.

The independent auditor sums per-event or per-probe service rather than
trusting a simulator's zero-violation counter. The CRFA audit covers the
committed public export (10,620 service rounds and 9,720 occurrences); it
does not reopen the primary campaign's private raw archive or measure NIC
bytes. All frozen hardware evidence remains unchanged.

### Level 2b — Reconciliation of supplied private-audit exports

A subsequent authorized local review supplied one derived record for each
of the 216 accepted primary arms, archived raw-split overlap counts, and 27
interface-diagnostic rows from nine archived inputs. The path-free export
and independent aggregation are in
[`formal_record_reconciliation/`](supporting_material/experiment_extension/formal_record_reconciliation/).
Its checks establish consistency of these supplied summaries and the public
accepted-arm index; they do not reopen the 1,512 privately retained source
logs or establish primitive chunk/in-flight integrity.

The local source inspection reports the deployed integer-remainder defect.
The supplied records reproduce 63,720 warm-up/measured/drain service rounds,
58,320 measured events and 10,848 B of unallocated demanded service. Reported
timely returns pool all six methods and three capacities. The model-interface
diagnostic is neither a new physical campaign nor a held-out detection study.
At this stage, archived cross-split feature overlap and unresolved capture/model-training
lineage remained explicit eligibility gaps. The paper incorporated
these findings without replacing the frozen hardware results. See the
[integration audit](submission/audit/FORMAL_RECORD_INTEGRATION.md).

### Level 2c — Subsequent private follow-up and checker repair

Commit `dc5269c` reports additional private deployment/window checks, a link
from the portable model export to source models and training/validation file
digests, a rounded whole-corpus overlap scan, and an offline 896-row content
diagnostic. The rounded counts, diagnostic code, protocol text, runtime patch
and narrative status are public. The underlying raw scan output, model and
training provenance artifacts, diagnostic consumer and 2,688 prediction rows,
and runtime comparison receipt are not included in the public checkout.

The public review can recalculate the rounded fractions and inspect the
algorithms; it cannot independently rescore the private diagnostic. All three
representations were reported correct on the selected file prefixes, with
zero observed full-minus-alert difference. Capture/episode independence and a
qualified new test split remain unresolved. See
[`FOLLOWUP_REVIEW.md`](supporting_material/experiment_extension/FOLLOWUP_REVIEW.md).

The original private-record checker is retained under
`experiment_extension/private_record_qualification/legacy/`.
The active checker now rejects erroneous or incomplete recorded fields rather
than returning success after merely counting errors. Its new tests use
synthetic fixtures. A subsequent private execution from b8a978b qualified
all 216 accepted arms for the recorded fields. Verify the public cohort
arithmetic, checker identities and seven diagnostic group summaries with
`python3 supporting_material/experiment_extension/retained_review/verify_export.py`.

### Level 3 — Manuscript build

Build the clean review PDFs with Tectonic:

```bash
cd submission
tectonic -X compile netshield_manuscript.tex
tectonic -X compile netshield_supplementary.tex
shasum -a 256 -c SHA256SUMS.txt
python3 validate_submission.py
```

The evidence snapshot under `supporting_material/evidence_snapshot/` contains
the machine-readable supporting records used by the repository validators.

## 4. Frozen action and service interface

The public manuscript defines the ten frozen actions and their application
payloads/utilities:

| Action | Payload (bytes) | Utility |
|---|---:|---:|
| `L_NONE` | 0 | 0.758501 |
| `L_ALERT` | 256 | 0.825168 |
| `L_SUMMARY` | 4,096 | 0.891835 |
| `M_NONE` | 0 | 0.766968 |
| `M_ALERT` | 256 | 0.833635 |
| `M_SUMMARY` | 8,192 | 0.900302 |
| `H_NONE` | 0 | 0.768378 |
| `H_ALERT` | 256 | 0.835044 |
| `H_SUMMARY` | 16,384 | 0.901711 |
| `H_FULL` | 131,072 | 0.968378 |

The formal application-byte budgets are 131,072, 262,144, and 393,216 bytes
per round (`low`, `mid`, and `high`). The shared-service invariant is:

```text
sum(grant_i(t)) <= C(t)
Q_i(t+1) = max(0, Q_i(t) + payload_i(t) - grant_i(t))
```

The source that generated the archived software outputs is retained in
[`legacy/run_methodology_repair_v1_3.py`](supporting_material/methodology_repair/legacy/run_methodology_repair_v1_3.py).
The corrected active implementation is
[`run_methodology_repair.py`](supporting_material/methodology_repair/run_methodology_repair.py).
They are intentionally not claimed to produce identical outputs: integer
residual service changes the low-capacity closed-loop decisions. Corrected
admission reserves all existing queued bytes before admitting new bytes;
that byte condition alone does not reserve detector/core/return time.

## 5. Evidence and access boundary

The repository intentionally excludes:

- the 1.34 GB raw campaign archive and raw event ledgers;
- packet-level captures and third-party dataset files;
- detector/model artifacts used by the physical run;
- machine identities, SSH targets, network addresses, and local paths.

The accepted campaign is documented as 12 sessions × 6 methods × 3 capacities
= 216 accepted arms. Three invalid infrastructure attempts are retained in
the audit record and excluded from the accepted set; no partial attempt is
stitched into an accepted session.

For an authorized reviewer who needs to audit the raw evidence, the archive
identity and controlled-access boundary are recorded in
[`supporting_material/formal_campaign_audit/README.md`](supporting_material/formal_campaign_audit/README.md),
[`RIGHTS_AND_ACCESS.md`](RIGHTS_AND_ACCESS.md), and the committed audit
manifests. The raw archive itself must be transferred through an authorized
private channel rather than GitHub.

## 6. Known reproducibility gap

The current public review package does not include a script that converts a
fresh CICIoT2023 download into the exact frozen feature-vector workload used
by the formal campaign. That gap must not be hidden. To reach byte-for-byte
end-to-end public reproducibility, a future authorized release would need to
add, subject to dataset/model licensing:

1. a source-file list and SHA-256 manifest for the selected CICIoT2023 inputs;
2. the frozen feature-selection, label-filtering, ordering, and partition
   procedure;
3. the frozen derived workload or an authorized generator;
4. model identities/weights or an independently runnable replacement;
5. a public, non-sensitive runtime configuration and a replay command.

Until those items are released and independently checked, the defensible
claim is: **the committed audit, offline sensitivity analyses, scaling
simulation, manuscript build, and path-free numerical result chain are
reproducible from the stated inputs; the private physical campaign is
auditable by controlled evidence access but is not publicly rerunnable from
the GitHub checkout alone.**
