# Build and layout report

Status: PASS — selective analytical/editorial integration, 2026-09-14.

## Outputs and typography

Main manuscript: 13 pages. Supplementary: 28 pages. Sources remain IEEEtran 10pt;
no font-size, margin, or line-spacing compression was used to hold the main page count.
Repeated contribution/discussion/conclusion prose was tightened instead.
Both PDFs were compiled three times with pdfLaTeX and copied from build/ to the package root.

## Executed checks

- Existing candidate validator: 84/84 PASS.
- Integration validator: 21/21 PASS.
- Analytical arithmetic/enumeration: 13/13 groups PASS, 6555 cases.
- Frozen baseline evidence/table/protocol/reference files: 54/54 SHA-256 matches.
- Undefined citations or references: 0; fatal LaTeX errors: 0.
- Overfull hboxes and vboxes: 0 in both final logs.
- All 7 main-paper figures and 8 tables have body-text references.

Non-fatal log notices include the existing italic-small-caps font-shape fallback,
underfull typography notices, and supplementary math in PDF bookmarks. These are
not unresolved citations or failed equations. Logs are included rather than described
as warning-free.

## Visual inspection

All 13 + 28 pages were rendered at 144 dpi. Page-level contact sheets were reviewed;
new analytical pages and changed figure labels were also inspected at full-page scale.
No clipping, overlap or missing figures was observed after the label repairs. Unchanged
long-form evidence tables remain in the original landscape layout and font sizes.
Figures 1 and 5 (file fig4) use the incoming corrected labels with identical vector
geometry. Figure 6 was changed only within its clipped axis-label text block; all
non-label content-stream bytes and off-label raster pixels were checked unchanged.

## Scope

This build is not a rerun of either hardware campaign. Historical raw-reconstruction
findings and PASS_WITH_ISSUES remain as preserved baseline evidence. This pass checks
source integration, supplied numerical gates, algebraic examples, layout, and artifact
integrity. Prior baseline reports are retained under audit_history/ for comparison.

## Clean-package reproduction

A clean extraction was checked against the delivery checksum manifest before rebuilding.
Both sources rebuilt from that extraction; the three validation suites passed again,
and all rebuilt PDF pages matched the delivered renderings. See CLEAN_REBUILD_REPORT.md.
