# Building and checking the 15 September 2026 revision

Requirements: pdfLaTeX with IEEEtran and the standard packages used by the sources;
Python 3.10+ with pandas and PyMuPDF. The inherited analytical checks use the Python
standard library. No network, Pi hardware, private disk path or dataset download is
required to compile or run the supplied checks.

From the package root, check the delivered files BEFORE rebuilding:

```bash
sha256sum -c SHA256SUMS.txt
bash build/rebuild.sh
```

On macOS, the first command can be `shasum -a 256 -c SHA256SUMS.txt`.
PDF metadata and LaTeX log timestamps may change on rebuilding. The immutable
scientific artifacts can be checked independently afterward:

```bash
shasum -a 256 -c BASELINE_FROZEN_SHA256SUMS.txt
```

`build/rebuild.sh` makes three pdfLaTeX passes per document, copies root PDFs, then
runs the inherited analytical checks, the maintained 84-check candidate validator,
and the new 40-check revision validator. See `build/EDITORIAL_VALIDATOR_CHANGES.diff`
for the small edits to the old validator (35 references; generalization scope now
located in Limitations; a stricter zero-overfull-vbox condition). All numerical gates
are unchanged. The old 13/28-page integration checker is historical and is not run.

Expected local result: main **14 pages**, supplement **29 pages**; abstract **229
whitespace-delimited words**, one paragraph; **35 references**. First 28 supplementary
pages are raster-identical to the supplied baseline in the tested environment.

`build/compact_cycle.py` is an optional regeneration tool for the short figure. It
reads the archived figure, selects eight rounds and verifies line geometry; it does
not execute a replay. Regeneration can change PDF metadata, so it is not run by the
normal rebuild. The normal validator checks the delivered figure geometry directly.

`SOURCE_CHANGES.diff` compares this revision with INTEGRATED_20260914. Files under
`audit_history/` describe prior deliveries; they are not current PASS reports. No
standalone font files or third-party publication PDFs are distributed.
