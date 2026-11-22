# Offline preparation for conditional supplemental hardware experiments

**Status: no physical experiment has been executed by this package.** The
planner writes `PLANNED_NOT_EXECUTED`, an order table, prerequisite checks and
hashes. It has no SSH, network, deployment or hardware-running functionality.
The private runtime, source/model/input bundle, physical stage measurements
and deployable shared-stage controller are not supplied here.

These are separate supplemental campaigns. Do not overwrite the accepted
216-arm primary campaign, 36-arm CRFA extension, their raw archives, or their
numerical outputs. Existing timely full-core hardware results remain observed
results; assumed delays must never be added to them retrospectively.

## Files and executable entry points

- `plan_hardware.py`: Python standard-library planner; no third-party packages.
- `protocol.json`: numerical factors, phases, anchors and initial-state rules.
- `qualification_template.json`: unresolved private-runtime prerequisites.
- `sample_size_rule_template.json`: deliberately has no default block count.
- `formal_freeze_template.json`: draft hash bindings; not a successful freeze.
- `raw_ledger_schema.json`: proposed JSON Schema for normalized event, service,
  transport-chunk, admission and attempt records.
- `CONTROLLER_AND_CAPTURE_CONTRACT.md`: implementation, clock, causal-input,
  source-isolation, raw-data and analysis requirements for the external runner.
- `test_plan_hardware.py`: offline design/gate regression tests.

Run the tests from the repository root:

```bash
python3 -m unittest discover -s supporting_material/experiment_extension/hardware -p 'test_*.py' -v
```

Planner arguments:

```text
plan_hardware.py
  --study allocator|shared_stage
  --phase calibration|pilot|formal
  --blocks INTEGER
  --order-seed INTEGER
  --campaign-id NEW_ID
  --output NEW_OR_EMPTY_DIRECTORY
  [--config PROTOCOL_JSON]
  [--include-mid-control]
  [--qualification QUALIFICATION_JSON]
  [--sample-size-rule-file FROZEN_SAMPLE_RULE_JSON]
```

`--blocks` is mandatory. It is a count of complete **physical condition
blocks**, not a count of random seeds or a sample-size recommendation.
`--order-seed` randomizes order only. Calibration and pilot blocks do not
count toward the formal sample size.

The following is a runnable **one-block offline drafting example**, useful
for checking the interface. It does not choose the actual study sample size
and cannot qualify or execute hardware:

```bash
python3 supporting_material/experiment_extension/hardware/plan_hardware.py \
  --study shared_stage --phase pilot --blocks 1 --order-seed 20261122 \
  --campaign-id TON_EXT_STAGE_OFFLINE_DRAFT \
  --output /tmp/ton_stage_offline_draft
```

Use a different empty destination for another draft. A populated destination
is rejected so that plans or data cannot be silently replaced. The output
contains:

- `plan.json`, including status, exact conditions, expected counts and balance;
- `condition_order.csv`, including fresh prospective block/arm identities;
- `qualification_report.json`, including the unmet objective prerequisites;
- `SHA256SUMS.txt`.

With no qualification file, the planner succeeds in **drafting** a plan and
reports `BLOCKED_MISSING_OR_UNVERIFIED_PREREQUISITES`. This is not a request
for user permission; the named source, instrumentation, calibration and
runtime checks must actually be completed before an external runner can use
the plan.

## A. Conditional allocator regression

First inspect the **deployed private runtime**, its actual allocator call
sites and the exact build used on the probes/core. The public historical
offline simulator's integer remainder bug does not by itself prove that the
physical runtime is affected.

If the deployed allocator is unaffected, retain the inspected source hash
and regression evidence. Set `deployed_allocator_affected=false` only in a
qualification document linked to that actual inspection artifact. A verified
unaffected finding yields `NOT_NEEDED_DEPLOYED_ALLOCATOR_UNAFFECTED` and
**zero scheduled arms**. An unsupported false flag does not skip the study.

If affected, use the same deployed runtime and frozen inputs for the original
and corrected allocator. The principal diagnostic is synchronized independent
I-QPG at **low capacity, `v=1`**, where small non-drained remainders can change
future decisions. Mid capacity at `v=1` is an optional control, selected
prospectively by `--include-mid-control`.

| Scope | Conditions per block |
|---|---:|
| Low `v=1`, original versus corrected allocator | 2 |
| Low plus optional mid `v=1`, original versus corrected | 4 |

The allowed difference is the allocator fix and any minimal, reviewed
allocator-interface plumbing needed to implement its explicitly frozen
residual-byte tie policy. Keep launcher timing, nominal/creation anchors,
actions, utility values, selector, queue updates, service semantics, workload,
models, scorer and instrumentation identical between variants. A new clock
alignment fix would confound this comparison and belongs in a separate study.

The intended windows are **5 warmup + 90 measured**, with at most 200 drain
rounds, only after confirming compatibility with the retained runtime. The
planner rejects changing these numbers silently. If actual runtime semantics
require another design, amend and re-review the prospective protocol before
running, rather than claiming compatibility.

There is no physical `allocator --phase calibration` grid. Source inspection,
counterexample fixtures and instrumentation checks precede its pilot. A draft
pilot command is:

```bash
python3 supporting_material/experiment_extension/hardware/plan_hardware.py \
  --study allocator --phase pilot --blocks "$TON_ALLOC_PILOT_BLOCKS" \
  --order-seed "$TON_ALLOC_ORDER_SEED" \
  --campaign-id "$TON_ALLOC_PILOT_CAMPAIGN" \
  --qualification "$TON_ALLOC_QUALIFICATION_JSON" \
  --output "$TON_ALLOC_PILOT_PLAN_DIR"
```

Use a campaign ID beginning `TON_EXT_ALLOC_`; the variables are deliberately
not populated by this package. Setting them selects a prospective plan, not
an observed outcome.

## B. Shared-link stage diagnostic

The main design has three probes, a 262,144-byte/round middle application
budget and 131,072-byte full payloads. It is a controlled **H-FULL/H-NONE
admission diagnostic**, not a rerun of summary-preserving S-CQPG. All three
policies see the same candidate requests, fallback semantics and frozen
priority rules.

| Policy | Constraint tested |
|---|---|
| `isolated_precheck_new_bytes` | Original isolated per-task stage estimate plus budget for newly admitted bytes. |
| `backlog_aware_bytes` | The same estimate, with existing queued work reserved before new bytes. |
| `causal_shared_stage` | An actually implemented controller using observable shared-network/core state and frozen independent latency estimates. |

Cross these policies with initial backlog **0 or 131,072 B**, giving **six
conditions per pilot/formal block**. Keep actual requests and H-NONE outcomes
in the generated denominator, including all-reject arms.

For backlog 131,072 B, the proposed remaining-queue fixture is:

| Probe | Remaining application bytes at the decision instant |
|---|---:|
| P1 | 43,691 |
| P2 | 43,691 |
| P3 | 43,690 |

These are the unserved tails of identified old full requests, not newly
invented events or unlogged dummy traffic. Retain the actual received prefixes
and full payload hashes. Their core work waits for complete evidence. At the
initial decision, **no completed-input core jobs may already be queued or
executing**; independently capture this state. If the actual runtime cannot
establish this fixture, qualify and preregister another explicit fixture
before formal data. Never silently assume the core is empty.

Apply the fixture **once**, just before the first measured candidate batch.
Do not replenish backlog every round. Capture actual per-probe values at the
decision, not only the intended aggregate. The primary backlog-mechanism
stratum is the **first measured generation batch**; the 90 measured rounds
provide a prespecified sustained-operation secondary stratum. The ledger
records both labels before outcomes. Later organically accumulating backlog
is measured, not reset to make the result cleaner.

### Separate stage calibration

`--study shared_stage --phase calibration` creates a distinct stage-capture
grid: one candidate on P1, P2 or P3, or candidates on all three, each with
backlog 0/B. These **eight capture conditions** characterize single-probe and
shared behavior; they are not eight controller comparisons. They use an
instrumented fixed-full capture path, so calibration does not require the
new controller to be already implemented. No timely-result acceptance gate
is used to select calibration observations.

This is a proposed capture matrix, not proof that calibration is sufficient
or a requirement to treat every batch as an independent sample. Choose its
block count and measurement plan prospectively. The core's actual concurrency
and transport/service mechanics must be inspected; do not copy the software
model's single-core or constant-rate assumptions without validation.

Calibration, pilot and formal runs have separate campaign/phase identities.
Pilot/formal comparison requires a real, reviewed controller implementation
and calibration frozen from disjoint observations. The software validation's
exact-model `deadline_reservation` is **not** that implementation and must
not be deployed under a claim of validated physical safety.

## Ordering and interpretation of blocks

The planner uses an even-order Williams crossover design. It randomizes the
condition relabeling and row order within each design cycle, keeping each
condition exactly once per block. For complete cycles of 2, 4, 6 or 8 blocks
(matching the number of conditions), every condition occupies each order
position equally often and every directed adjacent pair appears equally
often **within blocks**.

An incomplete final cycle remains usable as a prospectively chosen design,
but is not exactly balanced. The planner reports the exact position and
transition counts, number of complete cycles and partial-cycle blocks. It
does not count transitions between blocks or claim that balancing removes
all drift or carryover. Reset/verify runtime state between conditions and
retain its actual state in the raw logs.

Blocks must be freshly executed physical sessions. Duplicate deterministic
software trajectories or changing only `order_seed` do not create independent
replicates. The statistical unit and residual dependence between physical
blocks must be assessed from how they were actually collected.

## Formal qualification and freezing

1. Complete the private runtime/source inventory and each applicable review
   in `qualification_template.json`. Use actual local artifact paths and their
   SHA-256 digests. Paths are interpreted relative to the qualification file
   unless absolute. Boolean claims alone never qualify a run.
2. Collect distinct calibration/pilot data. Record every attempt. Freeze the
   deployed controller and a fixed number of complete formal blocks with a
   documented pilot-based precision/feasibility rationale. Set the completed
   sample-rule status to `FROZEN_SAMPLE_SIZE_RULE`; the template remains
   unusable until populated. There is no hardcoded `n=12` or requirement to
   stop when significance is reached.
3. Draft the formal plan with the exact block count, campaign identity,
   ordering seed and optional controls. A missing freeze receipt leaves the
   draft explicitly blocked; it does not prevent examining its schedule.
4. Populate `formal_freeze_template.json` from this prospective plan and the
   retained pilot/sample-size artifacts. Bind its exact `protocol_sha256`,
   `planner_source_sha256`, `raw_schema_sha256`, `condition_order_sha256`,
   study/campaign/block/seed/control fields, sample-rule hash, pilot identity
   and actual pilot-report hash. `qualification_evidence_sha256` must map
   each applicable review artifact except the receipt itself to its verified
   digest. Register the receipt before the first formal execution, then set
   its status to `FROZEN_FOR_FORMAL_EXECUTION` and record its hash in the
   qualification file.
5. Regenerate into a **new** destination with the same prospective arguments.
   The planner compares the bindings. Changing the order seed, adding a mid
   control, changing the sample rule, source, schema or any evidence artifact
   invalidates the old freeze.
6. The external runner additionally checks the real campaign registry for
   global ID reuse, deployment hashes and chronological freeze-before-run
   order. A new prefix and matching hashes alone cannot establish those
   facts. `fresh_campaign_registry_checked` binds the actual retained review.

Qualification is a set of technical prerequisites, not a separate approval
flow. The planner can verify artifact existence/hashes and explicit bindings;
it cannot make an unperformed private source review true. Keep private paths,
host addresses, credentials, model files and controlled raw data out of the
public repository.

## Analysis, failures and maturity

Capture the exact original primitive records and the adapter that maps them
to `raw_ledger_schema.json`; never manufacture a normalized success record
from an expected value. Reconstruct cap, queue and byte conservation from
actual service/chunk records, independently of grant/violation flags.

The primary timing anchor is actual event creation to matched result receipt
on the **same originating clock**. Retain nominal-anchor sensitivity
separately. Core wait/inference uses the **same core clock**. Record clock
epochs and never subtract unsynchronized host monotonic timestamps.

Missing timestamps stay null with explicit reasons. A missing result whose
deadline has not matured remains pending/censored, not a definitive miss.
After reliable observation through its deadline, an unreceived result is a
deadline miss even if it later returns. If logging is incomplete, report
uncertainty/bounds rather than inventing observation. Always retain rejected,
late, failed, cancelled and pending new events in the appropriate generated
denominator; separate admission coverage from conditional timeliness.

All attempts, including aborts, remain indexed. Before formal collection,
freeze permissible infrastructure exclusions and any bounded retry rule.
Poor timing, rejected work, cap violations, classifier errors and surprising
action mixes are scientific outcomes, not grounds to exclude or retry.
Missing pairs/blocks remain visible; no silent complete-case selection.

The hardware supplement can support the measured behavior of the actually
implemented methods under its recorded conditions. Empirical calibration
quantiles do not create a hard physical safety bound, and selection gaps do
not become Age-of-Information results. These studies do not establish the
semantic detection value of alert/summary/full evidence; that requires the
separate evidence-value experiment.
