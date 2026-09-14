# Claim Audit

Verdict: **PASS for the integrated hardware evidence boundary**

## Core analytical claim checks

- PASS — The one-round coverage/richness theorem is stated as an application-byte feasibility result, not a physical latency guarantee.
- PASS — The unrestricted full-evidence frontier `K_full^max = min(n, floor(C/B))` is a byte frontier. The manuscript does not equate it with guaranteed 1-s completion.
- PASS — Universal per-round remote coverage and unrestricted full evidence are separated. The low/mid/high price of requiring every probe to remain remotely represented is 1/1/0 full-evidence slots.
- PASS — The finite-deadline condition is explicitly tied to an idealized preemptive fluid server.
- PASS — Long-run load admissibility is not presented as a universal queue-stability theorem for arbitrary bursts.
- PASS — The desynchronized `p*=rho` equality is conditional on the reduced H-FULL/H-NONE regime, rate stability, work conservation/saturation, and flow balance.
- PASS — The mid-capacity `5/9` result is labelled an independence approximation, not a proved upper bound.
- PASS — The cyclic construction is analytically defined and has both discrete-event conformance and a separately frozen hardware extension. The software check and hardware evidence are not conflated.

## CRFA hardware checks

- PASS — The extension is identified as a separately frozen 36-arm hardware campaign, not part of the original 216-arm matrix.
- PASS — 36/36 planned arms are accepted from 55 indexed attempts; 19 infrastructure attempts are retained/excluded under the frozen retry rules.
- PASS — Timing outcomes were not acceptance/retry gates; partial attempts are not stitched.
- PASS — 9,720 measured occurrences and 10,620 reconstructed shared-service rounds are reported, with zero shared-cap violations and all action/payload/reconstruction/final-drain gates passing.
- PASS — Low/mid/high CRFA timely full-core output is 0.3056/0.6327/0.9660 per generated event, corresponding to 91.7%/94.9%/96.6% of the byte frontier.
- PASS — Every selected CRFA full event eventually returns a core result; the remaining frontier gap is post-release lateness rather than missing selected evidence.
- PASS — The matched mid-capacity physical comparison is 0.2938 C-QPG versus 0.6327 CRFA; paired difference +0.3389 with descriptive 95% session-bootstrap interval [0.3306, 0.3478].
- PASS — At high capacity the paired difference is -0.0037 with interval [-0.0133, 0.0046]; the paper does not claim equivalence or superiority from this interval.
- PASS — CRFA is not described as universally superior to C-QPG. The manuscript explicitly states that CRFA assigns H-NONE to non-selected probes and trades same-round universal remote coverage for more full-evidence opportunities.
- PASS — Admission fairness and timing fairness are separated. Opportunity counts are exactly equal by device, while P1/P2/P3 have different physical post-release rates.
- PASS — CRFA versus phase-randomized I-QPG is used only as an interpretive cross-evidence contrast, not a direct hardware-versus-hardware superiority test.

## Timing-anchor checks

- PASS — The primary 1-s quantity remains a post-release service SLO, not a complete schedule-inclusive deadline.
- PASS — P1's large nominal release offset is treated as an orchestration-phase measurement, not evidence that Raspberry Pi 5 computation/inference is slow.
- PASS — The exact low-level OS/network cause of the recurring proposal-arrival order remains `UNKNOWN`.
- PASS — CRFA nominal timely-full output (0.1111/0.2222/0.3330) is reported separately from post-release output (0.3056/0.6327/0.9660), and the per-device reconstruction discloses P1/P2 nominal zero and P3 near-unity nominal timing.

## Primary campaign / replay boundaries

- PASS — The phase-randomized independent controller remains a software sensitivity, not a physical baseline.
- PASS — `n=8/16/32` remains discrete-event conformance, not physical scalability evidence.
- PASS — The classifier ceiling on formal replay is treated as a controlled replay diagnostic, not open-world IDS superiority or state-of-the-art CICIoT2023 accuracy.
- PASS — No universal centralized-over-decentralized superiority claim is made.
- PASS — No safety-filter superiority over ordinary coordinated admission is claimed.
- PASS — The historical primary raw-audit verdict remains `PASS_WITH_ISSUES`; the two archival gaps are still disclosed and are not repaired retroactively by the CRFA extension.
- PASS — The CRFA primary archive and mirror are described as residing on the same physical external volume, so no independent-backup claim is made.

## Common-denominator interpretation

At mid capacity the software sensitivity remains reported on the common 270-generated-event denominator: C-QPG 0.3333 versus phase-randomized I-QPG 0.3352, with C-QPG using 37.5% fewer application bytes. This result now serves as a mechanism-isolation sensitivity rather than the paper's strongest physical result.

The new physical result is separately reported: session-matched primary C-QPG 0.2938 versus CRFA 0.6327 timely full-core results per generated event. This is interpreted as the measured consequence of choosing different coverage/richness operating points, not as a generic centralized-controller ranking.

## Forbidden / superseded claim scan

Paper-facing source must contain no affirmative use of:

- `timely_f1`;
- legacy 0.9332 / 0.2845 / 0.9336 / 0.2823 F1/FPR values;
- old non-inferiority as a live result;
- “centralized universally outperforms decentralized”;
- “shield outperforms C-QPG” or zero shield intervention;
- strict physical 1/2/3-Mbps language;
- full/global Lyapunov or DPP optimality;
- 32-probe physical scalability;
- byte-feasibility as a guaranteed physical deadline frontier.

## Naming / presentation hygiene

- PASS — Paper-facing source contains no internal `V1.x`, methodology-repair, or Task-A/B/C/D labels.
- PASS — Current journal header is `IEEE Transactions on Networking`.
- PASS — CICIoT2023 and Sommer--Paxson are cited.
- PASS — Internal CRFA campaign/protocol identifiers appear only where necessary for evidence traceability, not as manuscript revision labels.

## Selective integration boundaries

- PASS — New capacity planning is explicitly conditional on independent within-round requests, empty incoming queues and a feasible all-summary baseline. The illustrative 272 KiB does not replace the measured 256 KiB mid budget.
- PASS — Heterogeneous cheaper-first selection is asserted only for equal positive values/full-count maximization; general weighted value remains a 0/1 problem without the imported greedy guarantee.
- PASS — The continuous exchange rate is not an integer Pareto characterization; the slack discrete counterexample and rho-domain restrictions are stated.
- PASS — Deployment guidance distinguishes admission-opportunity bounds from returned-evidence age or physical deadline guarantees. Absolute-clock scheduling remains future aligned-rerun work.
- PASS — No new empirical experiments, TOST equivalence or universal desynchronization advantage are claimed.
- PASS — Evidence and paper tables remain byte-identical to the baseline. Figure changes are label-only; curve/bar geometry and values are preserved.
