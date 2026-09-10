# GitHub publication boundary

This directory is a path-free review export of the canonical local package
`ToN_V1_3_Methodology_Repair_20260909`.

- Canonical ZIP SHA-256: `cc9dcdd708db60ed3ab40f74d79d70d869e23795cbcf1304f4319a98a30fa66f`
- The scientific values, retained failures, seeds, source SHA-256 identities,
  reports, and row sets are unchanged. CSV line endings are normalized from
  CRLF to LF for repository consistency.
- Machine-local path prefixes in `RUN_METADATA.json` and
  `NOMINAL_DEADLINE_RESULTS.csv` are represented by `<TON_WORKSPACE>`,
  `<AUDIT_ROOT>`, and `<RUNTIME_ROOT>`.
- The committed script accepts the corresponding local evidence locations via
  `TON_AUDIT_ROOT`, `TON_RUNTIME_ROOT`, and `TON_RAW_ZIP`; this path-only change
  and explicit LF output setting mean its checkout hash intentionally differs
  from the canonical analysis script hash recorded in `RUN_METADATA.json`.
- `scope_guards.github_modified = false` records the state when the canonical
  analysis was executed. This later review export does not alter that run.

The raw archive, raw event ledgers, model artifacts, machine identities, and
full local evidence tree remain outside Git.
