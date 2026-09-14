# Building and checking this package

Requirements: a LaTeX installation with IEEEtran and the standard packages used by
the sources, and Python 3.10+. The submission validator uses only the Python
standard library. No network, hardware, private paths or third-party dataset
downloads are needed for the package checks.

From the package directory:

```bash
shasum -a 256 -c SHA256SUMS.txt
tectonic -X compile netshield_manuscript.tex
tectonic -X compile netshield_supplementary.tex
python3 validate_submission.py
```

On macOS, `shasum -a 256 -c SHA256SUMS.txt` may be used for the first command.
Run the delivery-manifest check BEFORE rebuilding: PDF metadata and compiler logs may
change on another system. This does not imply an evidence change. To check frozen
scientific inputs independently after a rebuild:

```bash
shasum -a 256 -c BASELINE_FROZEN_SHA256SUMS.txt
```

The supplied PDFs are the paper-facing build outputs. Recompilation does not edit
the frozen evidence files or recompute any empirical statistics. The detailed
selective-integration checks and clean-build records are retained in the CRFA
supporting material and in the delivered audit reports.

`SOURCE_CHANGES.diff` is a review aid against the CRFA FINAL baseline, not required to
compile. No standalone font files are included or required.
