# PDF build and visual verification

Both current source documents were rebuilt successfully with the genuine
IEEEtran class. The current PDFs in `submission/` correspond to the source hashes
recorded in [PDF_BUILD_METADATA.json](PDF_BUILD_METADATA.json).

## Build results

| Document | Pages | pdfLaTeX passes | Overfull boxes | Unresolved references/citations |
|---|---:|---:|---:|---:|
| Main manuscript | 14 | 3 | 0 | 0 |
| Supplementary material | 32 | 3 | 0 | 0 |

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

All **46 final pages** were rendered. Contact sheets for every page were
inspected, with individual enlarged inspection of the first manuscript page,
its hardware/mechanism figure page, the bibliography, and the new supplementary
counterexample/protocol pages. Rotation-aware text bounds were checked on all
pages: **zero text lines extended beyond a page boundary**.

Two issues observed during the first build were corrected in source and then
rebuilt: a long slash-separated phrase overflowed a supplementary paragraph;
and the generic balancing package produced a 1.10-pt last-page vertical
box overflow. The final source uses breakable prose and native IEEEtran
bibliography splitting. Only main page 14 and supplementary pages 31–32
changed in the final raster comparison with the already reviewed draft; all
three were inspected again. No clipping, overlapping content, or missing glyphs
was observed in the reviewed final renderings.

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
hardware data. Those evidence boundaries are recorded separately in the
methodology validation report.
