# Targeted experiment preparation

This directory prepares the next **real** experiments without manufacturing
new hardware or detection results. Start with [`PROTOCOL.md`](PROTOCOL.md)
and the complete Chinese [`CODEX_HANDOFF_CN.md`](CODEX_HANDOFF_CN.md).

## Current progress

The subsequent [`FORMAL_RECORD_REVIEW.md`](FORMAL_RECORD_REVIEW.md) reports
local archived-runtime inspection, primary window/event checks, raw-split
feature overlap and a nine-input model-interface diagnostic. The
[`formal_record_reconciliation/`](formal_record_reconciliation/) directory
provides a path-free exported-report reconciliation, and
[`FORMAL_RECORD_INTEGRATION.md`](../../submission/audit/FORMAL_RECORD_INTEGRATION.md)
documents the manuscript update. These are partial empirical/audit advances;
the fixed-allocator hardware comparison, causal shared-stage experiment and
qualified held-out content-value evaluation have not been completed.
[`PREPARATION_STATUS.json`](PREPARATION_STATUS.json) records each stage's
current evidence scope rather than treating every stage as unexecuted.

The published methodological revision starts at
`e9a2d335e75d1f34efb71c6a0fa2cf4b085660f5` on review PR #3. Its 120 model
runs, public selector reconstruction and CRFA export audit remain separate
from the unexecuted content-value and physical extensions prepared here.

## Tools that run without private inputs

| Tool | Purpose | What it does not establish |
|---|---|---|
| `discover_assets.py` | Read-only source/model/data candidate discovery with hashes and selected schema names | Which code actually ran, dataset independence, model compatibility, or a scientific result |
| `freeze_inputs.py` | Freeze and later verify named input bytes without copying private contents or absolute paths | Scientific adequacy, genuine pre-outcome registration, or actual model/hardware execution |
| `evidence_value/score_evidence_value.py` | Validate and score matched binary-task representation outcomes, grouping, missingness and optional measured deadlines | Execution of real encoders/models; that adaptation must run on qualified local inputs |
| `hardware/plan_hardware.py` | Produce reproducible calibration/pilot/formal plans, order diagnostics and qualification records | SSH/device execution or implementation of a real shared-stage controller |
| `../../scripts/verify_experiment_extension.py` | Run synthetic fixture tests and recheck the frozen public scientific artifacts | New empirical evidence or qualification of private materials |

## One verification command

From the repository root:

```bash
python3 scripts/verify_experiment_extension.py --output /tmp/netshield_extension_verification_NEW.json
```

Choose a fresh output filename. Fixture data are created in temporary test
directories and are explicitly synthetic. Test success never changes an
experiment's state to `EXECUTED`.

## Discover actual assets locally

```bash
python3 supporting_material/experiment_extension/discover_assets.py \
  --root checkout=. \
  --root private_runtime=/actual/authorized/runtime \
  --root private_evidence=/actual/authorized/evidence \
  --output /private/new_campaign/ASSET_INVENTORY.json
```

Replace example paths with observed local locations. The tool reads candidate
source as text/AST and never imports it or deserializes a model. CSV discovery
exports only names from a fixed schema vocabulary, not arbitrary cells or
feature values. It skips credential-like files, hidden directories and
symlinks. Large-file hashes are explicitly omitted above the configured
`--hash-max-bytes` limit and must be frozen separately. Missing roots, read
errors and truncation yield a partial report and nonzero exit status.

Source findings, including the integer-division/zero-break heuristic, require
manual call-path and deployed-artifact review. Directory discovery does not
certify that all relevant materials have been searched.

## Freeze qualified inputs before formal outcomes

```bash
python3 supporting_material/experiment_extension/freeze_inputs.py freeze \
  --label NEW_STUDY_FORMAL_INPUTS \
  --input protocol=/private/new_campaign/protocol.json \
  --input runtime=/actual/runtime/snapshot.tar \
  --input workload=/actual/frozen/workload.manifest.json \
  --input model=/actual/frozen/model.onnx \
  --input analysis=/private/new_campaign/analysis_plan.json \
  --manifest /private/new_campaign/INPUT_MANIFEST.json
```

Use actual artifacts, not empty examples. Repeat the same names and paths
with the `verify` action before and after execution; omit `--label`. The
manifest detects missing, extra, modified or changing files. Keep immutable
source snapshots and all named files, not just their hashes. A directory
must first be frozen through an explicit complete manifest or deterministic
snapshot; hashing one convenient source file does not freeze an entire
runtime.

## Study-specific contracts

- [`evidence_value/README.md`](evidence_value/README.md) specifies the exact
  protocol, groups, corpus, generated occurrence and prediction inputs. The
  current scorer supports a prespecified **binary** task. A timeline,
  localization or correlation task needs its own qualified scorer.
- [`hardware/README.md`](hardware/README.md) specifies the plan generator,
  qualification record, raw event/service schemas and real-controller
  integration requirements. A six-condition shared-stage diagnostic is a
  controlled H-FULL/H-NONE comparison, not an unchanged S-CQPG rerun.

Private runtime, model, data, machine identities and primitive hardware logs
remain in their authorized local storage. Review and publish only permitted
code, path-free aggregates and reports. Keep the 252 historical hardware
arms and previous scientific outputs immutable. Current manuscript/PDF
changes are deferred until new qualified measurements actually exist.
