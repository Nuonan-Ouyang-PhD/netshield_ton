# IEEE Transactions on Networking — V4.4 Submission Readiness

## Current manuscript status

- Journal: **IEEE Transactions on Networking**.
- Format: IEEEtran, 10-point, two-column, single-spaced.
- Main manuscript length: **10 pages** including references.
- Main empirical results are frozen and provenance-audited.
- Dataset wording is **CICIoT2023-derived feature-vector replay**; “ToN” is used only for the target journal context, not as a dataset identity.
- Architecture figure, ten-action lattice, shared-bottleneck model, joint pre-admission semantics, finite-admission proposition, per-window procedure, and mechanism-isolating discussion are included.
- A 3-page supplementary PDF contains all 75 frozen contrasts, action consistency, capacity-specific diagnostics, the unique deadline miss, and artifact identity.

## Human confirmations locked

- Author order: **Nuonan Ouyang → Adrian Shatte → Zhigang Lu → Chao Chen → Wei Xiang**.
- Nuonan Ouyang remains the corresponding author.
- N. Ouyang and A. Shatte remain affiliated with James Cook University as printed in the manuscript.
- Corresponding-author e-mail remains `nuonan.ouyang@my.jcu.edu.au`.
- The NetShield empirical manuscript itself has **not been previously published** and has no prior NetShield conference/journal/public-preprint version.

## Related prior work — disclosed

The same authors published the ACISP 2026 SoK **“Telemetry-Aware Runtime Assurance for Always-On On-device Intrusion Detection”** (DOI: 10.1007/978-981-92-3018-1_7). Because it is topically related, V4.2 cites it in Related Work and the cover letter supplies a difference statement. The SoK is a literature systematization/design synthesis and does not contain the NetShield shared-bottleneck mechanisms or S01–S12 empirical results.

## Submission-side files prepared

- `netshield_ton_full_manuscript_v4_4.pdf` — main manuscript.
- `netshield_ton_supplementary_v4.pdf` — reviewer-facing supplementary statistics/provenance.
- `COVER_LETTER_FINAL.md` — final cover-letter text with related-work disclosure.
- `AUTHOR_METADATA_CONFIRMED.md` — locked author metadata.
- `ORIGINALITY_AND_PRIOR_WORK_DISCLOSURE.md` — originality and ACISP difference statement.
- `MANUSCRIPT_NUMERIC_AND_SEMANTIC_AUDIT.md` — manuscript claim audit.

## Submission declarations confirmed by corresponding author

Confirmed on 5 Sep 2026:

- The NetShield manuscript is **not concurrently submitted** to any other journal or conference.
- The other authors **agree to this ToN submission**.

## Remaining portal-only checks

These do **not** require new experiments or manuscript rewriting:

1. Each author completes/links the ORCID workflow requested by the submission system, if not already linked.
2. Re-enter/affirm the already-confirmed declarations if the portal presents them as mandatory checkboxes.
3. Select publication route/options in the IEEE workflow when prompted.

## Experimental status

- No additional experiment is required for the claims currently made in the manuscript.
- A future shield-intervention stress campaign could support a stronger shield-efficacy claim, but the current paper deliberately claims non-interference under the evaluated feasible envelope; therefore such a campaign is not a prerequisite for the present submission.


## V4.3 reviewer-preemption revision

- The manuscript now distinguishes the frozen campaign labels `independent-DPP`/`central-DPP`/`shielded-DPP` from a claim of a full Lyapunov optimizer. The deployed selector is described as a finite-action queue-penalized DPP-style score.
- Central coordination is described as deterministic monotone pre-admission/degradation under the shared cap, not as a globally solved joint argmax.
- The 14.1% D-vs-E/F generated-payload difference is explicitly labelled descriptive aggregate accounting rather than a prespecified inferential test.
- The detector pool is explicitly outside the novelty claim; perfect F1 for several policies is scoped to the frozen CICIoT2023-derived replay.
- The previously open reproducibility field is now closed: the three formal S01--S12 low/mid/high configuration files have been supplied and independently inspected; all set `dpp_v = 1.0`. The V4.4 manuscript binds this value explicitly in the implemented queue-aware score, and the three JSON files are included in the source bundle.
