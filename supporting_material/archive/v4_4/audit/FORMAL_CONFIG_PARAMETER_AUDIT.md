# Formal configuration parameter audit — V4.4

Date: 5 Sep 2026

The three formal campaign configuration files supplied for the paper-eligible S01--S12 experiment were independently parsed before V4.4 manuscript generation.

| File | experiment_id | app_capacity_bps | dpp_v | window_seconds | windows | warmup_windows | deadline_ms | SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| experiment.low.json | hardware_main_low | 1,048,576 | 1.0 | 1.0 | 95 | 5 | 1000.0 | `c3e276c404784e894bf5595c26af281d1ee8f5899a806ced4596b227750ce53e` |
| experiment.mid.json | hardware_main_mid | 2,097,152 | 1.0 | 1.0 | 95 | 5 | 1000.0 | `fdcfcf5b4574cbd9bdd7fc42cac5c3ecdeba85d253a574f824b6ab07db182825` |
| experiment.high.json | hardware_main_high | 3,145,728 | 1.0 | 1.0 | 95 | 5 | 1000.0 | `b0d082f062eb42166e7184391d77261c50c4f4c2181d97c4eafc955f9458fa1b` |

Common fields in all three files also include `max_queue_bytes = 8388608`, `max_evidence_age_windows = 10`, `thermal_guard_c = 75.0`, `minimum_mem_available_bytes = 134217728`, `shared_efficiency = 0.7`, `strict_telemetry = true`, and `synthetic = false`.

## Manuscript binding

Equation (4) now states `v_DPP = 1.0` for all three formal capacity configurations. This closes the reproducibility field identified in V4.3.

The existence of `shared_efficiency = 0.7` is recorded here as configuration provenance. V4.4 does not assign an additional analytical interpretation to that field beyond the frozen implementation semantics already reflected by the campaign outputs; this avoids inventing a role that is not established solely by the JSON files.

No frozen S01--S12 result, statistic, table value, or figure was changed in V4.4.
