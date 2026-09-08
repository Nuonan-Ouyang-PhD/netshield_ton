# NetShield — Shared-Bottleneck Evidence Scheduling for Multi-Probe IoT Edge Intrusion Detection

Historical copy of the former **submission-frozen V4.4 manuscript package** for
IEEE Transactions on Networking (ToN).

> **Historical status:** V4.4 predates formal protocol
> `NSF12_20260906_RC1`. Its S01–S12 values are not RC1 results and this package
> is not the current submission candidate. See [`STATUS.md`](STATUS.md).

> **Visibility policy:** This repository must remain **private during co-author
> review and submission**. A public artifact release can be prepared separately
> after the submission policy decision. Do not make it public before the paper
> is accepted (or a preprint policy decision is made by all authors).

## Contents

| Path | Description |
|---|---|
| `netshield_ton_full_manuscript_v4_4.pdf` / `.tex` | Main manuscript, V4.4, 10 pages, parameter-locked |
| `netshield_ton_supplementary_v4.pdf` | Reviewer-facing supplementary (75 frozen contrasts, action consistency, diagnostics) |
| `source/` | LaTeX source: figures, configs, `references_v4.bib`, supplementary `.tex` |
| `frozen_reference/` | Frozen evidence chain: tables, `NUMBER_PROVENANCE.md`, `PROVENANCE.md`, `STATISTICS_FACTS.md`, formal config JSONs with SHA-256 |
| `audit/` | Submission-side audits: config parameter audit, numeric/semantic audit, reviewer-attack report, originality & prior-work disclosure, cover letter, author metadata, submission readiness |
| `V4_4_RELEASE_NOTES.md` | Original V4.4 release notes |
| `docs/` | Original bundle README and `MANIFEST_SHA256.txt` (integrity manifest, `shasum -a 256 -c` verified) |

## Key frozen facts

- Formal campaign: S01–S12, Raspberry Pi fleet, three capacity budgets (low/mid/high)
- Selector parameter: `dpp_v = 1.0` in all three formal configurations (SHA-256 audited)
- Statistical truth baseline: `a24b909` / `v0.4.7-analysis-rev2-session-level`
- Paper-facing documentation baseline: `92c3108` / `v0.4.7-analysis-rev2-doc-clean`
- Dataset scope: CICIoT2023-derived feature-vector replay (not live packet capture)
- Concurrent submission: none

## Integrity

Every file in this directory except the manifest itself has a SHA-256 entry in
`docs/MANIFEST_SHA256.txt`. Verify with:

```bash
cd legacy/v4_4
shasum -a 256 -c docs/MANIFEST_SHA256.txt
```

The manifest paths are relative to this `legacy/v4_4/` directory.
