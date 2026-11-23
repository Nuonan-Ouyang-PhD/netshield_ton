# Shared-stage candidate: complete public preparation and local execution

The current hardware preparation and private integration receipts are described in the [execution record](../HARDWARE_CLOSEOUT_CN.md).

The current code is a scoped candidate for the supplemental H-FULL/H-NONE
study. No physical arm or calibration is supplied by this directory.

## What is retained and what is current

The exact `72cc05d` source, runtime hook patch, opt-in integration runner and
receipt are retained in [legacy/](legacy/). The original
[stage_test.json](stage_test.json) is unchanged. Its ten reported synthetic
cases consist of **nine submit/decide cases and one direct-selector case**;
they do not validate the subsequent source changes.

Current files:

- `stage_admission.py`: typed causal snapshots, event/prefix identity checks,
  per-condition empirical envelopes, existing-reservation rechecks and
  explicit rejection of uncalibrated queue states.
- `runtime_hooks.patch`: dedicated stage methods in RC1 Probe/Core, all eight
  selected subsets, epoch capture and consistent in-arm probe epoch checks.
- `build_profile.py`: complete, hash-bound physical calibration input
  validation and per-condition component maxima.
- [CAPTURE_INPUT_CONTRACT.md](CAPTURE_INPUT_CONTRACT.md): exact normalized
  record fields, source mapping, clocks, sampling and estimator semantics.
- `tests/test_stage_admission.py`: public synthetic regressions.
- [../hardware/test_stage_runtime_adapter.py](../hardware/test_stage_runtime_adapter.py):
  **26 submit/decide cases** using the real private runtime with synthetic
  proposals, clocks and profile. The [instrumented runtime receipt](final_runtime_26.json)
  records the executed cases and the exact private tree identity.

## Candidate behavior

Every candidate addition checks the aggregate remaining payload against
C=262,144 B and rechecks the estimated remaining time of **all** queued and
previously accepted requests. Every full payload is B=131,072 B. Fresh and
old remaining slack must be integer nanoseconds and at most the original
one-second deadline; zero/negative slack is retained and causes rejection.

The current profile has 16 distinct conditions: all eight selected subsets
of P1/P2/P3, including the empty and two-probe subsets, crossed with actual
initial backlog 0 or B. All three probes still generate and execute their
selected action or H-NONE fallback. Pilot/formal comparisons remain the
separate six-condition design.

Profiles use the actual **first measured batch** of each calibration arm.
The B state has one real old request per probe with remaining tails
43,691/43,691/43,690 B. Prefixes, payload identity, idle Core state and actual
returns must be recorded. Do not reuse the initial label for later naturally
accumulating queues, and do not inject replacement backlog each round.

Condition-specific maxima keep the overloaded three-selected capture's
multi-round span separate from a feasible two-selected batch. The controller
uses the prospective selected subset's envelope and adds:

1. observed Core proposal residence and a calibrated proposal allowance;
2. dispatch/preparation/upload allowance;
3. the actual calibrated H-NONE fallback-computation allowance;
4. one calibrated Core-compute allowance per old and selected request;
5. the calibrated return allowance and the frozen margin.

The empirical components deliberately overlap. Proposal allowance comes
from a probe-local round trip, and return allowance from a probe-local
post-decision result suffix. They are conservative budgets, not a disjoint
pipeline decomposition or measured one-way Wi-Fi delays. No cross-host
monotonic timestamps are subtracted.

The B/no-new-selection envelope also records estimated old-work margin.
An unknown organic queue shape rejects new work with
`out_of_calibrated_backlog`; the actual old FIFO is still served. Rejection
does not erase pending work or remove new events from generated counts.

When all demanded bytes fit C, the archived integer allocator can fully
grant this particular in-scope batch; its small residual defect occurs when
demand exceeds capacity. Therefore the stage comparison keeps its common
allocator unchanged. The separate original/corrected allocator experiment
still measures the closed-loop physical effect of its repair.

## Apply once to a fresh private RC1 copy

Use the archived runtime whose retained tree digest ends in `393d7085`.
Keep that original intact for the allocator comparison. Apply the current
patch to a new private copy and copy the current `stage_admission.py` into
its `netshield/` package on Core and Probes. Do not apply the old and new
hook patches on top of each other. In the private copy, first run the real
patch check; source-context conflicts require examining the actual runtime.

The public review checks unified-diff syntax only because the complete RC1
source is controlled. It does not claim that the revised patch has been
applied to the actual private source or deployed to devices.

Regenerate the actual runtime identity manifest after all common
instrumentation is finished, retaining the model/input bindings. Both capture
and controller methods use that same frozen code. A physical profile is
bound to its controller source and the actual runtime tree; the Core checks
that identity when loading it. Profile parsing/source hashing occurs once
at load, and scalar envelope inputs are held immutable during operation.

The adapter reads the actual boot epoch from Linux `/proc/.../boot_id` or
macOS `sysctl -n kern.boottime`. Other hosts require a reviewed epoch adapter
before execution. No invented UUID is called an OS boot attestation. These
fields support in-arm checks and private normalization; the actual remote
host/clock qualification remains required. Snapshot creation is skipped for
drain windows.

The runtime assumptions remain one synchronous Core worker and the existing
barrier: a Probe proposes only after receiving its preceding response, and
complete-input inference runs synchronously in the Core event loop. A
pipelined/multiworker runtime needs another reviewed state adapter.

## Execute available checks

Public, standard-library-only tests, from the repository root:

```bash
python3 -m unittest discover \
  -s supporting_material/experiment_extension/stage_adapter/tests \
  -p 'test_*.py' -v
```

Then, in the environment that can import the actual patched RC1 dependencies:

```bash
python3 supporting_material/experiment_extension/hardware/test_stage_runtime_adapter.py \
  /actual/new/patched_runtime /actual/new/scratch_parent
```

The revised private runner sends all 26 cases through `submit/decide`,
including the complete calibration subset grid, both backlogs, zero slack,
a new request that would invalidate a prior reservation, expired old work
and an uncalibrated queue shape. It checks in-scope demand is completely
granted and fixes synthetic priority/time explicitly. Save stdout and the
exact runner/runtime hashes to a new receipt. Keep the old receipt unchanged.

A passing synthetic integration receipt is not a physical qualification.
The local work still has to instrument and review the actual timestamps,
response joins, fallbacks, primitive service chunks, observed initial
backlog/prefixes, clock identities and source-field mapping.

## Build a physical profile from complete real calibration

After three-probe qualification, execute the prospective 16-condition
calibration plan in independent physical blocks. Retain all attempts and
all 90 measured rounds, but normalize the declared first batch per arm for
this estimator. The exact JSONL and field-map contract is in
[CAPTURE_INPUT_CONTRACT.md](CAPTURE_INPUT_CONTRACT.md).

```bash
python3 supporting_material/experiment_extension/stage_adapter/build_profile.py \
  --records /actual/first_measured_batches.jsonl \
  --plan /actual/calibration_plan/plan.json \
  --field-map /actual/reviewed_capture_field_map.json \
  --margin-ns PREDECLARED_NONNEGATIVE_INTEGER \
  --output /actual/new/stage_profile.json
```

This command requires real hash-bound inputs. It will not create a profile
from absent data, an unqualified plan, an incomplete block, a wrong initial
state, missing/late-dropped jobs or unverified raw files. It preserves slow
values in the maxima and refuses an existing output path. Its output status
is `PROFILE_DERIVED_NOT_PHYSICAL_QUALIFICATION`.

Point the actual runtime config's `stage_profile.file` and `sha256` to that
new file. The calibration campaign must differ from pilot/formal campaign
IDs. Synthetic profiles are loadable only under `TON_EXT_STAGE_TEST_` IDs
and cannot enter a physical campaign. Record the independent profile,
hardware qualification and input identities before the pilot/formal freeze.

Use the independent pilot to assess instrumentation and feasibility, then
freeze the formal study and analysis. All-reject arms remain valid outcomes.
No observed maximum, successful software test or frozen margin establishes
a hard physical deadline bound.

## Source-row identity remains a separate result

[SOURCE_ROW_TRACE.json](../SOURCE_ROW_TRACE.json) records the prior 5,141,673
row matches to 31 source CSVs. That file/row identity is distinct from parent
capture/episode grouping. Complete the remaining lineage qualification
through the updated one-pass execution instructions; never assume numbered
PCAP fragments are independent acquisitions.


### Assemble an independently calibrated profile

After a complete physical calibration, run the following on the private evidence volume.
The reviewed map supplies the adapter identity, runtime tree, field definitions and
frozen margin. The command reconstructs each completed attempt from raw files and
checks its plan binding and field identities before building the profile.

```sh
python3 assemble_calibration.py --plan "$PLAN" --campaign "$CAMPAIGN" \
  --review "$REVIEWED_MAP" --margin-ns "$MARGIN_NS" --output "$NEW_PROFILE_DIR"
```
