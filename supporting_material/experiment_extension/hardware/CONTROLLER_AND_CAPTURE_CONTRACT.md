# Contract for the private-runtime implementation and physical capture

**This is an implementation contract, not a deployed controller or an
execution report.** Resolve the actual private code, field names and hardware
configuration before performing the supplemental experiments. The public
offline simulator is not proof that the deployed allocator or scheduler has
the same implementation.

## 1. Inventory and conditional allocator work

Retain an immutable manifest of the exact runtime tree/build, allocator
function and all call sites, action table, utilities, payload serializers,
workload plan, models, launchers, clocks, transport, queue update logic and
scorer. Locate where application service capacity is generated, allocated,
debited, sent and acknowledged; do not infer that a grant is an actual send.

Inspect the deployed allocator's treatment of an integer remainder smaller
than the number of nonempty queues. Exercise the actual function on small
unequal-demand cases, zero demand, capacity below the number of active queues,
and the frozen low/mid three-probe states. Establish work conservation as
`sum(grants) = min(cap, sum(demand))` while preserving nonnegative integer
grants, grant<=demand and total<=cap. The function tests must not invoke the
testbed or mutate the accepted archive.

If this deployed implementation is unaffected, record that finding and do
not run an allocator "fix" campaign solely because an offline script had a
bug. If affected, preserve its source and implement the smallest reviewed
allocator repair. Freeze residual-byte priority explicitly, including any
round-dependent rotation and minimal call-site plumbing; do not silently
change fairness policy. Verify original and corrected runtime manifests
differ only in the allowed allocator code/version identification.

For the physical original/corrected comparison, preserve the launcher and
both nominal/actual time anchors exactly. Do not combine an allocator fix
with absolute-clock alignment, detector changes, summary encoding changes,
or alternative scoring. Instrumentation changes needed for this new study
must be identical in both variants and separately recorded; do not apply
them retrospectively to accepted evidence.

## 2. Common candidate/action fixture for the shared-stage study

The six pilot/formal conditions are controlled H-FULL/H-NONE diagnostics.
Each declared candidate probe generates its real event before the admission
decision. The three policies receive the same candidate information,
payload encoding and admission-priority sequence. A nonselected request
uses the predeclared H-NONE path and remains in generated counts. Do not
substitute a local decision for a returned core result.

Freeze ties/rotation independent of the tested policy; record their state.
Keep detector thresholds/models, payloads, computation placement, generation
schedule, deadline anchors, core worker count and application service
accounting the same across policies. If a policy needs extra telemetry,
capture the corresponding telemetry in all arms so differential logging
overhead does not masquerade as a policy effect.

The new policy is not to be labeled S-CQPG or treated as the original
summary-preserving method. A later integration into that controller must be
reviewed and evaluated as its own explicit change.

## 3. Backlog and core-state fixture

Start the measured diagnostic from a verified state, not just a configuration
request. For the B-backlog condition, retain old request IDs and encoded
payloads whose remaining upload tails are 43,691/43,691/43,690 B on P1/P2/P3.
Their previously received prefixes and final decoded payload hashes must
reconcile. Their core computation must wait for complete upload; do not
silently remove the pending work after treating its bytes as background.

At the first measured decision, the core has zero active inference jobs and
zero complete-input jobs queued for inference. This leaves the old
incomplete-upload requests alive; as their tails arrive, they join the actual
core queue. Record the expected and observed state and the method used to
establish it. Do not assume that an asynchronous worker is idle merely because
its inbound byte queue is empty.

Any service pause, barrier or preparatory transfer needed to establish the
fixture must be documented and applied consistently to the zero-backlog
control. Retain setup logs separately from measured-origin events. If the
runtime cannot support the fixture without changing the tested behavior,
stop this design and amend the prospective protocol; do not synthesize
backlog by editing a result ledger.

Apply this fixture once, before the first measured candidate batch, then
allow subsequent queues to evolve. Preserve both the prespecified
first-batch mechanism stratum and all-90-round sustained stratum. Never
inject fresh hidden backlog each round or postselect the most favorable
rounds.

## 4. Required causal shared-stage controller

The existing exact-model software `deadline_reservation` is a diagnostic
oracle for declared durations. It is not the physical controller. The
private implementation must expose an auditable admission function and
source/build identity, taking only state available at decision time:

- candidate payloads, actual release/readiness information and elapsed slack;
- per-probe remaining queued work, including old and already admitted work;
- application service remaining in the current round and the inspected
  future-service semantics;
- actual core worker count, observable queued/executing jobs and calibrated
  estimates of their remaining cost;
- frozen estimates/uncertainty treatment for detector/preprocessing, uplink,
  core and return stages, learned only from separate calibration/pilot data;
- fixed tie/rotation state and declared fallback actions.

The controller must account for the interaction between newly admitted jobs
and all earlier admitted jobs. It cannot certify a new request while
invalidating a deadline reservation for previously admitted work. Record
the candidate set, selected set, state snapshot, calibration digest,
predicted slack and rejection reason at every decision.

Match the feasibility calculation to the **actual** service mechanism.
A round-byte budget is not automatically a constant-rate server, and a core
with multiple workers is not the one-worker software fixture. A single
`payload/link_rate` estimate is not a shared-service constraint. A remaining
byte budget does not by itself reserve detector, network-readiness, core
waiting or return time.

No test event's later measured upload/inference/return time may be supplied
as an input to its own decision. In source review, trace every latency
estimate to its frozen calibration artifact and every online state field to
a timestamped observation preceding the decision. Calibration and formal
episodes/attempts must be separate. Do not tune a quantile or safety margin
to the formal test's misses or zero-admission outcomes.

A central controller cannot combine raw monotonic deadline timestamps from
different probe clocks. Use a validated clock-alignment mechanism with
explicit error bounds, or a causally obtained remaining-slack mechanism
with the controller/communication delay accounted for. If that mechanism
is only an empirical estimate, report it as such. No successful software
rollout, calibration maximum or empirical quantile establishes a hard
physical latency bound.

Pilot acceptance is about implementation/instrumentation correctness,
not achieving a favorable admission or deadline score. If the configured
controller rejects all work, retain the observation and assess feasibility
during the pilot. Once formal parameters are frozen, all-reject arms are
valid scientific outcomes and remain in the generated denominator.

## 5. Capture the real pipeline without mixing clocks

Provide an adapter from actual private fields to the proposed normalized
schema and retain its source hash plus original field mapping. Preserve the
immutable primitive records. Normalization is not permission to populate
unobserved fields with expectations from configuration.

| Stage/endpoint | Required observation | Clock domain |
|---|---|---|
| Nominal and actual generation | Scheduled release; actual event creation | Originating probe |
| Detector and preprocessing | Real stage begin/end; overlap retained if present | Originating probe |
| Upload submission | Enqueue and local transport submit begin/end | Originating probe |
| Complete-evidence receipt | Explicit receipt ACK if the protocol has one; actual complete-payload readiness at core | ACK on origin; payload-ready on core, separately |
| Core queue and inference | Queue entry, actual start/end, result send | Core |
| Result deadline | Matched result received at originating probe | Originating probe |

Local socket-send completion is not remote complete-payload receipt. A core
timestamp minus a probe timestamp is not a measured one-way Wi-Fi latency
unless alignment and its uncertainty were independently validated. Record
host IDs and clock epoch/reboot IDs. Core waiting and inference can be
measured within the core clock; end-to-end result return can be measured
within the probe clock without requiring cross-host subtraction.

Actual Wi-Fi behavior is observed through the running transport path and
end-to-end timestamps. Do not substitute an assumed random delay distribution
and label it real Wi-Fi. If NIC/link-layer traffic or airtime is not captured,
retain `not_measured`; application-byte service is not total physical traffic.

## 6. Independent primitive service/queue accounting

Instrument the data path so that each actual unique application-service
chunk has a request ID, byte offsets, accounting round and source record ID.
Keep allocator grants separate. Preserve duplicate wire sends, framing,
cancelled/discarded bytes and in-flight state with their actual semantics.
For each probe and service period independently reconstruct:

```text
queue_before + newly_enqueued - cancelled_from_queue - actual_served = queue_after
```

Then sum actual charged unique application service across all probes in the
same round and compare it with the frozen budget. Reconstruct bytes using
the raw chunk offsets/records, not merely a `cap_violation=false` flag or an
allocator-internal grant counter. Verify expected event identities, missing
and duplicate records, payload conservation and final queues. Check the
adapter against the raw records; agreement between two summaries produced
from the same unverified counter is insufficient.

`scripts/audit_service_ledgers.py` already demonstrates independent checks
for the repository's known exported schemas. Reuse it where the fields
actually match, and extend through a reviewed adapter for the new primitive
logs. The proposed schema does not claim that every field is currently
available or that a private raw audit has already passed.

## 7. Attempts, maturity, denominators and interpretation

Register all starts, completions, aborts and retries with immutable attempt
IDs, exact runtime/plan/input hashes, health/preflight observations and raw
archive manifests. Freeze the independent infrastructure exclusion list and
retry limit before formal data. A bad scientific outcome—including a cap
violation—is never an exclusion/retry reason. Preserve an incomplete block
and its missing pair explicitly if infrastructure loss cannot be repaired
under the predeclared rule.

For each new request, retain actual generation even if rejected, cancelled,
failed, delayed or unreturned. Report selection fraction and timely full-core
results per all generated events, alongside conditional selected-result
timeliness. With labels available, timely correctness is an additional
endpoint, not a substitute for tracking missing results.

Keep unobserved timestamps null with a reason. Record the last trustworthy
observation instant. An unreceived result before deadline maturity remains
pending/censored; after reliable observation through the deadline it is a
deadline miss, even if still pending eventual return. Unknown follow-up due
to corrupted logging requires stated bounds/uncertainty. Do not treat a
missing timestamp as zero duration or silently drop the occurrence.

Report matched differences at the predeclared complete physical-block unit
and keep calibration/pilot separate from formal results. A generated event,
probe, round, scheduling seed or duplicated deterministic trajectory is not
an independent physical replication. Account for any remaining dependence
between collected blocks rather than assuming a magic sample size.

These experiments address allocation, contention and endpoint fidelity.
They do not prove that alert, summary and full evidence have different
intrusion-detection value. The evidence-value ablation remains a separate
study with real representations, a frozen downstream task and held-out
episode/capture groups.
