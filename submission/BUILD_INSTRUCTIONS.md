# Building and checking the current ToN submission

Run commands from the **repository root**, not from an older standalone ZIP.
The current build command is `scripts/build_submission.sh`. Historical references
to `build/rebuild.sh`, `build/validate_candidate.py`, and
`BASELINE_FROZEN_SHA256SUMS.txt` describe an earlier standalone package and are not
commands supplied by this checkout.

## Requirements

- Python 3.10+ for repository checks and build metadata.
- A working pdfLaTeX installation with the **genuine IEEEtran class** and the
  standard packages named in the two `.tex` preambles.
- Times/URW and Computer Modern/AMS font metrics, outlines, and generated font maps.
- Poppler (`pdfinfo`, `pdffonts`, `pdftoppm`) for optional font and visual inspection.

A typical complete TeX Live installation works. On Debian/Ubuntu, the relevant
package groups are `texlive-latex-base`, `texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-fonts-recommended`, and `texlive-publishers`.
Install these through the operating system's package manager, or install the
equivalent components through your existing TeX distribution.

Check the actual installation before building:

```bash
kpsewhich IEEEtran.cls
kpsewhich pdflatex.fmt
kpsewhich pdftex.map
kpsewhich ptmr7t.tfm
```

Each command must return a real file. If package files exist but these checks
return nothing, repair the distribution's filename database, formats, and font
maps; merely placing a renamed or emulated class beside the manuscript is not a
valid repair. IEEEtran is available from its official
[CTAN package](https://ctan.org/pkg/ieeetran).

## Verify the delivered package

Before rebuilding a supplied revision, run:

```bash
python3 submission/validate_submission.py
python3 scripts/verify_submission.py
python3 scripts/verify_campaign_audit.py
python3 scripts/verify_methodology.py
```

These checks validate the supplied source/evidence package and its frozen
provenance. They do not execute Raspberry Pi experiments. Follow the repository's
`REPRODUCIBILITY.md` for the separate corrected software experiments and raw-ledger
audit workflow.

## Build current source

```bash
bash scripts/build_submission.sh
```

The script creates a fresh temporary build directory, makes three pdfLaTeX
passes per document, and stops if either final log contains an overfull box,
missing character, or unresolved reference/citation. Only after **both** documents
pass does it replace:

- `submission/netshield_manuscript.pdf`
- `submission/netshield_supplementary.pdf`

Compilation uses `-no-shell-escape`. All supplied figures are already PDFs, so
automatic EPS conversion is unnecessary. Logs, `.fls` input records, and
`build_metadata.json` remain in the printed build directory. To choose its parent:

```bash
TON_PDF_BUILD_ROOT=/absolute/path/to/builds bash scripts/build_submission.sh
```

The metadata records the real engine version, IEEEtran class SHA-256, source/PDF
hashes, page counts, and nonfatal warning lines. It reports only a successful
document build; it is not evidence of a hardware run or a raw-data audit.

PDF metadata, engine versions, fonts, and line breaking can change output hashes
between installations. Do not regenerate frozen scientific evidence manifests
simply because a freshly compiled PDF differs. Supplied binary checksums apply
to the delivered binaries; current source/PDF correspondence is recorded by the
new build metadata.

When publishing a rebuilt candidate, copy that fresh build directory's
`build_metadata.json` to `submission/audit/PDF_BUILD_METADATA.json`, update
the existing entries in `submission/SHA256SUMS.txt` from the actual current
files, and run `scripts/verify_methodology_revision.py` as well. Retain the
fresh logs and visual review. Do not leave a new PDF paired with a previous
build's metadata.

## Inspect the result

```bash
pdfinfo submission/netshield_manuscript.pdf
pdfinfo submission/netshield_supplementary.pdf
pdffonts submission/netshield_manuscript.pdf
pdffonts submission/netshield_supplementary.pdf
```

Render and inspect pages containing the introduction, equations, figures,
longtables, references, and newly added supplementary sections. A successful
compiler exit is insufficient for visual quality assurance.

Imported historical figure PDFs retain their original font encodings and
embedding choices, including some standard Helvetica and Type 3 fonts.
The build does not silently rewrite these frozen scientific assets and does not
claim PDF/A or universal font embedding. Any later production conversion should
retain the source figures and independently verify the converted rendering.
