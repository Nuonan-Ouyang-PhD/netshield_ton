# Analytical additions: provenance and scope

These are self-contained derivations added during manuscript editing, not measured findings.
Existing empirical NUMBER_PROVENANCE.csv is intentionally unchanged.

This is the historical analytical-additions record. For current code/evidence
corrections, see [CODE_EVIDENCE_ALIGNMENT.md](CODE_EVIDENCE_ALIGNMENT.md) and
[METHODOLOGY_VALIDATION_REPORT.md](METHODOLOGY_VALIDATION_REPORT.md).
Byte-service completion in the archived software is upload completion, not
detector/core/result-return completion. Quantile examples remain analytical
planning examples and do not establish detection value or a physical deadline.

| Quantity | Value / relationship | Derivation / location |
|---|---|---|
| Mid residual per probe | 131072/3 B = 128/3 KiB; 43,691 B / 42.7 KiB rounded | Main III-F; Supplement III |
| Round downgrade probability | Pr(J > h(C)) | Binomial request count, independent within a round; Supplement IV-A |
| Expected admitted full count | E[min(J,h(C))] | Count-maximizing summary-preserving rule, empty incoming queues |
| Minimum planning budget | nS + (B-S) q_epsilon | Smallest upper-tail request-count quantile |
| Illustrative tail above 1 | 20/27 | J ~ Binomial(3,2/3), NOT a measured QPG distribution |
| Illustrative tail above 2 | 8/27 | Same illustrative distribution |
| Illustrative capacity | 278528 B = 272 KiB | n=3, B=131072 B, S=16384 B, epsilon=1/3, q=2 |
| Illustrative expected admitted / downgraded | 46/27 / 8/27 per round | min(J,2) and J-min(J,2) |
| Normalized admitted-count limit | min(p, min(1,(rho-sigma)/(1-sigma))) | Fixed rho >= sigma, B, S, p; convergence and boundedness |
| Heterogeneous count optimum | Largest feasible prefix of increasing incremental costs | Equal positive value; exchange/lower-cost-subset proof |
| Weighted counterexample | Capacity 3, cost/value (2,2) and (3,3) | Equal density does not justify cheaper-first weighted selection |
| Continuous slope | -(1-sigma)/sigma; magnitude 7 at sigma=1/8 | Only on a nondegenerate feasible active-line segment |
| Discrete slack Pareto example | (m,k)=(3,0), C=B, S=B/8 | Universal coverage cannot be maintained after a full upgrade |

Historical implementation in the supplied integrated package:
`build/check_analytical_extensions.py` (not included at that path in the clean
repository). The archived execution reported 13 groups and 6555 cases of
small-case enumeration and arithmetic regression. This historical statement
does not claim the script was rerun by the present correction. The large-n
bound checks are finite regressions, not a numerical proof of the limit.
No empirical schedule, CSV, denominator, confidence interval or controller policy was changed by these calculations.
