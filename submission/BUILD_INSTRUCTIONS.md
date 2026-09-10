# Build Instructions

The package is self-contained apart from a TeX engine with the standard
IEEEtran dependencies.

From the package directory, compile with Tectonic:

```sh
tectonic -X compile netshield_manuscript.tex
tectonic -X compile netshield_supplementary.tex
```

Equivalent XeLaTeX-compatible workflows may also be used. The checked build
produces the manuscript and supplementary PDFs from the clean submission
sources.

Integrity and semantic checks:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 validate_submission.py
```
