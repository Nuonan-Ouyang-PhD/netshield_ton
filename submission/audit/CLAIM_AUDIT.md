# Claim audit — editorial revision, 15 September 2026

This revision changes presentation and literature positioning, not the experimental
record. `build/baseline_invariants.json` records hashes from the supplied INTEGRATED
source. `build/validate_revision.py` checks them against the revised source.

## Preserved scientific scope

- Seven formal theorem/proposition/corollary statements and all 20 original labelled
  equations are preserved after whitespace normalization. The QPG equation moved
  from the Introduction to III-F; its expression is unchanged.
- The rate-balance result retains its reduced-model, rate-stability and saturation
  conditions. The independence approximation is not promoted to a proved bound.
- CRFA reaches the byte frontier under its ideal-service assumptions. Physical
  attainment remains 91.7%, 94.9%, 96.6%, not a universal latency/utility guarantee.
- Mid-capacity output remains 0.2938 vs 0.6327 and the descriptive paired difference
  +0.3389, with interval [0.3306,0.3478]. No new bootstrap estimates were generated.
- The full rotating-extension/launcher limitation paragraph is unchanged, including
  nonconcurrent session matching, nominal-anchor sensitivity and future aligned reruns.
- Three-probe physical scale, fixed feature replay, detector-generalization limitations,
  safety-filter separation and security-utility limits remain explicit.

## New exposition, not new evidence

The one additional labelled equation, C_min(k)=nS+k(B-S), is a direct restatement of
existing feasibility at m=n. For B=128 KiB, S=16 KiB and n=3, two full uploads plus
one summary require 272 KiB, 16 KiB (6.25%) above the tested 256 KiB middle budget.
This is labelled an analytical capacity threshold, not an executed fourth hardware
budget or a one-second physical completion guarantee.

The short mechanism plot is a vector-only view of the first eight original rounds.
The complete 16-round figure is retained unchanged and placed in the supplement.
No trajectory, seed, summary table, hardware measurement or outcome was recomputed.

## Attribution

Related Work now acknowledges collaborative perception/upload selection, FL client
selection, AoI/throughput scheduling and timely-delivery feasibility. The classical
processor-demand tool is explicitly attributed, rather than described as a new
scheduling theorem. Reference verification scope is in `REFERENCE_AUDIT.md`.

## Evidence boundary

The 60-file frozen manifest covers all 28 evidence files, all 22 table files, the
number provenance, two protocol files, and seven original figure PDFs. The supplied
package is a results/evidence layer, not the complete external raw archive. The
historical primary raw-audit PASS_WITH_ISSUES and its disclosed archival gaps remain.
This round did not run Pis, inspect the external raw volume or remove those issues.
