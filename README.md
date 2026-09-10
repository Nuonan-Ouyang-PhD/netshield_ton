# NetShield

Clean submission and reproduction package for the NetShield IEEE/ACM
Transactions on Networking manuscript.

## Start here

- Read the paper: [`submission/manuscript.pdf`](submission/manuscript.pdf)
- Read the supplementary material: [`submission/supplementary.pdf`](submission/supplementary.pdf)
- Build and validate the submission: [`submission/BUILD_INSTRUCTIONS.md`](submission/BUILD_INSTRUCTIONS.md)
- Follow the complete data/reproduction guide: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)

## Reproduce the package

From the repository root:

```bash
python3 submission/validate_submission.py
python3 scripts/verify_submission.py
python3 scripts/verify_campaign_audit.py
python3 scripts/verify_methodology.py
```

To build the PDFs locally:

```bash
cd submission
tectonic -X compile manuscript.tex
tectonic -X compile supplementary.tex
python3 validate_submission.py
```

The validation scripts use only the Python standard library. Tectonic is
needed only to compile the PDFs.

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

## Required equipment for the physical campaign

- Three Raspberry Pi probes: Raspberry Pi 5, Raspberry Pi 4B, and Raspberry
  Pi 3B+.
- One shared edge-core host running the heavy core-side service.
- Wi-Fi connectivity between the probes and the core service.
- A workstation with Python 3 for verification and Tectonic for manuscript
  compilation.

The public checkout does not contain SSH targets, machine addresses, private
model files, raw event ledgers, or the full physical-campaign archive. Those
items must be provided through the controlled reviewer workflow described in
[`RIGHTS_AND_ACCESS.md`](RIGHTS_AND_ACCESS.md); they are not required for the
package-only checks above.

## Reproduction boundary

The repository supports three reproducible activities:

1. build and validate the clean manuscript package;
2. verify the committed aggregate evidence, hashes, provenance, and claim
   boundaries;
3. rerun the offline replay, software sensitivity, timestamp reconstruction,
   and scaling simulation when the retained authorized inputs named in
   `supporting_material/methodology_repair/RUN_METADATA.json` are available.

The 216-arm physical campaign is auditable from the controlled raw archive,
but is not publicly rerunnable from this Git checkout alone. No Raspberry Pi
experiment is started by any repository command.

## Repository contents

- [`submission/`](submission/) — clean paper, supplementary material, figures,
  tables, audits, and build validation.
- [`scripts/`](scripts/) — standard-library verification commands.
- [`supporting_material/`](supporting_material/) — path-free audit inputs,
  sensitivity outputs, and historical supporting material retained for review.
- [`RIGHTS_AND_ACCESS.md`](RIGHTS_AND_ACCESS.md) — access and redistribution
  boundary.
