# NetShield-IDS V4 — Numeric and Semantic Audit

**Overall status: PASS**

This audit is for the V4 manuscript only. Empirical values remain bound to the frozen REV2 analysis; the V4 changes are exposition, system semantics, algorithm presentation, and submission formatting—not re-analysis.

## Frozen baselines

- Statistical truth: `a24b909` / `v0.4.7-analysis-rev2-session-level`
- Paper-facing documentation: `92c3108` / `v0.4.7-analysis-rev2-doc-clean`
- Clean analysis package SHA-256: `561742f99e7b4d389fd2077cf6485c04c432468ce692ef8c54144525ecfd8092`

## Automated checks

| Check | Result | Evidence |
|---|---|---|
| C timely-F1/FPR | PASS | table1_method_overview.csv: C=0.9332/0.2845 |
| C/D MaxQ | PASS | table1_method_overview.csv: C=7.92 MiB; D=0.08 MiB |
| F deadline violation | PASS | table1_method_overview.csv: F=0.000103 |
| E/F MaxQ zero | PASS | table1_method_overview.csv |
| D full-run delivery ratio | PASS | table1_method_overview.csv: D=0.998 |
| C-F timely-F1 Holm result | PASS | table2_primary_contrasts.csv |
| C-F FPR Holm result | PASS | table2_primary_contrasts.csv |
| C-F E2E Holm result | PASS | table2_primary_contrasts.csv |
| E-F E2E null after Holm | PASS | table2_primary_contrasts.csv |
| Non-inferiority | PASS | non_inferiority.json |
| E/F action identity | PASS | ef_action_consistency_results.json |
| D/F action difference | PASS | ef_action_consistency_results.json |
| Legacy simulated-result scan | PASS | No hits: clean |
| Dataset identity | PASS | Manuscript says CICIoT2023-derived feature-vector replay |
| Shared-service semantic statement | PASS | System model explicitly distinguishes queue-drain service from pre-admission |
| Shield claim boundary | PASS | Conclusion wording |
| F deadline miss disclosed | PASS | Results + discussion |
| Macro/micro distinction | PASS | Metrics + Table IV caption |

## V4 semantic correction relative to the earlier manuscript draft

The formal design is described as two distinct layers: **(1) common capped transport service** and **(2) optional joint pre-admission of newly generated evidence**. All six methods experience the common queue-drain service; E/F additionally reconcile simultaneous requests before queue insertion. A–D therefore remain valid uncoordinated/request-generation baselines without implying that they receive a physically different link.

This wording is consistent with the rc4 engineering audit that introduced a unified shared-service layer before the paper-eligible S01–S12 campaign. It also explains the observed hierarchy without over-attributing gains to the shield: C→D primarily tests queue awareness; D→E/F adds joint admission; E→F is an observed non-interference contrast.

## Frozen action semantics used in V4

The system section now uses the frozen ten-action lattice (L/M/H × none/alert/summary plus H-FULL), with payloads 0/256/4096/8192/16384/131072 B and the frozen 0.8 detector + 0.2 evidence utility construction. The manuscript labels this utility as a pre-campaign scheduling score rather than a universal performance ranking.

## Build identity

- `netshield_ton_full_manuscript_v4.tex` SHA-256: `28b9c76e4a3d2daa66de2bf2e400bd27a99ab949ce8f5d8c70f390fc9042ebc7`
- `netshield_ton_full_manuscript_v4.pdf` SHA-256: `1b0bbb73e2a84e176fc9452d7b591c36af0d7afec498908b58401dde7d0e5ae2`
- PDF: IEEEtran 10-point, two-column, US Letter, 10 pages.
- LaTeX final build: no undefined references/citations, no overfull boxes, and no LaTeX warnings in the final log (ordinary underfull spacing notices excluded).
- Render verification: all 10 pages rendered at 200 dpi; no clipped text, overlapping content, black boxes, or broken glyphs observed.

## Claim boundary to preserve

**Do not strengthen F-vs-E into a shield-efficacy or superiority claim.** In S01–S12, E and F choose the same action in all 9,720 measured windows. The data support architectural separation and non-interference under the tested feasible envelope. A future paper-eligible stress campaign would be needed to estimate intervention benefit.


## V4.4 formal-config closure

The formal low/mid/high JSON files supplied on 5 Sep 2026 were independently parsed. All three set `dpp_v = 1.0`; this value is now explicit in Eq. (4). Exact file hashes and common configuration fields are recorded in `FORMAL_CONFIG_PARAMETER_AUDIT.md`. No frozen result was modified.
