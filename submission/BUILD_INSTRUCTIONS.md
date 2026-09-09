# Build Instructions

The package is self-contained apart from a TeX engine with the standard
IEEEtran dependencies.

From the package directory, compile with Tectonic:

```sh
tectonic -X compile manuscript.tex
tectonic -X compile supplementary.tex
```

Equivalent XeLaTeX-compatible workflows may also be used. The checked build
produces a 12-page `manuscript.pdf` and a 24-page `supplementary.pdf`.

Integrity and semantic checks:

```sh
shasum -a 256 -c SHA256SUMS.txt
python3 validate_submission.py
```
