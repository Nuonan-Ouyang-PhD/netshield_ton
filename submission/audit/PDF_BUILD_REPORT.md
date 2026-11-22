# PDF build and visual verification

The subset-overlap update uses pdfTeX 1.40.29 (TeX Live 2026), three
passes per document. The main and supplementary PDFs have 14 and 33 pages.
Current source and PDF digests are in PDF_BUILD_METADATA.json. Both final
logs passed the build checks for unresolved references and overfull boxes.

## Previous build: follow-up wording alignment, 2026-11-22

These are the current outputs of the actual three-pass rebuild after aligning
the manuscript's provenance and content-diagnostic descriptions with the later
local follow-up. The build used `scripts/build_submission.sh`; its fresh logs
identify `pdfTeX 3.141592653-2.6-1.40.26 (TeX Live 2025/dev/Debian)`.

| Document | Pages | PDF SHA-256 |
|---|---:|---|
| Main manuscript | 14 | `3f3c69f7ed27247bda2c7d03a5c6f347d463a231d209c7fa1f3c3877b7551fc3` |
| Supplementary material | 33 | `9782d594d00f2ec428015ddfa38206c45366fc0fffaf14f202f99f083cf93834` |

### Actual build and input verification

Both repository PDFs are byte-identical to the fresh build outputs. The
repository [PDF_BUILD_METADATA.json](PDF_BUILD_METADATA.json) is also
byte-identical to that build's metadata. The current source hashes are
`caabe1f4fb7d994ffac29c4c7cd725f4228c9842d75e052827b0fae54c2da5e4`
(main) and
`6ada3d4ba81e05a496e91eefb52363607a0d3f47ec377d427c2ef1d6f0875580`
(supplement).

The verification read both fresh `.fls` recorder files, both final compiler
logs, and all six pass-output files. The recorder-derived sets of 12 main and
13 supplementary repository inputs and every input hash match the metadata
and current files. The actual IEEEtran class loaded by the compiler has
SHA-256 `da751920a317ed318b7b5cd7fa585a6cc7d28502d457856382e9be24b10a3bd7`.
Each of the three passes per document completed successfully. Shell escape
was disabled. Both final logs contain zero fatal errors, missing-character
messages, overfull boxes, or unresolved references/citations. The retained
nonfatal font-shape, bookmark, float and shell-escape notices are recorded in
the metadata; the zero-overfull result is not a claim that every warning was
removed.

### Visual verification of the current outputs

All 47 pages of the wording-alignment candidate were rendered with Poppler at
150 dpi and reviewed in six contact sheets. Main pages 12, 13 and 14 and
supplementary pages 29 and 33 were additionally opened at full resolution. This
enlarged review covers the revised provenance and common-consumer wording, the
fairness and content-value qualifications, the exact-overlap table and its
Section XXVII cross-reference, the local follow-up results, and all 35
bibliography entries.

The final rebuild moved the manual bibliography split from reference 17 to
reference 15. All 47 final pages were rendered again at the same resolution;
46 were pixel-identical to the reviewed candidate, and only main page 14
changed. That final page was reopened at full resolution. Its column-bottom
difference decreased from approximately 125.53 pt to 37.21 pt (final bottoms
704.32 pt and 667.11 pt), with all references complete and inside the page.
Thus the unchanged pages retain the actual review above, and the changed
page has a fresh visual check. No clipping, overlapping text, cropped table,
missing glyph, or broken reference flow was observed. Fresh rotation-aware
checks found zero content blocks outside any of the 47 final page boundaries.

The current verification concerns document compilation and presentation. It
does not constitute a new hardware experiment, detector-efficacy result, or
independent reopening of private raw records. The two earlier reviews below
are retained with their own artifact identities and do not substitute for this
fresh build and visual check.

## Historical follow-up artifact review: dc5269c

The review on 2026-11-22 inspected the artifacts at
`dc5269c4864e2c4416d6ce6d8390d741bbaad20b`:

| Document | Pages | PDF SHA-256 |
|---|---:|---|
| Main manuscript | 14 | `e27bd98ebae8b795202cc671825aeca0c478384c6b753700d3db11a920cd6c85` |
| Supplementary material | 33 | `1f9cf1114ac12cfdc5e5bc9e5d5120d426ba1de982b4b6f0ad96a278b7aaba2d` |

The supplied `netshield_manuscript(1).pdf` and
`netshield_supplementary(1).pdf` were byte-identical to the repository PDFs at
that revision, rather than the current rebuilt outputs above. The source and
output hashes in the metadata committed at `dc5269c`, including all 12 main and
13 supplementary `repository_input_sha256` entries, were independently checked
against that revision's files and matched.

### Build declaration and review scope

The build metadata supplied in that revision reports TeX Live 2026,
`pdfTeX 3.141592653-2.6-1.40.29`, three passes per document, shell escape
disabled, zero overfull boxes and zero unresolved references. Both PDFs report
producer `pdfTeX-1.40.29`, consistent with that engine version. This review
checked those artifact identities and rendered outputs; it did not rerun TeX or
revalidate fresh compiler logs or `.fls` recorder files. Matching the recorded
input hashes establishes file identity, without independently proving which
files the follow-up compiler opened.

### Visual verification of these PDFs

All 47 pages were freshly rendered with Poppler at 150 dpi and reviewed in
six contact sheets. Manuscript pages 12, 13 and 14 and supplementary page 33
were additionally opened at full resolution. The new main-text diagnostic
counts span pages 12–13; the supplemental follow-up is on page 33. No clipping,
overlap, cropped result text or bibliography-flow defect was observed.
Rotation-aware bounds checks found zero content blocks outside the page.

A same-resolution raster comparison with the PDFs preserved at `b0ec63b`
found 35 changed pages and 12 identical pages. All 14 manuscript pages changed;
the unchanged supplementary pages were 13–24. The historical 46-of-47
comparison below therefore does not describe these follow-up PDFs.

## Historical integration build and QA: b0ec63b

The remainder of this section records the earlier integration, before the
follow-up additions and the TeX Live 2026 build. Its PDF hashes were
`6eab6c76e6f87fbc5f3efc1686117539ffc1cef60089e13ab06b59d697b43392`
(main) and
`2519d85745b00616bed7907a43caaf5f933312047c42bcbfae03915eae6a1e83`
(supplement). Both source documents at that revision were rebuilt with the
genuine IEEEtran class. The environment, log findings and visual checks below
apply to those historical artifacts.

### Historical build results

| Document | Pages | pdfLaTeX passes | Overfull boxes | Unresolved references/citations |
|---|---:|---:|---:|---:|
| Main manuscript | 14 | 3 | 0 | 0 |
| Supplementary material | 33 | 3 | 0 | 0 |

The fresh build used `scripts/build_submission.sh`, with shell escape disabled.
The script checks both final logs before replacing either PDF. The metadata
contains each PDF hash, the main source hash, and the hashes of repository
inputs actually loaded according to the `.fls` recorder files. There were no
fatal TeX errors or missing-character messages.

### Historical TeX environment

- Engine: `pdfTeX 3.141592653-2.6-1.40.26 (TeX Live 2025/dev/Debian)`.
- Class: genuine IEEEtran v1.8b, downloaded from the official
  [CTAN IEEEtran directory](https://tug.ctan.org/macros/latex/contrib/IEEEtran/IEEEtran.cls).
- IEEEtran SHA-256: `da751920a317ed318b7b5cd7fa585a6cc7d28502d457856382e9be24b10a3bd7`.
- The container already contained standard TeX packages and Type 1 fonts, but
  its generated format/font-map/filename-database paths were missing. A local
  TEXMF search path and locally regenerated pdfLaTeX format and font maps used
  those actual installed files. Standard English hyphenation was loaded.
- No class was emulated or modified. No external font or class files were added
  to the repository. A normal complete TeX Live installation uses the same build
  script directly; see [BUILD_INSTRUCTIONS.md](../BUILD_INSTRUCTIONS.md).

### Historical visual verification

All **47 pages of that integration build** were rendered with Poppler at 150 dpi. Contact sheets
for every page were inspected, with enlarged inspection of manuscript pages
7, 10–14 and supplementary pages 29, 30, 32 and 33. This covers the integrated
runtime and content qualifications, the new exact-overlap and formal-record
tables, the experiment protocols, and the bibliography. Rotation-aware bounds
checks found **zero content blocks extending beyond a page boundary**.

That integration source used native IEEEtran bibliography splitting. The integration
build initially left unequal bibliography columns; moving the explicit split
from reference 19 to reference 17 reduced the final column-bottom difference
from approximately 140 pt to 31.23 pt. The rebuilt page was inspected again.
A full raster comparison with the already reviewed integration candidate found
46 of 47 pages pixel-identical; only manuscript page 14 changed. No clipping,
overlapping content, crowded audit table, or missing glyph was observed in the
integration renderings.

### Historical font findings and evidence boundaries

The manuscript text uses the genuine installed URW/Times and Computer
Modern/AMS fonts. Existing imported figure PDFs retain their original choices:
there are eight unembedded Helvetica/Helvetica-Bold font objects and three
Type 3 font objects in the main PDF, and two unembedded standard-font objects
in the supplement. These originate in historical figure assets; the build
preserves those files and makes **no PDF/A or universal-font-embedding claim**.

The integration logs also retained nonfatal inherited font-shape substitutions for
italic small caps, underfull-box notices, and supplementary bookmark/float
notices. Shell-escape warnings are expected because no automatic EPS conversion
is needed. These are distinct from the zero overfull-box and zero unresolved
citation/reference checks above.

This report distinguishes declared build metadata, file-identity checks and
visual inspection. This PDF review does not
claim a hardware rerun, a new detector experiment, or a re-audit of private raw
hardware data. The integration of the supplied local audit and its evidence
boundaries is recorded in
[FORMAL_RECORD_INTEGRATION.md](FORMAL_RECORD_INTEGRATION.md).
