# NetShield ToN Claim Audit

Status: **PASS**

## Frozen scientific content

- The abstract, RQ1--RQ4, contributions, claim boundary, system model, theorem, propositions, methodology, results, numerical tables, figures, discussion, limitations, provenance, and conclusions use the validated scientific content and the common-denominator RQ2 interpretation.
- Internal revision labels were removed from the manuscript and Supplementary title for clean first-submission presentation.
- Figure 5 was rebuilt to show conditional rates and common-denominator timely full-core output separately; the plotted values are the already validated software-sensitivity values.
- No Raspberry Pi execution, simulation, replay, or statistical analysis was run.

## Permitted changes

- Related Work received four distributed literature updates: recent lightweight/open-set IIoT IDS; security data collection and overhead; edge scheduling/admission; and remote-inference/inference-serving timeliness.
- The clean manuscript contains 30 bibliography entries, including the formal CICIoT2023 and Sommer--Paxson citations.
- The pre-bibliography `\\balance` command is present in the source. The final build emits a 0.68pt vertical balance warning on the last bibliography page; rendered inspection found no clipping, overlap, or missing content.
- The abstract, discussion, conclusion, and Figure 5 now state the validated common-denominator comparison without introducing new measurements or analyses.

## Forbidden-claim scan

- Centralized universal superiority: absent.
- Shield superiority: absent.
- Classifier superiority by NetShield: absent.
- Physical validation at n=32: absent.
- End-to-end 1-s deadline claim: absent; the frozen post-release service-SLO boundary is unchanged.
- No legacy `timely_f1` field or 0.9332/0.2845 result narrative was reinstated. The frozen sentence that explicitly rejects the historical `timely-F1` field remains unchanged.
- "NetShield is the first" priority claim: absent.

The manuscript continues to frame coordinated admission as deterministic
operating-point enforcement, not universal superiority.
