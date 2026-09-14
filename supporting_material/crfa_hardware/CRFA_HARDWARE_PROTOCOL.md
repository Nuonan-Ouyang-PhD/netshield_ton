# Rotating Full-Admission Hardware Extension Protocol

## 1. Scientific purpose

This extension tests one specific consequence of the analytical byte frontier on the existing three-probe hardware testbed. It does **not** rerun or replace the accepted 216-arm campaign. It adds one transparent controller whose only purpose is to attain the one-round full-evidence byte frontier while distributing full-evidence opportunities fairly across probes over time.

The extension must remain scientifically separate from the accepted campaign until its own validation gates pass.

## 2. Frozen scope

- Devices: the same three probes used in the accepted campaign: P1 (Raspberry Pi 5), P2 (Raspberry Pi 4B), P3 (Raspberry Pi 3B+).
- Workload/model/input lineage: identical frozen CICIoT2023-derived feature-vector replay and detector/model artifacts used by the accepted campaign.
- Sessions: the same 12 session identities, `F12_S01` through `F12_S12`.
- Capacities: low = 131,072 B/round; mid = 262,144 B/round; high = 393,216 B/round.
- Per arm: 5 warm-up rounds + 90 measured rounds per probe; up to 200 drain rounds.
- Service accounting, event schema, timestamp fields, raw logging, scorer, and validation semantics: reuse the accepted campaign unchanged unless a minimal new action-selection hook is required.
- No modification of historical accepted raw evidence.
- No new detector training, threshold tuning, queue-weight tuning, or capacity tuning.

Total planned extension: **12 sessions × 3 capacities × 1 method = 36 accepted arms**.

## 3. New controller: Cyclic Rotating Full Admission (CRFA)

Let:

- `n = 3` probes,
- `B = 131072` B for H-FULL,
- `C` be the application-byte service budget for the current capacity,
- `K(C) = min(n, floor(C / B))`.

For session `F12_Sxx`, define a frozen rotation offset

`o = (xx - 1) mod n`.

Let `r` be the **global generation-round index including warm-up**, starting at zero. Define

`start(r) = (o + r*K) mod n`.

The selected set is

`S_r = {(start(r)+j) mod n : j = 0,...,K-1}`.

Map indices `0,1,2` to `P1,P2,P3`.

Action rule:

- selected probe -> `H_FULL`;
- non-selected probe -> `H_NONE`.

No summary fallback is part of CRFA. No queue-penalized score is used to choose the action. No safety filter changes the selected action. The existing shared service mechanism still enforces the frozen application-byte budget.

### Deterministic capacity behavior

- low: `K=1` -> one H-FULL + two H-NONE per generation round;
- mid: `K=2` -> two H-FULL + one H-NONE per generation round;
- high: `K=3` -> three H-FULL per generation round.

The 90 measured rounds are divisible by the fair rotation period, so every device receives exactly:

| Capacity | H-FULL / device | H-NONE / device | Total H-FULL / arm | Exact measured payload / arm |
|---|---:|---:|---:|---:|
| low | 30 | 60 | 90 | 11,796,480 B |
| mid | 60 | 30 | 180 | 23,592,960 B |
| high | 90 | 0 | 270 | 35,389,440 B |

These are **protocol identity gates**, not performance targets.

## 4. Pre-run implementation gates

Before any Pi arm is executed, the new implementation must pass all of the following offline checks:

1. For every session/capacity, the action schedule generated for measured rounds matches the exact counts above.
2. For low/mid/high, `K` is exactly 1/2/3.
3. Per-device selection counts are exactly 30/60/90 H-FULL respectively.
4. Maximum consecutive non-selected measured rounds are exactly low=2, mid=1, high=0.
5. The cyclic schedule period is low=3, mid=3, high=1.
6. Generated measured payload is exactly the table above.
7. An offline service-accounting replay reports zero shared-cap violations.
8. Existing methods A--F and their frozen configuration files are byte-for-byte unchanged.
9. Existing accepted raw evidence is read only.
10. A manifest records the hashes of the runner, CRFA policy module/config, frozen model/input/config artifacts, and validation script before hardware execution.

If any gate fails: **STOP_AND_REPORT**. Do not run hardware.

## 5. Hardware execution order

Use the existing infrastructure-health and arm-acceptance gates from the accepted campaign. Do not weaken them for this extension.

Recommended deterministic order per session:

1. low
2. mid
3. high

The scientific unit remains a whole arm. If a pre-hardware or infrastructure failure occurs (device unavailable, SSD failure, power/throttle gate, Wi-Fi/SCP failure, corrupted raw file, runner crash), exclude the entire attempt and rerun the **same session/capacity** with the next attempt identifier. Never stitch partial device data from different attempts.

Do **not** rerun an arm because the timing result is scientifically disappointing. Outcome-based reruns are prohibited.

## 6. Required raw fields

Retain the same occurrence-level and service-round fields used by the accepted campaign. At minimum the extension must make it possible to reconstruct:

- session, attempt, capacity, method;
- probe/device;
- generation round and measured/warm-up status;
- scheduled release timestamp;
- actual event-creation timestamp;
- action requested and final action;
- generated application payload bytes;
- queue before/after service;
- service grant bytes per tick/round;
- core-required flag;
- core-result-received flag and timestamp;
- all fields required to reconstruct post-release and nominal-anchor timing;
- shared-cap accounting;
- device health/power/throttle preflight evidence;
- exact input/model/config hashes.

Add an explicit `rotation_selected` boolean and `rotation_start_index` field if this can be done without altering historical schemas. If schema compatibility requires an extension namespace, use one rather than changing old fields.

## 7. Acceptance gates for each arm

An arm is scientifically accepted only when all frozen infrastructure/data-integrity gates pass and all of the following identity checks hold:

- exactly 270 measured probe-events;
- exact per-device H-FULL/H-NONE counts for its capacity;
- exact total measured H-FULL count;
- exact generated measured payload bytes;
- zero shared-cap violations;
- final evidence queues drain to zero within the existing <=200 drain-round limit;
- no duplicate/missing measured event keys;
- raw-to-validator reconstruction is semantically identical;
- event-level scoring is reconstructable from raw records.

Timing coverage is **not** an acceptance gate.

## 8. Primary scientific outcomes

For each accepted arm and capacity compute:

### 8.1 Common-denominator timely full-evidence output

`timely_full_generated_fraction = on_time_full_core_results / 270`.

This is the primary outcome for comparison with the byte frontier.

The analytical byte frontier is:

- low: `1/3`;
- mid: `2/3`;
- high: `1`.

Define physical frontier attainment

`eta_attain = timely_full_generated_fraction / f_byte_max`.

Do **not** require `eta_attain=1`; physical timing residuals are an empirical outcome.

### 8.2 Conditional post-release timing

`conditional_post_release_on_time = on_time_full_core_results / selected_full_events`.

### 8.3 Eventual return coverage

`full_result_return_fraction = returned_full_core_results / selected_full_events`.

### 8.4 Temporal fairness

Report per device:

- H-FULL selection count;
- maximum consecutive measured rounds without H-FULL;
- maximum inter-selection interval in generation-round indices;
- post-release timely-full fraction.

The selection-count and schedule-gap quantities are deterministic protocol properties and should not receive confidence intervals.

### 8.5 Schedule-inclusive sensitivity

Using the same definitions as the accepted campaign:

`L_post = t_result - t_created_probe`

`L_nom = t_result - t_scheduled_release`

Report post-release and nominal-anchor on-time fractions. The primary 1-s claim remains a **post-release service SLO**.

## 9. Comparisons with existing accepted evidence

Do not alter historical results. After all 36 extension arms pass validation, compare CRFA against the accepted C-QPG result using the same 12 session identities.

Primary matched comparisons:

- low: CRFA vs C-QPG common-denominator timely full output;
- mid: CRFA vs C-QPG common-denominator timely full output;
- high: CRFA vs existing all-H-FULL hardware behavior as a timing/implementation anchor.

Also compare against the existing phase-randomized independent controller only as a **software sensitivity**, never as a new physical baseline.

For timing-derived session-level differences, report the paired session mean and a descriptive 95% session-bootstrap interval. Do not generate bootstrap intervals for deterministic action counts, byte counts, or theoretical frontiers.

## 10. Interpretation rules

Allowed if supported by results:

- CRFA physically approaches or attains a stated fraction of the byte frontier;
- relaxing universal per-round remote coverage increases timely full-evidence output;
- temporal rotation trades per-round coverage for bounded evidence-age/fairness;
- remaining gap to the byte frontier is attributable to measured timing residuals at the system level.

Not allowed without additional evidence:

- CRFA is globally optimal for security utility;
- CRFA improves intrusion-classification accuracy;
- centralized control universally beats decentralized control;
- the byte frontier guarantees physical 1-s completion;
- any exact OS/network cause of P1/P2/P3 schedule-relative offsets;
- any claim that the three-Pi extension is large-scale physical scalability evidence.

## 11. Extension deliverables

Return one clean ZIP containing at least:

- frozen pre-run manifest and hashes;
- runner/policy/config actually executed;
- attempt index including excluded infrastructure attempts;
- all accepted raw arm artifacts;
- per-arm validator outputs;
- occurrence-level reconstructed ledger;
- service-round cap audit;
- per-arm and per-session summary CSVs;
- timing-anchor reconstruction CSV;
- `CRFA_VALIDATION_REPORT.md`;
- `CRFA_NUMBER_PROVENANCE.csv`;
- `SHA256SUMS.txt`.

The validation report must state the number of planned, attempted, excluded, and accepted arms and must explicitly report whether every identity/cap/raw-reconstruction gate passed.

## 12. Stop condition

After the validated extension ZIP is produced, stop. Do not edit the manuscript, GitHub, or Overleaf. Do not infer paper conclusions. Return the evidence package to the paper-writing stage for scientific interpretation.
