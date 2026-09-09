# NetShield ToN V1.3 Build Report

Status: **PASS**

Build date: 2026-09-09 (Australia/Melbourne)

## Scope controls

- No Raspberry Pi experiment was run.
- Frozen V1.2 raw evidence was read only and not modified.
- V1.2/V4.4 superseded result narratives were not restored.
- GitHub and Overleaf were not modified.
- The submission candidate was built in the isolated `ToN_V1_3_Submission_Candidate_20260909/` directory.

## Environment

- macOS 15.3.1 (Darwin 24.3.0, arm64)
- Python 3.12.14
- pandas 2.2.3
- ReportLab 4.4.9
- pypdf 6.10.0
- Tectonic 0.15.0

## Reproducible commands

Run from the package root:

```sh
cd submission_v1_3
tectonic -X compile netshield_ton_manuscript_v1_3.tex
tectonic -X compile netshield_ton_supplementary_v1_3.tex
cd ..
python3 scripts/verify_submission_v1_3.py
```

The frozen figures and complete tables were generated from the methodology-repair
CSV/JSON outputs before publication. The private-review repository contains the
final sources and generated artifacts, not machine-local build inputs.

## Outputs

- Main manuscript: 12 letter-size pages, IEEE two-column journal layout.
- Supplementary material: 24 letter-size pages; complete large tables use landscape pages.
- Figures: 7 vector PDFs generated from frozen CSV/JSON data.
- Complete tables: Task A, Task B, Task C, release-lateness diagnostics, and Task D.

## Compiler checks

- Undefined citations: 0
- Undefined references: 0
- Missing figures/tables: 0
- Fatal LaTeX errors: 0
- Overfull boxes: 0
- Main-manuscript underfull diagnostics: 13 non-fatal line-breaking warnings
- Supplementary underfull diagnostics: 0

All 12 main pages and all 24 supplementary pages were rendered to PNG for visual inspection. The inspection found no clipped tables, missing graphics, unreadable figure labels, malformed references, or layout defects.

## Permitted mechanical integration edits

- Removed duplicated `Results` and bibliography declarations from the supplied source block.
- Added figure includes and package-relative paths.
- Bound the Task-B range and mean directly to the frozen CSV.
- Broke the long `v` set across lines to remove an overfull box.
- Expanded the journal title to `IEEE/ACM Transactions on Networking`.
- Completed Clockwork pages 443--462 from the official USENIX record.

No theory, RQ, core claim, hardware observation, or methodology-repair result was changed.
