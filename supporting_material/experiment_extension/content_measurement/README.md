# Held-out content and timely correctness

The independent cohort comes from CICIoMT2024. The ten selected CSVs matched the corresponding feature files in the distribution byte for byte. Libpcap read every packet in the ten paired captures. The earliest and latest packet timestamps of each capture are disjoint across splits. The original CICIoT2023 rows still lack verified parent acquisition boundaries.

The publisher describes seven Wi-Fi power-on experiments with one device powered at a time. The attack windows come from the published ARP spoofing, port scan and malformed MQTT scenarios. Each source capture stays in a single split. Each contributes 24 hash-selected rows. The 96 training, 72 validation and 72 test windows come from four, three and three captures. The test covers two power-on devices and one malformed MQTT capture in this testbed. This design does not separate class from device or attack subtype. [Publisher and data access](https://www.unb.ca/cic/datasets/iomt-dataset-2024.html) · [Collection methodology](https://doi.org/10.1016/j.iot.2024.101351)

| Representation | Information bytes | Padded application bytes | Correct / 72 | Timely returns / 72 | Timely and correct / 72 |
|---|---:|---:|---:|---:|---:|
| Alert | 1 | 256 | 63 | 72 | 63 |
| Summary | 33 | 16,384 | 62 | 72 | 62 |
| Full | 313 | 131,072 | 53 | 0 | 0 |

Each physical arm started with empty queues. Three probes sent one observation per probe per generation round over Wi-Fi, with a shared 131,072-byte uplink allowance each second and a one-second return deadline. Each of six matched blocks tested all three representations in balanced order. All 216 physical executions returned a result. In particular all 72 full results were late. The richer representation yielded ten fewer correct decisions than alert on these test windows before applying the deadline. The full-minus-alert descriptive 95% capture-bootstrap interval for that accuracy difference spans zero. The complete-case comparison uses only three held-out captures, and the imposed low allowance limits the transport finding to the tested load.

## Verify the public results

From the repository root run

```sh
python3 -B supporting_material/experiment_extension/content_measurement/verify_public.py
```

This checks the frozen three-way pairing, model and encoder identities, labels, scores and payload hashes. It reconstructs the transport scores and byte conservation for every service round. The public ledger uses role-specific clock origins. Within-device nanosecond differences and return classifications are preserved. The byte counts measure application evidence. Per-event physical header and retransmission bytes are unavailable.

[Parent PCAP and CSV hashes, counts and timing boundaries](parent_evidence.json) · [Window audit](input_audit.json) · [Exact source rows and sample ranks](sample_manifest.json) · [Frozen design](design.json) · [Physical queue](schedule.json) · [Information-only report](information/score.json) · [Measured transport report](transport/score.json) · [Service audit](transport/service_audit.json)

## Reconstruct the inputs and measurements

Obtain the Wi-Fi/MQTT PCAP and CSV files from the publisher or use the hash-identified [archived distribution](https://www.kaggle.com/datasets/cyberdeeplearning/ciciomt2024). The separate [profiling](https://www.kaggle.com/datasets/zeynepdemirta/ciciomt2024-profilling) and [attack CSV](https://www.kaggle.com/datasets/zeynepdemirta/ciciomt2024-attacks) mirrors were checked against the archived copies. The archive SHA-256 and individual member paths are recorded in the parent register. The public package contains source identities and derived results.

Use an empty study directory on the research disk and copy the acquisition scripts there. The original frozen CICIoT2023 manifest only supplies the 39-column order to `audit_windows.py`; on another host set its manifest location to your copy or use the feature list in `input_audit.json`. Copy the published design and save the original distribution and the two feature archives as `original.zip`, `profilling.zip` and `attacks.zip`. Extract `CICIoMT2024.tar.xz` from the original ZIP as `source.tar.xz`. With Python 3.12, NumPy and libpcap, run the following in the fresh directory.

```sh
cc -o capture_bounds capture_bounds.c -lpcap
python3 -B audit_windows.py
python3 -B inspect_distribution.py
python3 -B qualify.py
python3 -B prepare_study.py schedule
python3 -B prepare_study.py "$REPO"
python3 -B "$REPO/supporting_material/experiment_extension/evidence_value/run_content_study.py" spec.json information
python3 -B verify_transport.py setup
```

For a separately registered hardware replication, use the enrolled Pi 5 and two Pi 4 probes, a Wi-Fi Core, authenticated management paths, the study's health checks and exclusive experiment lock. Run the hardware preflight from the enrolled deployment into `ready/`, then run `launch_transport.py "$REPO" "$DEPLOYMENT" "$LOCKFILE" "$NEW_ATTEMPT"` and `verify_transport.py "$REPO" "$NEW_ATTEMPT"`. Only numerical representations and padding travel on the measured connection. Device credentials, original endpoint identifiers and raw captures remain in the research archive.
