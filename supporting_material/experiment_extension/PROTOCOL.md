# NetShield targeted experiment-extension protocol

## 1. Purpose, status, and evidence boundary

This protocol operationalizes the ten methodological criticisms without
replacing the accepted **216 primary + 36 CRFA = 252 historical hardware
arms**. Keep their raw inputs, outputs, inclusion decisions, source identities,
and published timing contrasts frozen. The corrected-code audit at published
commit `e9a2d335e75d1f34efb71c6a0fa2cf4b085660f5` is the starting point, not
evidence that a corrected runtime has already run on Raspberry Pis.

The completed 120 shared-service model runs remain **deterministic software
sensitivity** with assumed stage delays. Fixture tests validate tools, not
detectors, Wi-Fi, or physical safety. New datasets, calibration, pilot, and
formal runs receive fresh identities and separate directories/manifests.
Reuse a historical workload only by explicitly referencing its immutable
identity; never append new observations to an old arm or relabel old results
as corrected-runtime measurements.

The user has authorized this work. The qualification gates below check
scientific prerequisites and artifact consistency; they are **not new
permission requests**. If an input is missing or a gate fails, mark only the
dependent stage `BLOCKED_INPUT` or `BLOCKED_QUALIFICATION`, record the exact
reason, and continue independent preparation and checks. Do not infer a
successful experiment from a prepared plan, example CSV, or passing test.

## 2. Map the criticisms to work

| Criticism | Required step | Additional physical experiment? |
|---|---|---|
| 1. Upload completion labeled core result | Keep explicit upload/result endpoints; audit existing timestamps; score actual pipeline stages when available. | Only for a new physical stage/latency claim; adding assumed delays does not supply measurements. |
| 2. Waterfill remainder | Retain old/new software comparison; inspect the deployed allocator; conditionally execute the allocator comparison below. | Recommended if the affected implementation was actually deployed and corrected-runtime behavior will be claimed. |
| 3. Duplicate Task A seeds | Preserve 36 deterministic configurations and audit the 12 duplicate labels per configuration. | No; more ineffective seeds add no replication. |
| 4. Cap zero by construction | Independently reconstruct saved primitive grants, queue conservation, missing rounds, and timestamps. | Reaudit existing records first. Public CRFA exports and private primary raw records are different audit scopes. |
| 5. Backlog omitted | Test and log pre-existing per-probe queues, pending core work, and new arrivals separately. | Required for a new physical backlog/deadline effectiveness claim. |
| 6 and 9. Isolated safety under contention | Preserve counterexamples; qualify a causal shared-stage controller; run the conditional six-condition study below. | Yes if claiming that the new filter improves physical deadline outcomes; optional for the present isolated-heuristic scope. |
| 7. Different timely predicates | Distinguish origin-round upload, elapsed upload, and actual result return; inclusive deadline boundary. | No for the semantic correction. |
| 8. Paper/code mismatch | Maintain source/result manifests and an endpoint/version/claim mapping for every output. | No. |
| 10. Evidence-content value | Run the paired information-only ablation first; then, if justified, evaluate delivery under shared service. | The first value experiment can be entirely offline. |

Existing public checks and their executed scope are recorded in
[`METHODOLOGY_VALIDATION_REPORT.md`](../../submission/audit/METHODOLOGY_VALIDATION_REPORT.md).
The existing independent auditor is
[`scripts/audit_service_ledgers.py`](../../scripts/audit_service_ledgers.py).
Do not replace an unavailable private raw audit with the simulator's own
`cap_violation_counter`, or describe either as a NIC/airtime measurement.

For authorized local inputs, use `discover_assets.py --root NAME=PATH`
(repeat for each scoped root) with a fresh `--output` path. It reports
candidates and schema/source hints without executing code or loading model
objects; a discovered file is not a qualified deployed runtime or dataset.
Use `freeze_inputs.py freeze|verify --input NAME=PATH --manifest FILE`
(repeat `--input`, and supply `--label` when freezing) to retain/verify byte
identities without copying input contents. Record unresolved discovery,
read, and size-limit cases. A manifest records identity, not successful
execution, provenance sufficiency, or absence of leakage.

## 3. Freeze the scientific contract before outcomes

For each study record: study/campaign/phase IDs; source and adapter hashes;
runtime/model/encoder identities; dataset/group/split hashes; the task and
prediction unit; primary endpoint and contrast; positive class or multiclass
label set; threshold policy; complete conditions; generated-event and
analysis denominators; missing/censoring rules; exclusion rules; and the
sampling, ordering, and stopping plan. Outcome-informed model,
representation, or policy retuning requires a new frozen version and an
untouched evaluation set. Accounting/logging corrections must version both
artifacts and identify a reanalysis of already seen data; they do not turn
that data into a fresh confirmatory test.

Use actual independent source captures/episodes for detection inference and
fresh physical session blocks for hardware uncertainty. A random seed, an
event ID, and a repeated feature vector do not create independent units.
There is no automatic requirement for 12 seeds or 12 blocks. Use independent
pilot/calibration data to choose a defensible fixed block count and analysis
method before formal outcomes are visible. The supplied hardware planner
supports fixed complete-block counts only. A precision-based sequential rule
would require its own predeclared maximum sample size, valid analysis, and
separately implemented planner. Do not stop when significance,
an attractive improvement, or a desired number of successes first appears.

Record every attempted arm. Infrastructure exclusions must be predefined
and adjudicated from infrastructure/data-integrity evidence, not latency or
accuracy. Retain excluded and incomplete attempts with reasons; do not stitch
partial attempts. Predefine how an interrupted block is repeated and how
incomplete blocks are described. Give empirical estimates and uncertainty
for the declared population; no submission-probability estimate follows.

## 4. Information-only evidence-value ablation: first empirical priority

### Inputs and qualification

Obtain authorized source observations, their capture/episode relationships,
true labels kept outside the prediction path, actual representation encoders,
and actual downstream models. Public aggregate tables and the historical
perfect-classification replay cannot substitute for these inputs.

Define **one primary downstream task before inspecting its test outcomes**.
The supplied scorer supports predeclared **binary classification only**, with
an explicit positive class and prediction unit. Episode correlation,
incident localization, or another structured task needs a separate frozen
task adapter and scorer; the supplied CLI does not validate those outcomes.
Specify which fields alert, summary, and full actually expose. Create all
three representations for each held-out occurrence from the same underlying
observation; retain the encoded-byte hash, decoded field inventory, content
bytes, framing, and padding/repetition separately. A larger serialized payload
is not proof of more useful information. "Content bytes" is an accounting
label, not an information-theoretic utility measurement.
Freeze the observation window and availability horizon for all three levels;
full evidence must not silently use future observations unavailable to the
alert or summary. Preserve source-window boundaries and availability times.

The encoder adapter may access the source observation but not its ground-truth
label. The consumer adapter receives only the decoded representation and the
frozen model/configuration; it must not retrieve omitted features from a
shared dataset, resolve truth from IDs/filenames, or substitute the local
detector's score for an unexecuted core decision. An alert may legitimately
contain a **predicted** local label when that local model and its training
provenance are declared. Log adapter invocations, input/output hashes and
failures. A prediction CSV and a model-hash string alone cannot prove that
the actual model or representation pipeline was executed.

Prefer one frozen consumer/model/threshold with explicit field masks when
the task supports that comparison. If representation-specific consumers are
necessary, freeze their training budget and operating rules and describe the
contrast as **representation plus consumer**, not an isolated byte-count
effect. The supplied scorer binds one common model and threshold with three
declared encoders; representation-specific models need a separately versioned
schema/adapter/scorer, not falsified shared model IDs. Fit all transforms,
features, models, thresholds, and operating
points on training/validation data, then lock them before testing.

### Split and leakage checks

Assign related observations to the same source-capture/episode group before
splitting; repeated probes of one incident must not cross the split merely
because they have different device IDs. Audit both exact and near duplicates
across train, validation, calibration, and test. Specify canonicalization,
features, scaling, distance, thresholds, candidate-search method, and search
coverage. Fit scaling on training data or use a fixed domain definition;
never choose a near-duplicate threshold to improve test scores.

Exact hashing does not establish absence of near duplicates. Approximate
search or sampled comparisons must report their coverage and unsearched
pairs; they cannot certify a leakage-free dataset. Document how flagged
groups were merged, excluded, or assigned before the split was frozen.
Unresolved overlap or unavailable grouping provenance blocks an independent
held-out generalization claim; diagnostic scoring may continue with the
restriction stated. These audits reduce identifiable leakage, not every form
of dependence or domain shift.

### Execution and scoring

First execute all three representations with delivery delay/loss removed.
Retain all generated occurrences and one explicit outcome per representation,
including adapter failures or missing predictions. Use the scoring interface:

```bash
python3 supporting_material/experiment_extension/evidence_value/score_evidence_value.py \
  --protocol /path/to/protocol.json --groups /path/to/groups.csv \
  --corpus /path/to/corpus.csv --occurrences /path/to/occurrences.csv \
  --predictions /path/to/predictions.csv --output /path/to/report.json
```

The evidence-value directory documents the exact input schema. The scorer
validates/scores supplied artifacts; it is not a substitute for running the
qualified encoder/model adapters. Synthetic schema examples remain fixtures.

Report TP, FP, FN, TN, precision, recall, and F1 from the declared confusion
counts, all generated/scored/missing counts, and coverage. Preserve raw family
labels for separately declared per-family breakdowns; the supplied CLI's
confusion metrics are binary, not a multiclass/family evaluator.
Keep constructed/offered representation bytes separate from admitted,
actually served, and measured wire bytes. Summing a rejected request's
encoded payload does not mean those bytes traversed the link; unavailable
encoding or wire costs remain unknown rather than zero.
Define whether any "macro" average is across classes or across groups;
do not interchange them. Report pooled counts alongside group-level results.
Use paired resampling of the **same independent groups** for all evidence
levels, never event-wise bootstrap over repeated features. The bootstrap seed
and Monte Carlo sample count control the numerical calculation, not the
number of independent observations. With insufficient independent groups,
report descriptive paired outcomes and the limitation rather than a purported
population interval.

An observed-only F1 is conditional on obtaining an output; missing outputs
must not become true negatives. A high conditional score cannot hide poor
coverage. No detection-gain conclusion is qualified if material missingness
or leakage makes the comparison unidentified. A null or adverse value
contrast is retained and may require revising the utility ordering; do not
change the task after seeing it.

Only after this step, evaluate the same frozen task/representations under
shared-service conditions. Retain rejected, late, absent, and censored
outcomes in the generated ledger. Primary service quantities include timely
correct outputs per generated occurrence/episode and the corresponding
counts; conditional latency or conditional F1 is reported separately. Timely
attack recall, if added as a task metric, needs a separately verified
calculation using all generated positive episodes as its denominator,
including rejected and late cases; an absent benign prediction is an
abstention, not an observed true negative. The supplied CLI's primary
transport metric is timely correct outputs per generated occurrence. Do not
label the predetermined utility score, an increased payload, or a selection
gap as measured detection benefit or Age of Information.

## 5. Allocator study: inspect first, run only the dependent extension

Inspect the authorized deployed runtime and launch configuration, identifying
the actual service function, call path, integer units, residual policy,
queue order, and runtime/model/config hashes. Record one of: affected legacy
path confirmed; a different implementation verified; or deployment unknown.
Exact agreement of the public replay with old tables is supporting evidence,
not direct proof of the private executed source.

When the affected path is confirmed, qualify an old/new runtime pair that
differs only in the allocator change and its declared residual-byte priority.
The primary diagnostic is three probes, low budget 131,072 B/round,
`v=1`, paired old/new conditions on the same immutable workload. An optional
mid-capacity pair is a control, not a substitute for the affected low case.
Use fresh physical blocks, balanced condition order, verified resets/drains,
and preserved attempt records. Reuse five warm-up and 90 measured rounds
only when the inspected runtime's contract supports them; record any new
contract explicitly.

Primary outputs are per-round action counts, pre/post queues, demand/grant
conservation, residual service, and generated payload. Returned-result
timestamps are additional measured endpoints, not values inferred from the
public replay. Compare against the published software prediction without
treating it as a required acceptance outcome: low `v=1` changed from 66/270
to 90/270 full requests in that reconstruction. Report action period and
complete action-plus-queue state period separately. If the deployed path is
different or unavailable, retain that finding and do not invent a hardware
confirmation or invalidate all historical arms.

## 6. Shared-stage hardware study: conditional on the intended claim

The present manuscript treats the frozen filter as an isolated eligibility
heuristic. To add a claim of improved physical end-to-end deadline behavior,
qualify an actual causal shared-stage policy before testing it. Its decisions
may use only observations available at admission time: current queues,
declared request sizes, released/pending core work, and a predictor calibrated
on **independent calibration sessions**. Freeze predictor, margins,
controller code, and any retraining rules before formal blocks. The model
reservation oracle used in the 120 software runs is not a deployed controller
or independent validation of its own predictions.

The minimal diagnostic block has **six conditions**:

| Policy | Empty incoming queues | Controlled old backlog of 131,072 B |
|---|---|---|
| Original isolated precheck plus new-byte admission | Condition 1 | Condition 2 |
| Backlog-aware byte admission | Condition 3 | Condition 4 |
| Qualified causal shared-stage/result-deadline policy | Condition 5 | Condition 6 |

Use three probes, 131,072-B full requests, middle budget 262,144 B/round, and
a 1,000-ms result-return deadline. This is a controlled H-FULL/H-NONE
admission study: each new request asks for H-FULL, and an unselected request
retains H-NONE. It is not a relabeling of the frozen full action lattice or
its summary-preserving hardware method. Declare the release process, core
worker count, real payload representation, detector/model, and service
discipline. Freeze the old backlog's per-probe FIFO distribution,
age/remaining work and core work required after its upload; its aggregate
byte count alone does not define a repeatable condition. At entry to the
**first measured batch**, the core is idle with no pending core jobs, and the
designated old-upload backlog is exactly zero or 131,072 B. Verify those
actual states before admission. That first measured batch is the primary
comparison for the initial-backlog stratum; later batches describe the
ensuing trajectory and must not all be treated as independently exposed to
that same initial backlog. Balance
condition order across blocks and report incomplete order cycles rather than
silently describing them as perfectly balanced. Prevent uncontrolled carryover
with declared resets/washout and retain unresolved outcomes.

Calibration, pilot, and formal plans use separate IDs and data. The planner
interface is:

```bash
python3 supporting_material/experiment_extension/hardware/plan_hardware.py \
  --study shared_stage --phase formal --blocks N --order-seed INTEGER \
  --campaign-id NEW_ID --qualification /path/to/qualification.json \
  --sample-size-rule-file /path/to/sample-size-rule.json --output /path/to/plan
```

Use `--study allocator` for the paired allocator study and
`--include-mid-control` only when declared in its design. Substitute a
predeclared block count for `N`; this protocol supplies no arbitrary count.
The planner generates a plan, **not a hardware execution**. Formal execution
requires qualified runtime adapters, devices, workload and recording paths.
Preflight failures block the dependent run, while offline analyses continue.
The formal freeze receipt must bind the actual study/campaign, block count,
condition set/control choices, order seed, planner source, protocol and
sampling-rule hashes, retained pilot report, and qualification evidence
hashes. True booleans and an unrelated review file are insufficient.
An external campaign-registry check establishes that an ID is unused; a new
prefix alone does not. Record the freeze before the first formal observation.
Hash binding verifies identity, while source/deployment review and truthful
chronology remain explicit responsibilities of the real execution adapter.

Report rejection/selection, timely returned results per generated request,
conditional lateness, processing cost, and independent cap reconstruction.
Rejecting every request produces zero useful timely output; it cannot support
an effectiveness claim from a vacuous conditional success rate. Even with
no observed misses, finite calibrated tests establish behavior in their
tested conditions, not a universal physical deadline guarantee. Any causal
comparison additionally requires the declared randomized/balanced execution,
complete matched blocks or an explicitly justified incomplete-block analysis,
and disclosure of carryover/environmental limitations.

## 7. Clocks, denominators, ledger qualification, and retention

Compute primary result latency from creation and result receipt in the same
originating probe clock domain. Preserve scheduled-release anchoring as a
separate sensitivity. Record local compute/encoding, enqueue, last-byte
completion, core readiness/start/end, and result receipt with clock IDs.
Same-host stage durations are usable directly; subtract timestamps across
hosts only with a validated alignment procedure and an error bound. Do not
infer one-way Wi-Fi delay by subtracting unrelated monotonic clocks, or add
stage durations twice when their intervals overlap.
Creation-to-result time measures service after the declared creation anchor.
An attack-onset-to-alarm or temporal-correlation claim additionally needs a
separately defined and observed source/incident-time anchor; changing the
anchor cannot be hidden by creating the event after expensive processing.

An event is timely when its actual returned endpoint is no later than its
declared deadline, inclusive. A missing result becomes an observed deadline
miss only after the observation horizon reaches that deadline in the relevant
clock. Immature missing observations remain censored, with bounds or an
unavailable estimate; preserve later returns and all generated events.
Separate warm-up, measured and drain observations without dropping late
measured outcomes. Immutable event IDs must connect requests, admission,
service and results.

The independent audit must reconstruct per-round grants from primitive
records, check nonnegative service/demand, queue continuity and byte
conservation, identify missing/duplicate rounds and events, and recompute
deadline classifications from timestamps. It must not call the scheduler
to certify the scheduler or trust a stored zero-violation flag. Record
whether the audit covers original primitive logs, exported records, or only
aggregates; no level silently certifies another.

Retain source/result/config manifests, commands and environment, input hashes,
all attempt statuses, qualification reports, actual protocol deviations, and
an endpoint-to-claim map. Preserve private raw observations, model artifacts,
credentials, machine identities and third-party data in authorized local
locations; prepare only reviewed path-free aggregates and permitted code for
repository publication. Hashing a private file does not grant redistribution
rights. Keep proposed changes on the review branch; no main-branch merge or
rewrite of frozen scientific artifacts is part of this protocol.

## 8. Qualified conclusions and completion criteria

| Observed outcome | Conclusion that is supported |
|---|---|
| Tool/fixture tests pass | Implementation checks passed on the specified fixtures. No experiment result is implied. |
| Existing ledger reconstruction passes | The stated records are internally consistent with the reconstructed metrics and cap. No new physical campaign occurred. |
| Public old/new replay differs | The declared allocator can alter controller decisions in that model. Physical effects remain a separate question. |
| Paired physical allocator comparison completes | The measured old/new difference for the inspected runtime and tested workload, with declared uncertainty and scope. |
| Qualified held-out content ablation completes | The tested representations/consumers differ, or do not demonstrably differ, on the prespecified task and population. |
| Shared-stage physical comparison completes | Empirical selection/deadline trade-offs under the tested load and calibration conditions; no universal safety guarantee. |
| A prerequisite remains absent | A precisely identified unexecuted stage plus reusable validated preparation, with no fabricated scores or timestamps. |

Completion means every feasible stage has produced a traceable artifact and
every dependent stage has either real qualified results or an explicit
missing-input/qualification status. Positive results are not a completion
criterion. Update paper claims only after matching the executed evidence to
this table; retain all null findings, limitations, and version boundaries.
