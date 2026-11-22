# Physical calibration input contract

This defines the actual local adapter output accepted by `build_profile.py`.
No physical records or calibration values are supplied in the public package.
The synthetic test fixtures exercise this contract only and must never be
copied into an experiment directory as observations.

## Planned observations and sampling unit

Use the qualified prospective shared-stage **calibration** plan. Each
physical block has all eight selected subsets of P1/P2/P3 (including no
selection) crossed with the two initial backlog states, for 16 conditions.
All three probes generate candidates in every condition and execute the
declared H-NONE fallback when unselected. Pilot/formal comparisons retain
their separate six-condition design.

For each planned calibration arm, normalize **only its first measured
generation batch** into one JSONL record. Its actual pre-decision backlog
must equal the planned per-probe state. Build that state once; preserve all
later rounds in the original raw archive and describe them separately.
Three selected full requests already exceed C=2B, so subsequent rounds of
the all-selected capture must not be relabelled as the original 0/B state.

Every first-batch new selected request and preexisting background request
must have its actual matched Core result captured, including late results.
Keep complete follow-up beyond the originating round. The builder refuses
missing jobs, missing/invalid timestamps, duplicate condition rows or an
incomplete block. Resolve instrumentation or follow-up gaps rather than
dropping inconvenient observations. Preserve all attempted arms and retries
under the existing predeclared infrastructure rules; a slow or missed
deadline is an outcome, not an exclusion reason. A terminal unreturned job
prevents this complete-return calibration estimator from being formed and
must be reported, not silently replaced.

The sample unit here is the physical first batch of a condition in a block.
The estimator is the componentwise maximum within each condition. It is not
a population confidence bound or a worst-case physical guarantee.

## `--field-map`: reviewed adapter and raw identities

Supply one local JSON object with these fields:

| Field | Required value/meaning |
|---|---|
| `status` | `REVIEWED_PHYSICAL_CAPTURE_FIELD_MAP` after the actual mapping is reviewed |
| `campaign_id` | Exact calibration plan campaign |
| `runtime_tree_sha256` | `package_tree_sha256()` of the actual isolated patched runtime used for capture |
| `frozen_margin_ns` | The chosen nonnegative integer margin, matching `--margin-ns`; freeze the rationale and value before formal data |
| `mapped_fields` | Object mapping each normalized field below to its actual raw field/boundary definition; nonempty strings |
| `raw_files` | Nonempty list of `{source_id, path, sha256}` for immutable primitive capture files |
| `adapter_source` | `{path, sha256}` identifying the actual normalization implementation |
| `mapping_review` | `{path, sha256}` identifying the review of field semantics, sampling and clock domains |

Paths resolve relative to this file, or may be actual absolute private paths.
Keep this file private. The builder verifies the referenced file digests and
input relationships; the meaning and completeness of the field mapping
require the actual source/record review. It does not independently reexecute
an arbitrary private normalizer. The physical qualification also binds the
actual workload/model inputs, firmware/hosts, source tree and clock epoch
observations. A string claiming that a mapping is reviewed is not a substitute
for those existing qualification gates.

`mapped_fields` must include:

```text
proposal_sample_origin_ns
decision_received_origin_ns
fallback_complete_origin_ns
decision_core_ns
last_decision_sent_core_ns
core_payload_ready_core_ns
core_start_core_ns
core_end_core_ns
core_result_send_core_ns
result_received_origin_ns
origin_clock_id
core_clock_id
backlog_by_probe_bytes
received_prefix_bytes
payload_sha256
core_state_before
```

The profile includes digests of this map, the raw files, the adapter, its
review, the normalized records, the prospective plan and the controller.
At runtime, the Core checks the profile file digest and compares the current
package tree to the calibrated tree. Reuse after changing runtime code needs
renewed calibration qualification; actual model/input compatibility is also
checked through the broader frozen-input qualification.

## `--records`: one JSON object per physical first batch

| Top-level field | Required meaning |
|---|---|
| `campaign_id`, `block`, `condition_id`, `attempt_id` | Planned campaign, positive block number, exact plan condition and unique actual attempt |
| `analysis_stratum` | Exactly `first_measured_generation_batch` |
| `basis` | `physical_capture`; this is a declaration backed by the mapped raw evidence, not a tool-created measurement |
| `workers` | Observed single synchronous Core worker (`1`) |
| `core_clock_id` | Actual Core host and monotonic boot/epoch identity |
| `core_state_before` | Observed `{executing_jobs: 0, queued_complete_jobs: 0}` before this batch decision |
| `decision_core_ns` | Actual barrier decision timestamp on the Core clock |
| `last_decision_sent_core_ns` | Actual last admission response dispatch on the same Core clock |
| `backlog_by_probe_bytes` | Actual P1/P2/P3 queue tails, exactly matching this condition's 0/B fixture |
| `selected_devices` | Actual selected subset, exactly matching `stage_capture_devices` in the plan |
| `raw_source_ids` | Nonempty references to retained `raw_files` source IDs |
| `probes` | Object with exactly P1, P2 and P3, using the probe fields below |
| `jobs` | Complete list of selected new and old background Core jobs for this batch |

Every timestamp and count is an integer; booleans, floating point values and
nonfinite numbers cannot stand in for nanoseconds or bytes. Unobserved values
are not filled from intended configuration. The complete-return estimator
has no missing-timestamp imputation path.

### Each `probes[device]`

- `origin_clock_id`: actual host/monotonic epoch identity.
- `proposal_sample_origin_ns`: timestamp when this batch's stage snapshot was
  taken immediately before sending the proposal.
- `decision_received_origin_ns`: actual receipt of this batch's admission
  response at that same probe/epoch.
- `fallback_complete_origin_ns`: actual H-NONE fallback completion when
  unselected; `null` only when selected. Capture the operation even in the
  empty selected subset, retaining its source record.

### Each `jobs[]` entry

- `event_id`: unique across calibration arms; preserve the old request's
  identity for background work.
- `device_id`, `origin_kind`: P1/P2/P3 and `new` or `background`. Exactly one
  new job is required for each selected probe and exactly one old job for
  each probe with a positive B-fixture tail.
- `remaining_before_bytes`: observed 131,072 B for new work, or the actual
  43,691/43,691/43,690 B tail for old work.
- `received_prefix_bytes`: the actual verified Core prefix, equal to
  131,072 minus that remaining count.
- `payload_sha256`: actual complete serialized payload identity; the local
  raw review must reconcile its prefix, tail and final reconstruction.
- `origin_clock_id`, `core_clock_id`: match this batch's corresponding clock
  identities; reject epoch changes.
- `core_payload_ready_core_ns`, `core_start_core_ns`, `core_end_core_ns`,
  `core_result_send_core_ns`: actual ordered Core observations. Across jobs,
  inference intervals must not overlap the single-worker assumption.
- `result_received_origin_ns`: the matched actual result receipt at the
  originating probe, on its declared clock.

An old job may complete after the first measured round; it remains part of
this batch's required follow-up. The calibration adapter must join by event
identity and cannot replace its Core work with anonymous background bytes.

## Derived allowances and their interpretation

For each condition, retain componentwise maxima over its complete physical
blocks:

| Profile field | Measured local interval used |
|---|---|
| `proposal_transit_ns` | Maximum probe snapshot → admission-response receipt round trip across all three probes |
| `dispatch_compute_upload_ns` | Core decision → latest full-payload readiness for the batch, or last admission-response dispatch when no Core jobs exist |
| `fallback_compute_ns` | Maximum actual H-NONE completion minus admission-response receipt on the same unselected probe; zero only when all probes are selected |
| `core_per_job_ns` | Maximum actual Core inference start → end in that condition |
| `return_ns` | Maximum originating-probe admission-response receipt → matched result receipt for that batch's Core jobs; zero only when no Core jobs exist |

The first interval deliberately includes barrier wait/response time and
therefore over-allocates the one-way proposal delay. The last interval
deliberately includes preparation, upload, Core waiting/computation and
return, so it over-allocates a return stage. Neither is labelled a measured
one-way Wi-Fi delay. Core upload span may itself include earlier synchronous
inferences or local fallback delay. The fallback maximum is retained and
budgeted separately, including in the empty/zero-backlog condition; it is
not discarded merely because that batch has no Core jobs. These overlaps
are retained as conservative empirical budgeting;
no timestamp from one host is subtracted from a timestamp on another host.

After subtracting observed Core proposal residence and the calibrated
proposal allowance from each request's remaining slack, the candidate
reserves:

```text
dispatch_compute_upload_ns
+ fallback_compute_ns
+ number_of_queued_and_selected_jobs * core_per_job_ns
+ return_ns
+ frozen_margin_ns
```

All old and previously admitted jobs are checked again for each proposed
addition. The appropriate selected-subset/backlog envelope is used, so an
over-capacity three-selected calibration does not automatically impose its
multi-round span on a feasible two-selected batch. Unknown organically
arising queue shapes reject new work; existing queues are still served.

Profile conservatism may produce zero admission. Retain that outcome. Check
feasibility during the independent pilot; do not retune the frozen estimator
or margin to improve formal results. The source, packet behavior, hardware
conditions and empirical variation still limit extrapolation.
