# NetShield ToN Submission Package

This package contains the manuscript, supplementary material, figures, tables,
reference audit, claim audit, build instructions, and integrity checks for the
NetShield submission.

## Primary files

- `netshield_manuscript.tex` and `netshield_manuscript.pdf`
- `netshield_supplementary.tex` and `netshield_supplementary.pdf`
- `cover_letter.md`
- `figures/`
- `tables/`
- `audit/REFERENCE_AUDIT.md`
- `audit/CLAIM_AUDIT.md`
- `audit/CODE_EVIDENCE_ALIGNMENT.md`
- `audit/METHODOLOGY_VALIDATION_REPORT.md`
- `audit/PDF_BUILD_METADATA.json` and `audit/PDF_BUILD_REPORT.md`
- `BUILD_INSTRUCTIONS.md`
- `VALIDATION_REPORT.md`
- `validate_submission.py`
- `SHA256SUMS.txt`

Dataset and reproducibility instructions are maintained at the repository
level in [`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md).
They distinguish the public CICIoT2023 source and offline analyses from the
controlled raw evidence of the 216-arm physical campaign. The path-free CRFA
hardware result layer is published separately under
`../supporting_material/crfa_hardware/`; private raw arms are not included.

The current manuscript has 14 pages and the supplementary material has 35 pages. The current methodology report supersedes the historical validation
claims for the earlier delivery. Software upload completion and hardware
core-result return now have explicit separate definitions; the supplement
includes corrected allocator sensitivity, shared-service counterexamples,
and a file-prefix content diagnostic. Independent held-out efficacy is pending.
