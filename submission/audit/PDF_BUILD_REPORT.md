# PDF build and visual verification

The follow-up PDFs were rebuilt with TeX Live 2026, three passes each.
The current metadata records 14 and 33 pages, zero overfull boxes and
zero unresolved references. The pages containing the follow-up counts
(main p. 13 and supplement p. 33) were rendered and inspected.

## Previous integration build

Both current source documents were rebuilt successfully with the genuine
IEEEtran class. The current PDFs in `submission/` correspond to the source hashes
recorded in [PDF_BUILD_METADATA.json](PDF_BUILD_METADATA.json).

## Build results

| Document | Pages | pdfLaTeX passes | Overfull boxes | Unresolved references/citations |
|---|---:|---:|---:|---:|
| Main manuscript | 14 | 3 | 0 | 0 |
| Supplementary material | 33 | 3 | 0 | 0 |

The fresh build used `scripts/build_submission.sh`, with shell escape disabled.
The script checks both final logs before replacing either PDF. The metadata
contains each PDF hash, the main source hash, and the hashes of repository
inputs actually loaded according to the `.fls` recorder files. There were no
fatal TeX errors or missing-character messages.

## Actual TeX environment

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

## Visual verification

All **47 final pages** were rendered with Poppler at 150 dpi. Contact sheets
for every page were inspected, with enlarged inspection of manuscript pages
7, 10–14 and supplementary pages 29, 30, 32 and 33. This covers the integrated
runtime and content qualifications, the new exact-overlap and formal-record
tables, the experiment protocols, and the bibliography. Rotation-aware bounds
checks found **zero content blocks extending beyond a page boundary**.

The final source uses native IEEEtran bibliography splitting. The integration
build initially left unequal bibliography columns; moving the explicit split
from reference 19 to reference 17 reduced the final column-bottom difference
from approximately 140 pt to 31.23 pt. The rebuilt page was inspected again.
A full raster comparison with the already reviewed integration candidate found
46 of 47 pages pixel-identical; only manuscript page 14 changed. No clipping,
overlapping content, crowded audit table, or missing glyph was observed in the
final renderings.

## Preserved font and evidence boundaries

The manuscript text uses the genuine installed URW/Times and Computer
Modern/AMS fonts. Existing imported figure PDFs retain their original choices:
there are eight unembedded Helvetica/Helvetica-Bold font objects and three
Type 3 font objects in the main PDF, and two unembedded standard-font objects
in the supplement. These originate in historical figure assets; the build
preserves those files and makes **no PDF/A or universal-font-embedding claim**.

The final logs also retain nonfatal inherited font-shape substitutions for
italic small caps, underfull-box notices, and supplementary bookmark/float
notices. Shell-escape warnings are expected because no automatic EPS conversion
is needed. These are distinct from the zero overfull-box and zero unresolved
citation/reference checks above.

This report covers source-to-PDF construction and visual checks. It does not
claim a hardware rerun, a new detector experiment, or a re-audit of private raw
hardware data. The integration of the supplied local audit and its evidence
boundaries is recorded in
[FORMAL_RECORD_INTEGRATION.md](FORMAL_RECORD_INTEGRATION.md).
