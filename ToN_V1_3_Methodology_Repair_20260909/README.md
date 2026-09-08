# ToN V1.3 Methodology Repair

This directory is a path-free review snapshot of the independent ToN /
NetShield methodology-repair analysis. It does not alter the formal V1.2
evidence, manuscript, Overleaf, or Raspberry Pi systems.

Run:

```bash
export TON_AUDIT_ROOT=/path/to/ToN_FullRaw_Audit_20260908
export TON_RUNTIME_ROOT=/path/to/NSF12_20260906_RC1/runtime
export TON_RAW_ZIP=/path/to/ToN_Raw_Sessions_12x_20260908_under512MB.zip
python3 ToN_V1_3_Methodology_Repair_20260909/run_methodology_repair.py \
  > ToN_V1_3_Methodology_Repair_20260909/run.log 2>&1
```

The analysis uses only Python's standard library. See `RUN_METADATA.json` for
the exact environment, inputs, seeds, commands, and source SHA-256 values.

Task A and the synchronized/coordinated parts of Task B replay the frozen
selector and capacity rules. The desynchronised baseline uses a documented
1 ms discrete-event time line with seed-fixed independent initial phases.
Task C alone reconstructs metrics directly from formal hardware timestamps.
Task D is an independent scaling simulation.

The committed tables preserve the canonical numeric values and source hashes.
Machine-local path prefixes were replaced with logical root tokens for private
review. See `GITHUB_PUBLICATION_NOTE.md` for the exact boundary.
