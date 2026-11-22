# Shared-link and returned-result sensitivity

This is a new, self-contained **software** experiment. It addresses the
difference between an isolated latency precheck, a per-round byte budget,
and completion of a returned core result when probes compete for service.
It does not rerun or modify the frozen primary or CRFA hardware campaigns.
None of its detector, preprocessing, extra uplink, core, or return delays
are measurements of the physical testbed.

## Reproduce

From the repository root, with Python 3 and no third-party packages:

```bash
python3 -m unittest discover -s supporting_material/contention_validation -p 'test_*.py' -v
python3 supporting_material/contention_validation/run_contention_validation.py
```

To keep the committed outputs untouched, append `--output /path/to/new/results`
to the runner. The script performs no network access and does not require the
private runtime, action table, dataset, or Raspberry Pis. All result files are
deterministic for the committed source and explicit configuration.

## Declared model

Every new request is created at tick zero, has a 131,072-byte full payload,
and has a 1,000-ms result deadline. A tick is exactly one millisecond.

1. Each probe performs the configured detector and preprocessing stages.
2. Ready payloads join a per-probe FIFO. Existing remaining work precedes new
   work. A shared server makes
   `floor((t+1)*C/1000) - floor(t*C/1000)` bytes available during `[t,t+1)`;
   integer max-min water filling divides those bytes across ready probes.
   Unused service expires each tick. There is no idle credit bank.
3. After upload completion, the configured extra uplink delay elapses.
4. One FIFO core executes the configured per-event inference time.
5. The result returns after its configured return delay.

The fixed-rate server is a declared proxy for application byte service. The
extra uplink delay is not a measured Wi-Fi distribution, and it does not
model retransmissions, airtime contention, or correlated jitter. Return
traffic has a latency term but no contending byte queue. Different
schedulers, runtime overheads, simultaneous core workers, or uncertain
delays require a different validated model.

| Profile | Detector | Preprocessing | Extra uplink | Core | Return |
|---|---:|---:|---:|---:|---:|
| `zero` | 0 | 0 | 0 | 0 | 0 |
| `assumed_homogeneous` | 40 | 20 | 15 | 35 | 10 |
| `assumed_heterogeneous`, probe pattern 1 | 20 | 10 | 5 | 10 | 5 |
| `assumed_heterogeneous`, probe pattern 2 | 80 | 20 | 25 | 40 | 15 |
| `assumed_heterogeneous`, probe pattern 3 | 140 | 30 | 50 | 100 | 30 |

All entries are assumed milliseconds. The heterogeneous pattern repeats by
probe index. It is a sensitivity input, not an attribution to Pi model or
hardware performance.

## Compared policies

| Policy | Admission rule | What a pass means |
|---|---|---|
| `isolated_precheck` | Each job's configured compute, full-link upload, core and return estimate fits its deadline. | It fits when alone under that estimate. |
| `new_bytes_only` | Isolated precheck plus sum of new payloads no greater than `C`. | New bytes fit the nominal budget; old work and timing slack remain unchecked. |
| `backlog_aware` | Isolated precheck plus existing remaining bytes and new payloads no greater than `C`. | The byte condition is repaired; stage timing and core competition remain separate. |
| `deadline_reservation` | Try each candidate in fixed identifier order, replay all current admitted jobs and background work through the declared model, retain it only if every admitted new result meets its deadline. | Conformance to this exact configured model. |

All policies consider the same requests in the same fixed order. The last
policy is a transparent conservative mechanism for these diagnostics, not
an optimal scheduler or a fairness guarantee. Its rejection count and
selection fraction are reported; a policy that admits no requests does
not obtain a positive timely-output score. Rejected requests remain in the
generated denominator and event ledger.

There are 30 deterministic configurations and four policies, producing
120 runs. The three-probe grid includes low/mid/high capacity, no backlog or
half a round of backlog, and all three delay profiles. Software scaling uses
8, 16 and 32 probes at nominal ratio `C/(nB)=2/3`, both backlog settings and
zero/homogeneous delays. Integer capacity is rounded down for those scaling
cases. There are no statistical seeds, repeated-trial intervals, or
population-level effect estimates.

## Executed counterexamples

At the middle three-probe capacity, `B=131072` bytes and `C=262144` bytes/s:

| Backlog and delay profile | Policy | New full requests admitted | Latest new upload | Latest new returned result | Timely new results |
|---|---|---:|---:|---:|---:|
| Empty, zero | isolated precheck | 3 | 1500 ms | 1500 ms | 0 |
| Empty, zero | new bytes only | 2 | 1000 ms | 1000 ms | 2 |
| 131072 B, zero | new bytes only | 2 | 1500 ms | 1500 ms | 0 |
| 131072 B, zero | backlog aware | 1 | 1000 ms | 1000 ms | 1 |
| Empty, assumed homogeneous | new bytes only | 2 | 1060 ms | 1155 ms | 0 |
| Empty, assumed homogeneous | deadline reservation | 1 | 560 ms | 620 ms | 1 |
| 131072 B, assumed homogeneous | backlog aware | 1 | 1000 ms | 1060 ms | 0 |
| 131072 B, assumed homogeneous | deadline reservation | 0 | — | — | 0 |

The first case isolates the shared-link problem: all three jobs pass a
500-ms standalone upload estimate, but their total 393,216 bytes require
1,500 ms of shared service. The final two cases show why a timely upload is
not necessarily a timely returned result.

Across the whole configured grid, the deadline-reservation policy admits
93 new jobs and all 93 return within the modeled deadline. This is an
expected exact-model check, not independent evidence of physical safety or
an empirical superiority result. The other policies deliberately expose
the omitted constraints. The 120 runs produce 1,668 event records (1,112
new and 556 background), 1,637 event/round service records, and 167 used
service rounds. These counts are simulation bookkeeping, not hardware
observations.

## Ledger and independent audit boundary

- `results/CONFIG.json` records every case, assumption, stage delay, and
  source hash.
- `results/EVENT_LEDGER.csv` retains every generated new request, including
  rejected ones, plus remaining old requests. It contains creation,
  network-ready, upload-complete, core-ready/start/complete and result-return
  ticks. Background creation is `-1000`; its original deadline is not part
  of the new-request admission claim. Background `payload_bytes` means the
  bytes remaining at tick zero.
- `results/SERVICE_LEDGER.csv` records the bytes served to one event during
  one service round. `start_tick` is its first positive service tick and
  `end_tick` is one past its last positive service tick in that round. They
  bound an aggregate interval; they do not assert uninterrupted exclusive
  service. One record never crosses a 1,000-tick round boundary.
- `results/RUN_SUMMARY.csv` reports selection opportunities, upload timing,
  returned-result timing, and the runner's conformance counters.
- `results/SHA256SUMS.txt` identifies the result files.

An auditor can reconstruct round service by summing the service ledger,
reconstruct event byte totals and last-service endpoints, and recompute the
deadline classifications from event milestones without calling the allocator
or trusting summary counters. This checks saved-output consistency. The
allocator itself is cap constrained, so zero simulation violations remains
a software invariant; it does not replace a raw hardware service-ledger
audit. These aggregates do not support a within-tick independent audit.

## Evidence-level value remains an open experiment

This experiment evaluates delivery and configured pipeline timing. It
contains no attack labels and makes no claim that alert, summary or full
payloads improve detection or investigation. The existing formal metric
schema records final admitted predictions, not a same-event comparison of
the downstream value of three representations. See
`DETECTION_VALUE_PROTOCOL.md` for the concrete, unexecuted validation needed
to make that additional claim.
