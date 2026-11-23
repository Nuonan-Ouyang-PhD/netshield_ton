# Historical archive checksum reconciliation

Date: 23 November 2026 (Australia/Melbourne).

The final GitHub integrity run identified one mismatch in the historical
`supporting_material/archive/v4_4/docs/MANIFEST_SHA256.txt`: the entry for
`frozen_reference/PROVENANCE.md`. All other 33 listed files matched.

## Verified cause

Commit `93400678f9878fca527d255bcfbfa72054978c02` refreshed the archive manifest
against the then-current provenance document. Commit
`9bcf9115398b5b57c557bfa5e26006bb83e6fb0d` subsequently changed only line 7 of
that document, replacing an absolute local checkout path with a controlled
local-worktree description. It did not update the corresponding manifest entry.
The redacted document is unchanged from that commit through the scientific
results revision `75d529c` and the first final-package commit `a18e1d8`.

| Document state | Bytes | SHA-256 |
|---|---:|---|
| Before the documented path redaction | 5,802 | `a87128fe1990320ab1508396dd797219bb3f938232dcac18b3db5a5bb9240495` |
| Existing public, redacted document | 5,773 | `6c2d92c9d1964abc32b6fe805639efa50b0dea53d8e0f63f30c314455e5b01e2` |

## Correction

The public redaction is preserved. Only its checksum line in the historical
archive manifest is updated to the hash of the already-published redacted
document. The provenance document itself, scientific data, figures, tables,
paper results and validation workflow are unchanged. The historical manifest
and its earlier hash remain recoverable from Git history.

Neither this provenance document nor its archive manifest belongs to the
separately frozen 120-file scientific input set. That input set is verified
independently by `scripts/verify_methodology_revision.py`.

The original archive gate remains enabled: from
`supporting_material/archive/v4_4`, run
`sha256sum -c docs/MANIFEST_SHA256.txt` to verify every one of the 34 entries.
The executed result is included in `FINAL_CHECKS.json`.
