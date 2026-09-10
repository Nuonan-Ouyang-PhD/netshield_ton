# NetShield ToN Reference Audit

Status: **PASS**

The manuscript includes 11 recent references published in 2024--2026 and
30 bibliography entries in total. Metadata was checked against
IEEE Xplore or USENIX proceedings records and cross-checked with DBLP or
Crossref where available. No ResearchGate record was used as the sole source.

Publication-quality labels use the CCF seventh-edition venue lists. The CCF
networking list identifies TON, TMC, INFOCOM, and NSDI as CCF-A; the CCF
network and information security list identifies TIFS and USENIX Security as
CCF-A.

- CCF networking list: https://www.ccf.org.cn/Academic_Evaluation/CN/
- CCF network and information security list: https://www.ccf.org.cn/Academic_Evaluation/NIS/

## Added references

### `neto2023ciciot`

- Exact title: CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment
- Authors: E. C. P. Neto et al.
- Venue: Sensors
- Year: 2023
- Volume: 23
- Issue: 13
- Article: 5941
- DOI: 10.3390/s23135941
- Official verification: https://www.unb.ca/cic/datasets/iotdataset-2023.html
- Publication quality: peer-reviewed dataset paper
- Cited in: Abstract, methodology, and detector/replay limitations
- Relevance: Formal source citation for the CICIoT2023-derived frozen feature-vector workload.

### `sommer2010outside`

- Exact title: Outside the Closed World: On Using Machine Learning for Network Intrusion Detection
- Authors: Robin Sommer; Vern Paxson
- Venue: IEEE Symposium on Security and Privacy
- Year: 2010
- Pages: 305--316
- DOI: 10.1109/SP.2010.25
- Official verification: https://doi.org/10.1109/SP.2010.25
- Publication quality: IEEE security and privacy conference paper
- Cited in: Detector and replay limitations
- Relevance: Supports the closed-world/generalisation limitation for the frozen detector evaluation.

### `yang2025openset`

- Exact title: A Lightweight and Dynamic Open-Set Intrusion Detection for Industrial Internet of Things
- Authors: Xueji Yang; Fei Tong; Fang Jiang; Guang Cheng
- Venue: IEEE Transactions on Information Forensics and Security
- Year: 2025
- Volume: 20
- Issue: N/A (no issue listed in the IEEE record)
- Pages: 2930--2943
- DOI: 10.1109/TIFS.2025.3546849
- Official verification: https://ieeexplore.ieee.org/document/10908210/
- Cross-check: https://dblp.org/rec/journals/tifs/YangTJC25
- Publication quality: CCF-A
- Cited in: Related Work / Lightweight IoT Intrusion Detection
- Relevance: Recent resource-conscious IIoT work that combines open-set detection with lightweight dynamic updates. It supports the stated open-world limitation without implying classifier superiority by NetShield.

### `mirnajafizadeh2024isdc`

- Exact title: Enhancing Network Attack Detection with Distributed and In-Network Data Collection System
- Authors: Seyed Mohammad Mehdi Mirnajafizadeh; Ashwin Raam Sethuram; David Mohaisen; DaeHun Nyang; Rhongho Jang
- Venue: 33rd USENIX Security Symposium (USENIX Security 24)
- Year: 2024
- Volume: N/A
- Issue: N/A
- Pages: 5161--5178
- DOI: N/A (none assigned in the USENIX proceedings record)
- Official verification: https://www.usenix.org/conference/usenixsecurity24/presentation/mirnajafizadeh
- Publication quality: CCF-A
- Cited in: Related Work / Security Data Collection and Evidence Overhead
- Relevance: ISDC treats defense-data collection and constrained in-network resources as a systems bottleneck. This is directly related to NetShield's evidence-collection control point.

### `oqaily2024chainpatrol`

- Exact title: ChainPatrol: Balancing Attack Detection and Classification with Performance Overhead for Service Function Chains Using Virtual Trailers
- Authors: Momen Oqaily; Hinddeep Purohit; Yosr Jarraya; Lingyu Wang; Boubakr Nour; Makan Pourzandi; Mourad Debbabi
- Venue: 33rd USENIX Security Symposium (USENIX Security 24)
- Year: 2024
- Volume: N/A
- Issue: N/A
- Pages: 3441--3458
- DOI: N/A (none assigned in the USENIX proceedings record)
- Official verification: https://www.usenix.org/conference/usenixsecurity24/presentation/oqaily
- Publication quality: CCF-A
- Cited in: Related Work / Security Data Collection and Evidence Overhead
- Relevance: ChainPatrol explicitly evaluates security visibility and classification against traffic and delay overhead, complementing NetShield's evidence coverage-richness trade-off.

### `zhao2024curcoedge`

- Exact title: Cur-CoEdge: Curiosity-Driven Collaborative Request Scheduling in Edge-Cloud Systems
- Authors: Yunfeng Zhao; Chao Qiu; Xiaoyun Shi; Xiaofei Wang; Dusit Niyato; Victor C. M. Leung
- Venue: IEEE INFOCOM 2024
- Year: 2024
- Volume: N/A
- Issue: N/A
- Pages: 411--420
- DOI: 10.1109/INFOCOM52122.2024.10621190
- Official verification: https://ieeexplore.ieee.org/document/10621190/
- Cross-check: https://dblp.org/rec/conf/infocom/ZhaoQSWNL24
- Publication quality: CCF-A
- Cited in: Related Work / Edge Offloading and Shared Network Control
- Relevance: Cur-CoEdge coordinates request scheduling across edge-cloud resources. NetShield differs because its selected security action creates the offered evidence load before admission.

### `hao2024edgetimer`

- Exact title: EdgeTimer: Adaptive Multi-Timescale Scheduling in Mobile Edge Computing with Deep Reinforcement Learning
- Authors: Yijun Hao; Shusen Yang; Fang Li; Yifan Zhang; Shibo Wang; Xuebin Ren
- Venue: IEEE INFOCOM 2024
- Year: 2024
- Volume: N/A
- Issue: N/A
- Pages: 671--680
- DOI: 10.1109/INFOCOM52122.2024.10621305
- Official verification: https://ieeexplore.ieee.org/document/10621305/
- Cross-check: https://dblp.org/rec/conf/infocom/00010F24
- Publication quality: CCF-A
- Cited in: Related Work / Edge Offloading and Shared Network Control
- Relevance: EdgeTimer adapts scheduling timescales in MEC. It motivates timing-aware scheduling context while remaining distinct from NetShield's evidence-admission semantics.

### `li2025oacr2`

- Exact title: OACR²: Online Admission Control and Resource Reservation for 5G Slice Networks With Deep Reinforcement Learning
- Authors: Fang Li; Yijun Hao; Shusen Yang; Peng Zhao
- Venue: IEEE Transactions on Mobile Computing
- Year: 2025
- Volume: 24
- Issue: 8
- Pages: 7360--7376
- DOI: 10.1109/TMC.2025.3548767
- Official verification: https://ieeexplore.ieee.org/document/10915540/
- Registry cross-check: https://doi.org/10.1109/TMC.2025.3548767
- DBLP cross-check: https://dblp.org/rec/journals/tmc/LiHYZ25
- Publication quality: CCF-A
- Cited in: Related Work / Edge Offloading and Shared Network Control
- Relevance: OACR2 jointly addresses online admission and resource reservation. NetShield instead admits security actions whose choice determines the offered load and evidence richness.

### `shisher2024timely`

- Exact title: Timely Communications for Remote Inference
- Authors: Md Kamran Chowdhury Shisher; Yin Sun; I-Hong Hou
- Venue: IEEE/ACM Transactions on Networking
- Year: 2024
- Volume: 32
- Issue: 5
- Pages: 3824--3839
- DOI: 10.1109/TNET.2024.3408673
- Official verification: https://ieeexplore.ieee.org/document/10559951/
- Cross-check: https://dblp.org/rec/journals/ton/ShisherSH24
- Publication quality: CCF-A
- Cited in: Related Work / Deadline-Aware Inference Serving and Admission
- Relevance: The work links feature freshness and scheduling to remote-inference quality. NetShield instead controls evidence coverage and richness before shared-service admission.

### `ari2026goal`

- Exact title: Goal-Oriented Status Updating for Real-Time Remote Inference Over Networks With Two-Way Delay
- Authors: Çağrı Arı; Md Kamran Chowdhury Shisher; Yin Sun; Elif Uysal
- Venue: IEEE Transactions on Networking
- Year: 2026
- Volume: 34
- Issue: N/A (no issue listed in the IEEE record)
- Pages: 4011--4025
- DOI: 10.1109/TON.2026.3670099
- Official verification: https://ieeexplore.ieee.org/document/11426757/
- Cross-check: https://dblp.org/rec/journals/ton/AriSSU26
- Publication quality: CCF-A
- Cited in: Related Work / Deadline-Aware Inference Serving and Admission
- Relevance: The paper jointly considers packet freshness, packet length, transmission timing, and two-way delay for remote inference. This is communication-oriented context rather than an identical evidence-admission problem.

### `khare2025superserve`

- Exact title: SuperServe: Fine-Grained Inference Serving for Unpredictable Workloads
- Authors: Alind Khare; Dhruv Garg; Sukrit Kalra; Snigdha Grandhi; Ion Stoica; Alexey Tumanov
- Venue: 22nd USENIX Symposium on Networked Systems Design and Implementation (NSDI 25)
- Year: 2025
- Volume: N/A
- Issue: N/A
- Pages: 739--758
- DOI: N/A (none assigned in the USENIX proceedings record)
- Official verification: https://www.usenix.org/conference/nsdi25/presentation/khare
- Publication quality: CCF-A
- Cited in: Related Work / Deadline-Aware Inference Serving and Admission
- Relevance: SuperServe uses fine-grained inference serving to handle unpredictable workloads under latency and accuracy targets. NetShield acts upstream by selecting the security evidence request itself.

### `wu2026fastserve`

- Exact title: FastServe: Iteration-Level Preemptive Scheduling for Large Language Model Inference
- Authors: Bingyang Wu; Yinmin Zhong; Zili Zhang; Shengyu Liu; Fangyue Liu; Yuanhang Sun; Gang Huang; Xuanzhe Liu; Xin Jin
- Venue: 23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI 26)
- Year: 2026
- Volume: N/A
- Issue: N/A
- Pages: 57--74
- DOI: N/A (none assigned in the USENIX proceedings record)
- Official verification: https://www.usenix.org/conference/nsdi26/presentation/wu-bingyang
- Publication quality: CCF-A
- Cited in: Related Work / Deadline-Aware Inference Serving and Admission
- Relevance: FastServe provides low-latency preemptive scheduling for already-defined LLM inference jobs. It is related SLO-aware serving context, not the same control problem as evidence generation and admission.

### `ruan2026libra`

- Exact title: Libra: Flexible Request Partitioning and Scheduling for Serving Unbalanced and Dynamic LLM Workloads
- Authors: Chaoyi Ruan; Yinhe Chen; Dongqi Tian; Yandong Shi; Yongji Wu; Jialin Li; Cheng Li
- Venue: 23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI 26)
- Year: 2026
- Volume: N/A
- Issue: N/A
- Pages: 1243--1258
- DOI: N/A (none assigned in the USENIX proceedings record)
- Official verification: https://www.usenix.org/conference/nsdi26/presentation/ruan-libra
- Publication quality: CCF-A
- Cited in: Related Work / Deadline-Aware Inference Serving and Admission
- Relevance: Libra partitions and schedules dynamic requests under strict SLOs. NetShield controls evidence semantics and byte demand before the transport-and-core service.

## Verification conclusion

All 11 additions have complete, source-supported metadata for the fields that
apply to their publication type. Conference volume/issue fields and USENIX DOI
fields are marked N/A rather than invented. The two IEEE continuous-volume
records for which Xplore does not list an issue are also marked N/A. No
unverified bibliographic field is presented as known.
