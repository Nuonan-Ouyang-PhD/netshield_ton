# Final submission build and editorial integration

Date: 23 November 2026 (Australia/Melbourne).
Scientific-results baseline: `75d529c9f52612c050832da269a7caf4f7b73539`.

## Final changes

The six-block physical backlog comparison now appears in Results, Section V-C.
With 131,072 B initial backlog, the three policies select 12/6/0 Full requests
among 18 first-batch generated events per policy and return 0/6/0 within one
second. The paragraph preserves the empty-queue control and calibrated
all-reject result. Limitations retains the overlapping empirical-timing-budget
interpretation and refers back to Results. No new scientific outcomes are
inferred from this editorial move.

README, the current code/evidence mapping and citation title now match the
completed physical studies and manuscript. The cover letter foregrounds the
networking contribution. The package includes a submission file guide and a
standalone Overleaf source package.

## Actual build and PDF review

Engine: `pdfTeX 3.141592653-2.6-1.40.26 (TeX Live 2025/dev/Debian)`. Genuine IEEEtran SHA-256:
`da751920a317ed318b7b5cd7fa585a6cc7d28502d457856382e9be24b10a3bd7`.

Three successful pdfLaTeX passes per document, with shell escape disabled.
Both final logs have zero overfull boxes, missing-character errors or unresolved
citations/references. Nonfatal notices are retained in `PDF_BUILD_METADATA.json`.

| Document | Pages | Source SHA-256 | PDF SHA-256 |
|---|---:|---|---|
| Main manuscript | 14 | `bec6989d775de5feff6a1f65ba5cd67502af9dec49625e04d3f2134f442d292e` | `50411b190478158bb50ce4427d182cfff297154f1a73c2ce6f6600474f47f48c` |
| Supplement | 35 | `f54d42f49c8a125ccce3af675002d61df4c0e259021ad6b7e36b393624c7d214` | `57674f497ea51914460bbe8a47029b253d8ef6e6f4364a4717a4576b3f3123a4` |

All 49 pages were rendered with Poppler at 110 dpi and visually reviewed in
13 contact sheets (four for the manuscript, nine for the supplement). Detailed
checks included manuscript pages 8, 9, 13 and 14 and supplementary pages 18,
31 and 35. The new result paragraph fits on manuscript page 9, and all 35
references fit on page 14. No visible clipping, overlap, missing glyphs or
unintended rotation was found. An independent rotation-aware bounds scan found
no text blocks extending outside any page.

The supplied PDFs retain the original figures and their font encodings. No
PDF/A or universal font-embedding claim is made.

## Executed validation

The following commands all exited successfully; their exact output is retained
in `FINAL_CHECKS.json`:

- `python3 submission/validate_submission.py`
- `python3 scripts/verify_submission.py`
- `python3 scripts/verify_campaign_audit.py`
- `python3 scripts/verify_methodology.py`
- `python3 scripts/verify_methodology_revision.py`

These checks include 120 frozen file identities, 14 formal blocks, 21 labelled
equations, the unchanged abstract, 36 public selector cases, reconstruction of
120 deterministic software runs, and 10,620 CRFA service rounds / 9,720
occurrences. This is package verification, not new physical collection.

The public verification completed at the baseline also reproduced all 8
allocator and 36 shared-stage formal arms and all 16 calibration envelopes.
Those experiment files and analysis implementations are unchanged by this
finalization. Independent held-out content value remains unavailable because
the parent-acquisition mapping is unresolved.

## Delivery and GitHub

The complete review ZIP contains the current source, both PDFs, supporting
public evidence and a per-file SHA-256 manifest. The standalone Overleaf ZIP
contains the same two sources, required figures/tables, supplied PDFs and
cover-letter text, with its own checksum manifest. Archive identities are
recorded in `review_package/PACKAGE_MANIFEST.json` outside the archives to avoid
self-referential hashes.

Changes are published to the existing PR #3 review branch. The PR remains draft
and `main` is not merged. Journal submission is performed by the author.
