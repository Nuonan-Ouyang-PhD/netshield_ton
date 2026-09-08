# Cover letter — final V4.2 draft

Dear Editor-in-Chief,

Please consider our manuscript, **“NetShield: Shared-Bottleneck Evidence Scheduling for Multi-Probe IoT Edge Intrusion Detection,”** for publication in *IEEE Transactions on Networking*.

The manuscript studies a networking problem that arises when multiple edge intrusion-detection probes generate evidence over a common constrained service path. Rather than treating detector accuracy and communication as independent, NetShield separates per-probe queue-aware evidence selection, deterministic joint pre-admission against a shared bottleneck, common queue-drain service, and optional feasibility shielding. The frozen campaign retains DPP method labels for provenance, but the manuscript deliberately does not claim a globally optimal joint scheduler or a full Lyapunov-optimal implementation. The paper evaluates the mechanism hierarchy on a heterogeneous Raspberry Pi 5/4B/3B+ Wi-Fi testbed.

The formal paper-eligible campaign contains 12 independently seeded sessions, three shared-capacity regimes, six methods, 216 method–capacity arms, 648 device-runs, and 58,320 measured probe-windows. The primary statistical analysis uses the physical session as the inferential unit. The results show that fixed-full evidence generation can retain strong nominal detector quality while producing persistent backlog and stale evidence; independent queue-aware drift-plus-penalty control removes most backlog, and network-wide pre-admission further reduces generated demand while eliminating the residual queue. Central-DPP and shielded-DPP select identical actions in all 9,720 measured windows per method, so the shield result is reported conservatively as non-interference under the evaluated feasible envelope rather than as a superiority claim.

A reproducibility package with frozen statistics, generated tables and figures, exact session-level contrasts, action-consistency results, and checksum provenance accompanies the work. A separate supplementary PDF reports the complete 75 pairwise contrasts and additional diagnostics.

The NetShield manuscript has not been published previously, is not under concurrent review at another journal or conference, and has no prior conference, journal, or public-preprint version. All authors have approved this submission. For completeness, we disclose our related ACISP 2026 publication: N. Ouyang, A. Shatte, Z. Lu, C. Chen, and W. Xiang, **“SoK: Telemetry-Aware Runtime Assurance for Always-On On-device Intrusion Detection,”** *Information Security and Privacy (ACISP 2026), LNCS 16794*, pp. 163–183, Springer, 2026, https://doi.org/10.1007/978-981-92-3018-1_7. That paper is a Systematization of Knowledge and presents TQS-IDS only as a non-implemented design template/interface specification. It does not contain the NetShield shared-bottleneck formulation, DPP/joint-pre-admission mechanisms, Raspberry-Pi S01–S12 campaign, or any of the empirical results reported in this manuscript. We cite the SoK in the submitted manuscript and explicitly state this relationship in the Related Work section.

Thank you for considering this work. We believe its focus on shared-bottleneck control, queue freshness, real-system measurement, and statistically disciplined multi-probe experimentation fits the networking systems and security scope of *IEEE Transactions on Networking*.

Sincerely,

Nuonan Ouyang  
Corresponding Author  
College of Science and Engineering  
James Cook University  
E-mail: nuonan.ouyang@my.jcu.edu.au
