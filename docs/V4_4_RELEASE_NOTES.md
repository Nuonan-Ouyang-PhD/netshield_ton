# V4.4 release notes — parameter-locked submission candidate

- Independently parsed the three formal low/mid/high S01--S12 configuration JSON files supplied on 5 Sep 2026.
- Bound the implemented queue-aware selector coefficient to `v_DPP = 1.0` in the main manuscript; all three configs use the same value.
- Added the three formal config JSON files to both `source/configs/` and `frozen_reference/configs/`.
- Added `FORMAL_CONFIG_PARAMETER_AUDIT.md` with exact configuration SHA-256 values and common frozen fields.
- Closed the final V4.3 reproducibility TODO in `SUBMISSION_READINESS.md`.
- Normalized the displayed system/title name to **NetShield** so the manuscript title matches the final cover letter.
- Recompiled with IEEEtran: 10 pages, no undefined references/citations and no overfull boxes. Only non-blocking underfull-box notices remain.
- Rendered and visually inspected the 10-page PDF after the edit.
- No frozen S01--S12 empirical result, statistical contrast, table value, or figure was changed.
