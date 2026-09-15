# Reference audit — 15 September 2026 revision

## Scope

The revised main manuscript has **35 unique, cited bibliography entries**: the
29 original entries are preserved, with six focused additions. Entries are
ordered by first citation. The citation-resolution check is separate from
source verification: a resolving citation does not by itself verify a paper.

This round checked the relevance and bibliographic sources for the six additions
below. It did **not** re-fetch all 29 inherited entries. The historical audit is
retained in `audit_history/integrated_20260914/REFERENCE_AUDIT.md` as history,
not a claim that its checks were repeated on this date. No arbitrary reference
count target was used, and no unrelated Kubernetes/K3s citations were added.

## `zhang2021emp`

EMP: Edge-assisted multi-vehicle perception (2021). DOI: `10.1145/3447993.3483242`.

**Use in this paper:** Compare data-partition/upload decisions with evidence representation constraints.

**Verification basis:** ACM indexed publication record gives 25 October 2021; author paper confirms method and author list. The delayed MobiCom 2021 conference was held in 2022; use canonical proceedings publication year 2021.

- https://dl.acm.org/doi/10.1145/3447993.3483242
- https://feng-qian.github.io/paper/emp_mobicom21.pdf

## `zhu2024harbor`

Boosting collaborative vehicular perception on the edge with vehicle-to-vehicle communication (2024). DOI: `10.1145/3666025.3699328`.

**Use in this paper:** Compare V2V-assisted collaborative perception and heterogeneous connectivity with coverage-constrained evidence admission.

**Verification basis:** Author PDF: title, nine authors, SenSys 2024, first page 141, last page 154, DOI; first and last pages visually inspected.

- https://feng-qian.github.io/paper/harbor_sensys24.pdf
- https://dl.acm.org/doi/10.1145/3666025.3699328

## `nishio2019fedcs`

Client selection for federated learning with heterogeneous resources in mobile edge (2019). DOI: `10.1109/ICC.2019.8761315`.

**Use in this paper:** Contrast communication/computation-aware client selection with the evidence-coverage objective, not with training convergence.

**Verification basis:** Author arXiv record confirms authors, abstract, ICC 2019 journal reference, and published DOI. IEEE-published literature confirms pp. 1-7.

- https://arxiv.org/abs/1804.08333
- https://ieeexplore.ieee.org/document/8761315

## `kadota2019aoi`

Scheduling algorithms for optimizing age of information in wireless networks with throughput constraints (2019). DOI: `10.1109/TNET.2019.2918736`.

**Use in this paper:** Locate freshness/throughput scheduling and explicitly distinguish selection gaps from AoI guarantees.

**Verification basis:** MIT institutional manuscript record confirms authors, journal 27(4), year and DOI; author publication list confirms pp. 1359-1372.

- https://dspace.mit.edu/entities/publication/bae10e2d-2db9-44c5-b812-9571e39e8e41
- https://abhishek-sinha-tifr.github.io/Abhishek_Sinha_resume.pdf

## `hou2009qos`

A theory of QoS for wireless (2009). DOI: `10.1109/INFCOM.2009.5061954`.

**Use in this paper:** Acknowledge prior deadline-and-reliability feasibility and timely-delivery work.

**Verification basis:** Original author paper confirms authors and joint delay/delivery-ratio/channel-reliability formulation; first page visually inspected. INFOCOM 2009 bibliographic metadata are indexed as pp. 486-494. Direct DOI/publisher fetch was unavailable, so this is not claimed as a successful DOI-registry verification.

- https://soihub.org/site/assets/files/4411/supplemental_communication_kumar_pr_theory-of-qos-infocom.pdf
- https://ieeexplore.ieee.org/document/5061954/

## `baruah1990feasibility`

Algorithms and complexity concerning the preemptive scheduling of periodic, real-time tasks on one processor (1990). DOI: `10.1007/BF01995675`.

**Use in this paper:** Attribute the established processor-demand tool used in the common-deadline byte-service specialization.

**Verification basis:** Springer publisher record confirms authors, title, volume 2, pp. 301-324, year, DOI and preemptive feasibility context.

- https://link.springer.com/article/10.1007/BF01995675

## Access limitations

Direct fetches of several publisher/DOI endpoints were blocked; verification used
accessible author papers, institutional records and publisher-indexed records as
specified above. Failed Crossref API requests are not represented as successful
registry checks. No third-party paper PDF has been bundled with this submission.
