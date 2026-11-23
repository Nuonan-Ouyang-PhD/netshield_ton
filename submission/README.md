# NetShield ToN Submission Package

This package contains the manuscript, supplementary material, figures, tables,
reference audit, claim audit, build instructions, and integrity checks for the
NetShield submission.

## Primary files

- `netshield_manuscript.tex` and `netshield_manuscript.pdf`
- `netshield_supplementary.tex` and `netshield_supplementary.pdf`
- `cover_letter.md`
- `OVERLEAF.md`
- `figures/`
- `tables/`
- `audit/REFERENCE_AUDIT.md`
- `audit/CLAIM_AUDIT.md`
- `audit/CODE_EVIDENCE_ALIGNMENT.md`
- `audit/METHODOLOGY_VALIDATION_REPORT.md`
- `audit/PDF_BUILD_METADATA.json` and `audit/PDF_BUILD_REPORT.md`
- `audit/SUBMISSION_FINALIZATION.md` and `audit/FINAL_CHECKS.json`
- `audit/CONTENT_CLOSEOUT.md` and `audit/CONTENT_CLOSEOUT_CHECKS.json`
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

The current manuscript has 14 pages and the supplementary material has 36 pages.
The content closeout aligns historical status, scenario labels, padded payloads,
confusion counts and timing/byte-accounting scope with the completed study.
Results Section V-C now presents the completed backlog-aware physical comparison.
The separate allocator and shared-stage studies contain 8 and 36 formal physical
arms, respectively. The calibrated controller's all-reject result and the separately verified CICIoMT2024 content cohort are explicitly reported.

The current methodology report supersedes historical validation claims for
earlier deliveries. Software upload completion and hardware core-result return
have separate definitions. The supplement includes allocator sensitivity,
shared-service counterexamples, a file-prefix content diagnostic and the new
physical comparisons. The held-out content and matched Wi-Fi results use 72 windows from three test captures.

The complete package and a standalone Overleaf source ZIP are available under
the repository's `review_package/` directory. See
[`SUBMISSION_GUIDE.md`](../SUBMISSION_GUIDE.md) for the submission file map.
