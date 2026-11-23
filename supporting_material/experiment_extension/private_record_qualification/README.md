# Qualification checker repair after dc5269c

This change repairs the **checker**, not the historical experiment. The repaired
checker has been exercised on synthetic fixtures only. It has **not** been run
against the private accepted-arm records in this workspace. No historical
result, ledger, source runtime, or allocation measurement is replaced here.

The local execution statements in [FOLLOWUP_STATUS.md](../FOLLOWUP_STATUS.md)
were produced before this repair. Their checker source is preserved byte for
byte in [qualify_private_records_dc5269c.py](legacy/qualify_private_records_dc5269c.py),
from commit `dc5269c4864e2c4416d6ce6d8390d741bbaad20b`. Its SHA-256 is:

```text
5b193c43e476df783837b51b49d40750222dd8acb3723ada16cd89f8ce81affd
```

The preserved file is a provenance snapshot. Its top-level command-line and
private-runtime imports are unchanged; do not import it as a library.

## Defects addressed

The former checker recorded nonzero `event_balance_errors` and
`grant_demand_service_errors` without failing its process. Its other constraints
used `assert`, which Python removes under `-O`. It accepted empty or repeated
arm lists, accepted fractional byte values, and could accept a byte balance
formed from a negative queue and an excessive receipt. A balanced terminal
record could still contain queued or in-flight work.

The revised [qualify_private_records.py](../qualify_private_records.py) uses
explicit checks and writes a report even when a recognized input, identity,
coverage, or accounting check fails. Importing the module does not inspect
command-line arguments, load the private runtime, or read experiment inputs.
Running the command deliberately loads the supplied archived package-tree
helper, reads the archived source/model bytes, and compares reported identities.
The helper's presence and an aggregate tree attestation remain distinct from
independent remote deployment receipts.

## Command and exit status

The original three positional arguments are retained. From the repository root:

```bash
python3 supporting_material/experiment_extension/qualify_private_records.py \
  /path/to/private/accepted-campaign \
  /path/to/archived/RC1-runtime \
  /path/to/new-qualification-report.json
```

The output must not already exist. The checker reads inputs without rewriting
them and preserves nonzero diagnostic counters in its report.

| Report status | Exit | Meaning |
| --- | ---: | --- |
| `PASS_RECORDED_FIELDS_ONLY` | 0 | The implemented recorded-field checks passed; the limitations below still apply. |
| `FAIL` | 1 | An implemented schema, identity, coverage, or accounting check failed. The report retains the error and partial counts. |
| `PENDING_TERMINAL_STATE` | 2 | No implemented error was found, but a terminal queue, in-flight byte count, final probe queue, or required return is still outstanding. This is an incomplete observation, not a scientific failure of a policy. |

Cancellation bytes are reported separately. A closed record with cancellations
is labelled `CLOSED_WITH_CANCELLATIONS`, not successful delivery. An observed
return after the deadline is a valid late outcome; it does not cause `FAIL`.
`generated` retains all 90 measured occurrences per probe, including occurrences
that did not require a core result. Neither late results nor declined core work
are removed to improve a timely-result fraction.

The report records the checker hash, preserved checker hash, public/private index
hashes, hashes of the inputs read, exact expected/input cohort sizes, per-arm scan
completion, errors, and counters. Its `private_sources` contains local private
paths; use a separately reviewed sanitization process before publishing a raw
report. A source hash and a successful synthetic test are not evidence that this
new checker has already passed the private campaign.

## Implemented checks and their source basis

1. **Cohort binding.** The private accepted-arm set must exactly equal the
   repository's [public accepted index](../../formal_campaign_audit/results/ATTEMPT_INDEX.json).
   Empty, repeated, missing, extra, and different-attempt arms are rejected.
   The default public cohort must contain 216 unique arms, including its selected
   reruns. The checker no longer infers a valid cohort from a total count alone.

2. **Archived identities and capacities.** Deployment roles must be exactly
   `core`, `P1`, `P2`, and `P3`. Deployment model hashes must match the three
   archived weight files. Deployment and runtime-manifest package-tree digests
   must match the archived helper's digest. Probe preflight and manifest host
   names must agree. Each one-second manifest budget must agree with its
   low/mid/high arm. The optional `windows=95`, `warmup_windows=5`, and
   `drain_windows=200` checks use the actual frozen
   [low](../../formal_campaign_audit/configs/formal_v1_2_low.json),
   [mid](../../formal_campaign_audit/configs/formal_v1_2_mid.json), and
   [high](../../formal_campaign_audit/configs/formal_v1_2_high.json)
   configurations; these values are not inferred from a guessed field meaning.

3. **Windows and grants.** Each core device/window pair must occur exactly once
   for three probes and indices 0 through 294. Each probe sequence must contain
   precisely these 295 indices in order. Every cap, demand, grant, receipt, and
   checked queue/payload byte field is a nonnegative integer: booleans, floats,
   negative values, and non-finite JSON values are rejected. Per-device receipt
   must not exceed grant, grant must not exceed demand, and the three grants
   must not exceed that window's configured cap. A violating window contributes
   to `checked_rounds`, but not `verified_rounds`.

4. **Existing producer cross-checks.** The queue recurrence and probe/core
   receipt comparisons are brought forward from
   [review_formal_records.py](../review_formal_records.py). Drain records retain
   its zero-generation treatment. Final probe queue bytes are reported. This
   checks recorded aggregates; it is not a reconstruction from transport chunks.

5. **Measured occurrence identity and endpoint.** Each probe has one measured
   occurrence at each origin 5 through 94. Required event fields bind the
   enclosing arm and device, and the deadline is one second. `event_key` remains
   an opaque historical identifier, unique within its arm/probe namespace, as
   in the original primary reviewer. The checker does not assume that a string
   containing pipes uses the separate CRFA export's key grammar. Window and
   manifest `run_id`/`device_id` fields are checked if present and their absence
   is counted; no new private-schema fields are invented. Terminal component
   bytes must conserve payload bytes. Required result times are checked against
   creation times on the same originating probe clock; missing and negative
   times are handled explicitly.

These checks still do **not** independently establish boot epochs, absolute clock
alignment, remote per-file deployment identity, primitive chunk offsets,
physical receipt, core stage-duration correctness, or in-flight transitions.
They do not validate detection efficacy or eliminate the historical exclusions.
The 295 indices include warmup, measured generation, and drain; they are not a
measurement of 295 seconds of wall-clock runtime. Passing recorded terminal
balances is not proof that all payload bytes were independently observed on
the wire or that all core decisions were timely.

## Synthetic regression suite

```bash
python3 -m unittest discover \
  -s supporting_material/experiment_extension/private_record_qualification/tests \
  -p 'test_*.py' -v
```

The suite uses one synthetic arm with 295 windows and 270 measured occurrences,
three tiny placeholder model files, and a test-only package-tree helper. It does
not load any real model or private input. There are 11 test groups, covering:

- A valid baseline, byte-exact legacy snapshot, and import safety.
- Both formerly nonfatal counters, and capacity failure under normal Python
  and `python -O`.
- Negative, fractional, and boolean byte fields.
- Empty, duplicated, missing, extra, and wrong-attempt cohorts, including a
  one-arm fixture rejected against the real default 216-arm index.
- Duplicate event keys, wrong explicit run/device/origin identities, missing
  windows, and missing required timestamp fields.
- Opaque event-key compatibility without borrowing the CRFA grammar.
- Outstanding queue/in-flight bytes and missing returns producing `PENDING`.
- Queue recurrence, paired receipt, and negative return-latency errors.

Tests supply `--expected-index /path/to/synthetic-index.json` explicitly. This
option is useful for bounded fixtures and is recorded as a nondefault expected
index in the report. A pass with a substituted index does not qualify the public
216-arm cohort. The synthetic helper and placeholder model files test the
checker mechanics; they do not validate the actual archived hash helper or
models.
