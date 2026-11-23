# Offline preparation verification

The complete machine-readable test receipt is
[`OFFLINE_VERIFICATION.json`](OFFLINE_VERIFICATION.json); scientific-stage
status is recorded separately in [`PREPARATION_STATUS.json`](PREPARATION_STATUS.json).

## Executed checks

| Check | Executed result |
|---|---|
| Read-only asset discovery | 5 tests passed: source is not executed; candidate findings are not deployment verdicts; secrets/symlinks/arbitrary CSV values are not exported; partial scans/hash limits are explicit; old output is not overwritten |
| Input identity freezing | 2 tests passed: stream-hash verification, changed/missing/extra inputs, duplicate identifiers, symlinks and overwrite rejection |
| Evidence-value scoring | 19 tests passed: exact matching and splits, artifact hashes, source-feature leakage, fixed labels/thresholds, missing/censoring/maturity, clock domains, inclusive deadlines, byte-cost unknowns, paired group weighting and synthetic-data separation |
| Hardware plan generation | 9 tests passed: supported designs, full/partial order balance, qualification artifacts, formal receipt bindings, fixed block rule, unaffected allocator skip and no-overwrite behavior |
| Frozen science/public reconstruction | Prior verifier passed: 120 frozen file hashes; 14 formal blocks; 21 labeled equations; unchanged abstract; 36 public selector configurations; 120 software runs; 10,620 CRFA service rounds/9,720 occurrences; source-matched manuscript and supplementary PDFs |

There are **35 new fixture tests**, not 35 experiments or physical sessions.
All fixture observations are generated temporarily and explicitly marked
synthetic. No new detector, private runtime, Wi-Fi or Raspberry Pi execution
was performed. The model/result/encoder execution adapter must be connected
to the actual authorized local artifacts by the next operator.

The available public checkout does not include the private frozen models,
full deployment runtime, raw feature captures or complete primary primitive
service logs. Their qualification remains a local task; read-only file
discovery cannot establish which private artifact ran in the historical
campaign. No synthetic evidence-value or physical-result table is supplied
as a substitute.

## Reproduce

```bash
python3 scripts/verify_experiment_extension.py --output /tmp/netshield_extension_verification_NEW.json
```

The output must be fresh. The verifier records source hashes before/after
the checks and keeps test results distinct from scientific execution status.
Its recorded elapsed seconds are tool wall times, not hardware profiling.
The current manuscript and supplementary PDFs retain the previously
validated source/output identities; no new empirical claim was inserted.

## Handoff

Follow [`CODEX_HANDOFF_CN.md`](CODEX_HANDOFF_CN.md) and
[`PROTOCOL.md`](PROTOCOL.md), then the exact study-specific schemas. The
next operator should continue through available real inputs and objective
qualification gates; a missing dependency blocks only its dependent stage,
not the independent work. Null or adverse findings remain valid outputs.
