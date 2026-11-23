# NetShield

[主稿 PDF](submission/netshield_manuscript.pdf) · [补充材料 PDF](submission/netshield_supplementary.pdf) · [定向补实验执行记录](supporting_material/experiment_extension/physical_extension/README.md)

Clean submission and reproduction package for the NetShield
IEEE Transactions on Networking manuscript.

## Start here

- Read the paper: [`submission/netshield_manuscript.pdf`](submission/netshield_manuscript.pdf)
- Read the supplementary material: [`submission/netshield_supplementary.pdf`](submission/netshield_supplementary.pdf)
- Build and validate the submission: [`submission/BUILD_INSTRUCTIONS.md`](submission/BUILD_INSTRUCTIONS.md)
- Follow the complete data/reproduction guide: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Read the methodology correction and remaining evidence gaps:
  [`METHODOLOGY_REVIEW_CN.md`](METHODOLOGY_REVIEW_CN.md)
- Follow the current source-to-evidence mapping:
  [`submission/audit/CODE_EVIDENCE_ALIGNMENT.md`](submission/audit/CODE_EVIDENCE_ALIGNMENT.md)
- Read the retained experiment workflow in the complete
  [`one-pass Codex execution instructions`](supporting_material/experiment_extension/COMPLETE_LOCAL_EXECUTION_CN.md)
  and [`offline preparation tools`](supporting_material/experiment_extension/README.md).
  Their earlier pre-collection checkpoints are superseded by the completed
  physical results linked below.
- Review the subsequent retained-record findings and their integration in
  [`FORMAL_RECORD_INTEGRATION.md`](submission/audit/FORMAL_RECORD_INTEGRATION.md).
  The primary window/event review, raw-split overlap and model-interface
  diagnostic precede the [physical extension](supporting_material/experiment_extension/physical_extension/README.md). The [held-out content study](supporting_material/experiment_extension/content_measurement/) uses separately verified CICIoMT2024 captures.
- The [retained-record status](supporting_material/experiment_extension/COMPLETION_STATUS_CN.md)
  covers the private record checks, the 896-row diagnostic and the source-row trace.
  The [physical comparison](supporting_material/experiment_extension/physical_extension/README.md)
  reports 8 allocator and 36 shared-stage formal arms, with separately
  registered qualification, calibration and pilot measurements.
  The [capture provenance review](supporting_material/experiment_extension/physical_extension/CONTENT_INPUT_REVIEW.md)
  documents the unresolved lineage of the original CICIoT2023 segments.

## Methodology correction

The current offline driver fixes integer residual service and reserves existing
backlog during admission. Its software deadline endpoint is **payload upload
completion**. The hardware endpoint remains **core-result return**. The original
driver and all frozen experimental outputs are retained with their hashes.

Task A's 432 archived rows represent **36 deterministic configurations**, each
repeated under 12 session labels. The public reconstruction reproduces those 36
historical configurations and separately reports the corrected allocator's
changed trajectories. A new 120-run deterministic shared-service experiment
adds explicit assumed processing/core/return stages; it is not measured Wi-Fi.
See [`supporting_material/contention_validation/`](supporting_material/contention_validation/).

## Reproduce the package

From the repository root:

```bash
python3 submission/validate_submission.py
python3 scripts/verify_submission.py
python3 scripts/verify_campaign_audit.py
python3 scripts/verify_methodology.py
python3 scripts/verify_methodology_revision.py
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s supporting_material/contention_validation -p 'test*.py' -v
```

To build the PDFs locally:

```bash
bash scripts/build_submission.sh
python3 submission/validate_submission.py
```

The validation and public simulation scripts use only the Python standard
library. A working TeX installation with IEEEtran is needed to compile the
PDFs; see the current build instructions for the pdfLaTeX route.

## Required data

The public source dataset is [CICIoT2023](https://www.unb.ca/cic/datasets/iotdataset-2023.html),
available through the official [download form](https://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/).
Download the provider's archive and keep it outside this Git checkout. The
provider describes `PCAP`, extracted `CSV` features, examples, and
supplementary processing material.

The paper uses a frozen **CICIoT2023-derived feature-vector replay**, not a
packet-level replay. A fresh download by itself does not recreate the exact
formal workload: the authorized frozen workload/model/runtime bundle and the
private raw hardware archive are also required for an exact physical rerun.
This boundary is documented in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Equipment and physical cohort identities

- The accepted primary and CRFA campaigns used Raspberry Pi 5, Raspberry
  Pi 4B, and Raspberry Pi 3B+ probes.
- The later allocator and shared-stage comparisons used a separately
  identified replacement cohort: Raspberry Pi 5, Raspberry Pi 4B, and
  Raspberry Pi 4B with 8 GB RAM. These measurements do not replace the
  historical campaigns.
- One shared edge-core host running the heavy core-side service.
- Wi-Fi connectivity between the probes and the core service.
- A workstation with Python 3 for verification and pdfLaTeX for manuscript
  compilation.

The public checkout does not contain SSH targets, machine addresses, private
model files, raw event ledgers, or the full physical-campaign archive. Those
items must be provided through the controlled reviewer workflow described in
[`RIGHTS_AND_ACCESS.md`](RIGHTS_AND_ACCESS.md); they are not required for the
package-only checks above.

## Reproduction boundary

The repository supports five reproducible activities:

1. build and validate the clean manuscript package;
2. verify the committed aggregate evidence, hashes, provenance, and claim
   boundaries;
3. rerun the offline replay, software sensitivity, timestamp reconstruction,
   and scaling simulation when the retained authorized inputs named in
   `supporting_material/methodology_repair/RUN_METADATA.json` are available;
4. run the corrected public selector reconstruction and shared-service
   counterexamples, and independently reconstruct the public software/CRFA
   ledgers without private inputs;
5. recompute the replacement-cohort physical comparisons and all 16 empirical
   calibration parameter sets from the public exports using the commands in
   [`physical_extension/README.md`](supporting_material/experiment_extension/physical_extension/README.md).

Current offline commands and the historical/current source distinction are
documented in [`supporting_material/methodology_repair/CORRECTIONS.md`](supporting_material/methodology_repair/CORRECTIONS.md).

The 216-arm physical campaign is auditable from the controlled raw archive,
but is not publicly rerunnable from this Git checkout alone. The verification
and build commands above do not start Raspberry Pi experiments. Physical
acquisition requires the separately qualified equipment, controlled inputs
and frozen execution protocol.

## Repository contents

- [`submission/`](submission/) — clean paper, supplementary material, figures,
  tables, audits, and build validation.
- [`scripts/`](scripts/) — standard-library verification commands.
- [`supporting_material/`](supporting_material/) — path-free audit inputs,
  sensitivity outputs, and historical supporting material retained for review.
- [`supporting_material/crfa_hardware/`](supporting_material/crfa_hardware/) —
  path-free CRFA hardware-extension results, protocol, timing reconstruction,
  and provenance.
- [`RIGHTS_AND_ACCESS.md`](RIGHTS_AND_ACCESS.md) — access and redistribution
  boundary.
