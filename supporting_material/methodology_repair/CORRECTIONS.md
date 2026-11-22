# Methodology corrections

The top-level CSVs, `RUN_METADATA.json`, `VALIDATION_REPORT.md`, `run.log`,
`README.md`, and `SHA256SUMS.txt` are **historical V1.3 artifacts**. Their
original bytes are retained. Their software column names containing
`core_result` refer to payload upload completion, not core-result arrival.
The historical 432 Task A rows are 36 deterministic configurations repeated
under 12 session/seed labels; the labels do not create independent runs.

The old public driver is retained byte-for-byte as
`legacy/run_methodology_repair_v1_3.py` (SHA-256
`6dc4608ba00ae27f9f13334371309eb49c945049b458d3cb922e1443e84fea3c`).
`scripts/verify_methodology.py` resolves the original manifest's driver entry
to that file. All other historical manifest entries still resolve to their
original paths. The old run metadata contains a separate original execution
source identity from before public path sanitization; neither source is
silently presented as the current implementation.

## Current driver

`run_methodology_repair.py` now imports without private files and uses
`simulation_primitives.py` for work-conserving integer allocation,
backlog-reserved admission, explicitly isolated latency prechecks, and a
shared inclusive elapsed-upload deadline predicate. Residual-byte priority
rotates by round (Task A) or tick (Task B).

Task A evaluates 36 configurations once. Task B retains distinct random
phase realizations where phases affect decisions; synchronized controls
remain deterministic conditional on their tie-breaking rules. Neither task
simulates core inference, wireless jitter, or result return. Task A uses a
round-end upload timestamp; Task B uses a 1-ms tick-end timestamp and an
application-byte bucket with intra-bucket credit. These resolutions and
service models are explicitly different.

Full private-input rerun, when the authorized inputs are available:

```bash
export TON_AUDIT_ROOT=/path/to/retained/audit
export TON_RUNTIME_ROOT=/path/to/retained/runtime
export TON_RAW_ZIP=/path/to/retained/raw.zip
export TON_OUTPUT_DIR=/path/to/new/corrected_results
export TON_OUTPUT_ZIP=/path/to/new/corrected_results.zip
python3 supporting_material/methodology_repair/run_methodology_repair.py
```

The output directory/ZIP must not already exist. The driver refuses to write
over frozen input locations. This complete private-input workflow was not
executed during the public correction.

## Public checks and separate new experiments

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_public_selector_audit.py
python3 supporting_material/contention_validation/run_contention_validation.py
python3 scripts/audit_service_ledgers.py \
  --software supporting_material/contention_validation/results \
  --crfa supporting_material/crfa_hardware
```

The public selector reconstruction uses the manuscript's rounded utility
and payload table; it does not substitute invented private detector times.
Its old-source reconstruction matches all 36 archived action/queue cases.
Corrected allocation changes 24 queue trajectories and 5 low-capacity action
mixes, demonstrating that small residual-byte errors can change closed-loop
selection. This evidence is reported separately from the frozen hardware.

The new contention experiment uses explicit assumed stage delays and a
different fixed-rate service proxy. Its independent ledger reconstruction
checks accounting and timestamps; it is not a physical Wi-Fi measurement.
See `../contention_validation/README.md` and
`../../submission/audit/CODE_EVIDENCE_ALIGNMENT.md` for current endpoints.
