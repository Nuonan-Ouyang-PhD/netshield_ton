# ToN V1.3 Methodology Repair Validation Report

Generated UTC: `2026-09-08T14:28:57.144838+00:00`

## Scope and evidence boundary

The accepted V1.2 raw evidence, protocol, actions, runtime source, manuscript, GitHub, Overleaf, and Raspberry Pis were not modified. Tasks A, B, and D are offline replay/simulation results; only Task C is a reconstruction from measured formal raw timestamps. Simulated deadline coverage must not be described as a new hardware measurement.

## Run completeness

- Task A: 432 planned rows, 0 retained failures.
- Task B: 240 planned rows (20 fixed seeds x 3 capacities x 4 methods), 0 retained failures.
- Task C: 648 planned session/method/capacity/device rows, 0 retained failures.
- Task D: 20 planned n/rho rows, 0 retained failures; theory/simulation all-match=True.

## Task A — v sensitivity

The exact frozen objective `v*utility - queue_bytes*payload_bytes/1,000,000`, frozen action order, and exact integer max-min allocator were replayed for all 12 formal seeds. `queue_trajectory_bytes` contains every generation-window post-service queue for P1/P2/P3. Period detection is exact and automatic: it reports the earliest suffix (within the first 30 measured windows) repeated at least three times.

The v=1 replay was checked against all 36 accepted formal D session-capacity cells for exact nonzero action mix, payload bytes, core fraction, and sampled max queue: all-match=True, failed checks=0. Hardware post-release coverage is retained as a reference column but is not an identity criterion: the service replay has no Pi runtime/network jitter and exact equality is not expected.

Core-required-fraction ranges by v/capacity:

```json
[
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 1
  },
  {
    "capacity": "low",
    "maximum": 0.24444444444444444,
    "mean": 0.24444444444444444,
    "minimum": 0.24444444444444444,
    "n": 12,
    "v": 1
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 1
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 10
  },
  {
    "capacity": "low",
    "maximum": 0.3,
    "mean": 0.29999999999999993,
    "minimum": 0.3,
    "n": 12,
    "v": 10
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 10
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 100
  },
  {
    "capacity": "low",
    "maximum": 0.3333333333333333,
    "mean": 0.3333333333333333,
    "minimum": 0.3333333333333333,
    "n": 12,
    "v": 100
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 100
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 1000
  },
  {
    "capacity": "low",
    "maximum": 0.28888888888888886,
    "mean": 0.2888888888888888,
    "minimum": 0.28888888888888886,
    "n": 12,
    "v": 1000
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 1000
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 10000
  },
  {
    "capacity": "low",
    "maximum": 0.24444444444444444,
    "mean": 0.24444444444444444,
    "minimum": 0.24444444444444444,
    "n": 12,
    "v": 10000
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 10000
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 100000
  },
  {
    "capacity": "low",
    "maximum": 0.28888888888888886,
    "mean": 0.2888888888888888,
    "minimum": 0.28888888888888886,
    "n": 12,
    "v": 100000
  },
  {
    "capacity": "mid",
    "maximum": 0.6222222222222222,
    "mean": 0.6222222222222221,
    "minimum": 0.6222222222222222,
    "n": 12,
    "v": 100000
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 168
  },
  {
    "capacity": "low",
    "maximum": 0.24444444444444444,
    "mean": 0.24444444444444444,
    "minimum": 0.24444444444444444,
    "n": 12,
    "v": 168
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 168
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 3
  },
  {
    "capacity": "low",
    "maximum": 0.24444444444444444,
    "mean": 0.24444444444444444,
    "minimum": 0.24444444444444444,
    "n": 12,
    "v": 3
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 3
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 30
  },
  {
    "capacity": "low",
    "maximum": 0.32222222222222224,
    "mean": 0.3222222222222223,
    "minimum": 0.32222222222222224,
    "n": 12,
    "v": 30
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 30
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 300
  },
  {
    "capacity": "low",
    "maximum": 0.24444444444444444,
    "mean": 0.24444444444444444,
    "minimum": 0.24444444444444444,
    "n": 12,
    "v": 300
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 300
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 3000
  },
  {
    "capacity": "low",
    "maximum": 0.24444444444444444,
    "mean": 0.24444444444444444,
    "minimum": 0.24444444444444444,
    "n": 12,
    "v": 3000
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 3000
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "minimum": 1.0,
    "n": 12,
    "v": 30000
  },
  {
    "capacity": "low",
    "maximum": 0.28888888888888886,
    "mean": 0.2888888888888888,
    "minimum": 0.28888888888888886,
    "n": 12,
    "v": 30000
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "minimum": 0.5,
    "n": 12,
    "v": 30000
  }
]
```

## Task B — desynchronised independent baseline

Each desynchronised probe uses a seed-fixed independent initial phase in [0,1) s. It observes only its own queue when selecting; there is no action/queue exchange and no joint admission. A 1 ms discrete-event clock makes exactly C/8 application bytes available per second (integer cumulative accounting) and applies the frozen deterministic max-min shared service to current queues. Synchronized independent, central coordinated, and shielded coordinated use the same simulator, workload count, action table, and service rule; coordinated methods alone use the frozen joint degradation rule.

Shield safety uses the frozen deadline calculation under a nominal healthy state: retry delta 0, no thermal guard trigger, and no memory guard trigger. This is a software sensitivity baseline, not replayed hardware telemetry.

Core-required-fraction ranges by method/capacity:

```json
[
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "method": "central_coordinated",
    "minimum": 1.0,
    "n": 20
  },
  {
    "capacity": "low",
    "maximum": 0.0,
    "mean": 0.0,
    "method": "central_coordinated",
    "minimum": 0.0,
    "n": 20
  },
  {
    "capacity": "mid",
    "maximum": 0.3333333333333333,
    "mean": 0.3333333333333332,
    "method": "central_coordinated",
    "minimum": 0.3333333333333333,
    "n": 20
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "method": "desynchronized_independent",
    "minimum": 1.0,
    "n": 20
  },
  {
    "capacity": "low",
    "maximum": 0.3333333333333333,
    "mean": 0.3333333333333332,
    "method": "desynchronized_independent",
    "minimum": 0.3333333333333333,
    "n": 20
  },
  {
    "capacity": "mid",
    "maximum": 0.6666666666666666,
    "mean": 0.6666666666666664,
    "method": "desynchronized_independent",
    "minimum": 0.6666666666666666,
    "n": 20
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "method": "shielded_coordinated",
    "minimum": 1.0,
    "n": 20
  },
  {
    "capacity": "low",
    "maximum": 0.0,
    "mean": 0.0,
    "method": "shielded_coordinated",
    "minimum": 0.0,
    "n": 20
  },
  {
    "capacity": "mid",
    "maximum": 0.3333333333333333,
    "mean": 0.3333333333333332,
    "method": "shielded_coordinated",
    "minimum": 0.3333333333333333,
    "n": 20
  },
  {
    "capacity": "high",
    "maximum": 1.0,
    "mean": 1.0,
    "method": "synchronized_independent",
    "minimum": 1.0,
    "n": 20
  },
  {
    "capacity": "low",
    "maximum": 0.24444444444444444,
    "mean": 0.2444444444444444,
    "method": "synchronized_independent",
    "minimum": 0.24444444444444444,
    "n": 20
  },
  {
    "capacity": "mid",
    "maximum": 0.5,
    "mean": 0.5,
    "method": "synchronized_independent",
    "minimum": 0.5,
    "n": 20
  }
]
```

## Task C — nominal deadline reconstruction

For core-required measured events, `post_release_latency=result_received-created_probe` and `nominal_latency=result_received-scheduled_release`. Missing results remain in the denominator and are not counted on time. Release-lateness quantiles use all measured events in each session/method/capacity/device cell.

Across cells with a core-required endpoint, post-release minus nominal coverage ranged from 0.0 to 1.0.

Observed aggregate p50 ordering: `['P1', 'P2', 'P3']`; P1>P2>P3=True.

The source/log-supported mechanism is recorded in `RELEASE_LATENESS_DIAGNOSTIC.csv`: independent per-probe nominal clocks are created before window 0; the core decision is a three-probe barrier; raw window-0 decision latency and window-1 release lateness expose unequal first-iteration waiting; and the probe loop sleeps relative to the completed iteration without absolute catch-up. The exact OS/network reason for the recurring proposal-arrival order and residual per-session variation are explicitly UNKNOWN.

## Task D — scaling validation

The independent simulator starts all n probes at H_FULL and repeatedly applies the frozen H_FULL-to-H_SUMMARY capacity degradation until total admitted payload fits C. For every requested n and rho, the simulated full count is compared with `clip_[0,n](floor((C-nS)/(B-S)))`, B=131072 and S=16384.

All 20 theory/simulation comparisons match: **True**.

## Validation verdict

PASS — all planned runs are present, the v=1 formal identity gate passed, no shared-cap violation occurred, and scaling theory matches simulation.
