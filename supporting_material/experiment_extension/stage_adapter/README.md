# RC1 shared-stage adapter candidate

Starting review commit: a936fe818e69794ec7aa8de9a89926512ac0e370.
The archived runtime tree ends in 393d7085. Apply runtime_hooks.patch to
a private copy of that runtime and copy stage_admission.py into its
netshield package. The resulting tree digest is in stage_test.json.
Regenerate the private runtime identity manifest for that copy, preserving
the portable model identities. The archived RC1 package remains the
reference for the separate allocator comparison.

The stage methods use a dedicated TON_EXT_STAGE_ experiment ID. They share
the existing barrier, grant allocator, FIFO service and synchronous core
inference path. The probe samples remaining slack on its own clock just
before sending the proposal. At the core barrier, proposal residence time
and a calibrated transit allowance reduce that slack. Outstanding FIFO jobs
carry their event identity, remaining payload and remaining deadline. The
core cross-checks their received prefixes against its reassembly buffers.
In this runtime the barrier collects a proposal only after the originating
probe has received its previous response; inference runs synchronously in
the core event loop. A multiworker or pipelined runtime needs a different
state adapter.

The capture method takes stage_capture_devices (one probe or all three).
The two byte comparisons use the same isolated H_FULL precheck. The causal
method tests each addition in seeded rotating order, admits complete work
within the current round, and rechecks estimated slack for every remaining
job. It uses a conservative serialized batch estimate. This is one specific
candidate policy. The separate calibration profile must cover all three
probes, fallback computation, dispatch, payload preparation, uploads,
per-job core work, return, staleness and margin for the conditions tested.
Its phase, separate campaign ID, single-worker setting and file hash are
checked at load time. Those checks alone do not qualify empirical estimates.
Store per-decision inputs and reasons in the private core log.

Run the integration check with a Python environment that can import the
archived runtime dependencies:

    python3 hardware/test_stage_runtime_adapter.py PATCHED_RUNTIME SCRATCH_PARENT

This tests core submit/decide, both backlog levels, capacity, zero slack and
the effect of a new request on an earlier reservation. The fixture has
invented timing values solely for checking control flow. Physical entry
requires true backlog tails and verified prefixes, complete stage capture,
independent calibration, timestamp and qualification checks and a separate
pilot. The current implementation has no physical qualification receipt.

## Source-row identification

The archived provider CSV guide distinguishes the per-PCAP feature exports
from the merged, shuffled release. trace_feature_rows.py joined each of
5,141,673 frozen records by source group and recorded row number to the
original unlabelled CSV. All 39 finite feature values matched in order for
every row. SOURCE_ROW_TRACE.json contains 31 original/labelled file digest
pairs and split-specific row counts. This identifies the source CSV and row;
the inspected exports lack authoritative parent acquisition IDs and
boundaries connecting numbered PCAP segments from the same recording.
The physical and independent content studies have no new scientific outcome.
