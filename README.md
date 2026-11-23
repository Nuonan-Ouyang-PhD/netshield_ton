# NetShield

NetShield studies how edge intrusion-detection probes share a limited uplink. Each probe can keep a decision locally or send an alert, a summary, or full evidence to an edge core. The paper examines how these choices affect evidence coverage, queue growth, and the number of results returned before a deadline.

[Manuscript PDF](submission/netshield_manuscript.pdf) · [Supplementary material](submission/netshield_supplementary.pdf) · [Complete package](review_package/NetShield_ToN_Review.zip) · [Overleaf source](review_package/NetShield_ToN_Overleaf.zip)

The manuscript has 14 pages; the supplement has 36. Source files, figures, tables, and build instructions are in [`submission/`](submission/). See the [submission guide](SUBMISSION_GUIDE.md) for the file list.

## Experiments

| Study | Design | What it measures |
|---|---|---|
| [Primary campaign](supporting_material/formal_campaign_audit/README.md) | 216 hardware runs: 12 sessions, 6 methods, 3 budgets | Evidence delivery, queues, and core-result return times using frozen CICIoT2023 feature replay |
| [CRFA extension](supporting_material/crfa_hardware/README.md) | 36 hardware runs across the same session identities and budgets | Rotating full-evidence admission, selection fairness, and attainment of the byte-budget frontier |
| [Allocator and shared-stage comparisons](supporting_material/experiment_extension/physical_extension/README.md) | 8 allocator and 36 shared-stage formal runs, with separate calibration and pilots | Effects of integer remainder allocation, existing backlog, and stage-time estimates |
| [Content and timely correctness](supporting_material/experiment_extension/content_measurement/README.md) | 72 held-out windows, 3 representations, 216 measured transmissions | Classification outcomes and correct results returned within one second |

The content study uses ten identified CICIoMT2024 captures, split 4/3/3 for training, validation, and testing. Alert, Summary, and Full returned 63, 62, and 0 correct results within one second. All 72 Full results eventually returned; 53 were correct. Correctness is assessed against capture-scenario labels, and the test contains two device power-on captures and one malformed-MQTT capture.

These timing results use fixed, padded payloads: 256, 16,384, and 131,072 bytes for Alert, Summary, and Full encodings containing 1, 33, and 313 bytes, respectively. The three probes share 131,072 application bytes per second.

Hardware measurements end when the originating probe receives the core result. Offline queue simulations use upload completion as their endpoint; simulations with processing delays state those assumptions separately. The archived 432-row queue sweep represents 36 deterministic configurations repeated under 12 session labels.

## Verify and build

Run these checks from the repository root with Python 3:

```bash
python3 submission/validate_submission.py
python3 scripts/verify_submission.py
python3 scripts/verify_methodology_revision.py
python3 -B supporting_material/experiment_extension/content_measurement/verify_public.py
```

These checks use the Python standard library. They verify the committed files and reconstruct the published content and transport results. Further commands are in [REPRODUCIBILITY.md](REPRODUCIBILITY.md). The [methodology notes](METHODOLOGY_REVIEW.md) explain the software corrections and their effect on the reported results.

To compile both PDFs:

```bash
bash scripts/build_submission.sh
```

The build requires pdfLaTeX, IEEEtran, and the packages listed in the document preambles. See [build instructions](submission/BUILD_INSTRUCTIONS.md) for dependencies and output checks.

## Data and access

The repository includes derived results and verification code. Exact reruns of the original hardware campaign require its controlled workload, models, runtime, and raw archive. The original CICIoT2023 segments still lack verified parent-capture boundaries; the later CICIoMT2024 study has its own documented sources and splits.

Dataset download routes and reproduction requirements are documented in [REPRODUCIBILITY.md](REPRODUCIBILITY.md) and the [content-study guide](supporting_material/experiment_extension/content_measurement/README.md). Repository access and redistribution terms are in [RIGHTS_AND_ACCESS.md](RIGHTS_AND_ACCESS.md).
