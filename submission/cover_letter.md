# Cover Letter

Dear Editor,

Please consider our manuscript, “NetShield: Timely Evidence Feasibility under
Shared Bottlenecks for Multi-Probe Edge Intrusion
Detection,” for publication in *IEEE Transactions on Networking*.

The manuscript studies how multiple edge probes share a limited uplink while
preserving timely evidence for a core service. It derives a closed-form
coverage--richness frontier, constructs a rotating admission policy that
attains the corresponding byte frontier, and measures how much of that
frontier survives a one-second result-return deadline on a heterogeneous
three-probe Raspberry Pi testbed. The rotating hardware experiment achieves
91.7%--96.6% of the analytical byte frontier across three capacity regimes.

Separate physical comparisons examine integer allocator corrections and
admission with existing backlog. They distinguish increased Full selection
from timely completion and show when backlog accounting improves timely
coverage. The manuscript reports the calibrated controller's complete
rejection outcome alongside these findings. Public results, reconstruction
scripts and explicit provenance connect the analytical claims to the measured
service outcomes.

A separate CICIoMT2024 study compares three representations on the same 72
held-out feature windows using real three-probe transmission and core
inference. Alert, Summary and Full yield 63, 62 and zero correct returns within
one second under the declared fixed padded payloads and shared budget. The
paper reports the confusion counts, recall and false-positive rates, with
conclusions limited to the stated models, capture-scenario labels and three
held-out captures.

The work is original, has not been published previously, and is not under
consideration elsewhere. All authors have approved the manuscript and agree
with its submission. The contribution concerns evidence feasibility,
admission, queue behavior and service timing, complemented by this bounded
content comparison. Broader detection generalization and incident-level
localization remain outside the validated empirical scope.

The repository includes the clean manuscript and supplementary material,
machine-readable result tables, validation scripts, and a data/reproduction
guide. Third-party source datasets and private historical hardware raw evidence
are not redistributed in the repository; their access and licensing boundaries
are documented separately. The content-study directory provides its public
model, prediction and transport records for result reconstruction.

Thank you for your consideration.

Sincerely,

Nuonan Ouyang, on behalf of all authors
