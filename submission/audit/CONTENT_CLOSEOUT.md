# Editorial closeout after the held-out content measurement

Date: 23 November 2026 (Australia/Melbourne).
Starting results commit: `8fc18a981de06af1f46df365f2345703a52cbc67`.

## Completed changes

The main paper and supplement now distinguish the original CICIoT2023
content-evidence limitation from the completed, separate CICIoMT2024 study.
The historical design discussion cross-references Supplementary Section XXIX;
the current code/evidence table no longer labels that later study as pending.

The content paragraph identifies source-capture scenario labels and reports
the 1/33/313-byte information encodings alongside their configured padded
payloads of 256/16,384/131,072 B. The supplement states that event creation
precedes encoding of an already extracted feature window. Offline packet
capture and feature extraction are outside that clock interval.

The supplement adds the retained prediction counts below. Each method uses
the same 24 attack-scenario and 48 benign test windows.

| Representation | TP | FN | FP | TN | Attack recall | FPR |
|---|---:|---:|---:|---:|---:|---:|
| Alert | 18 | 6 | 3 | 45 | 75.00% | 6.25% |
| Summary | 17 | 7 | 3 | 45 | 70.83% | 6.25% |
| Full | 19 | 5 | 14 | 34 | 79.17% | 29.17% |

Full therefore yields a net one additional true positive and eleven additional
false positives relative to alert. No general detection-value ordering is
claimed. Only three captures are held out; class, device and attack subtype
remain confounded. The original CICIoT2023 lineage limitation and the separate
shared-stage controller's all-reject outcome remain explicitly reported.

The content README explains the frozen `wire_accounting` enumeration:
it defines the scope for a supplied wire-byte observation, not a status
assertion. The measured records contain no header or retransmission byte
observations. Frozen protocol fields, code, parameters, model files and
predictions were preserved.

## Source and evidence preservation

All 48 content-study files other than the explanatory README and its checksum
manifest are byte-identical to the starting commit. Only the README entry was
updated in that directory's checksum manifest. The earlier 120-file frozen
scientific set, formal statements, labelled equations and abstract pass the
existing revision validator.

No model was refitted and no hardware activity was repeated. Running the
public verifier reconstructed existing results in a temporary directory;
it did not create new experimental observations.

## Actual build and page review

Both documents were compiled with genuine IEEEtran and three pdfLaTeX passes,
with shell escape disabled. The actual engine and source/asset identities are
recorded in [PDF_BUILD_METADATA.json](PDF_BUILD_METADATA.json).

| Document | Pages | Source SHA-256 | PDF SHA-256 |
|---|---:|---|---|
| Main | 14 | `692adde9dfe13b0b7276ae791a9ea1836f87f027880db4a5f47521697ee12be9` | `163c389226cd18f616c3aa506fcf5f5345a08301bd79dea9d52cc794d8dd1bbd` |
| Supplement | 36 | `96db05656445455ce06c2b71f75f92bef1b3b946e3cd217420e64dbcda43ece2` | `a4357adfb5f9ec20c74e79a172879c9ea06ce401e6cb90c2fb59b4540c44d86a` |

Final logs contain no overfull boxes, unresolved references/citations or missing
characters. Nonfatal inherited notices remain in the build metadata. The first
main-paper build overflowed to 15 pages; concise wording of the same content
restored 14 pages without changing the document class, margins, fonts, evidence
or references.

All 50 pages were reviewed in 13 rendered contact sheets. Detailed checks
covered main pages 13 and 14 and supplementary pages 33, 35 and 36.
The final supplementary rebuild is pixel-identical, page for page, to the
36 reviewed renders. No visible clipping, overlapping elements or missing
glyphs were observed. A rotation-aware bounds check found no text blocks
outside any page.

## Local verification and delivery

The nine checks in [CONTENT_CLOSEOUT_CHECKS.json](CONTENT_CLOSEOUT_CHECKS.json)
all passed, including the public content reconstruction and the full PR
whitespace check against main. Existing claim, citation, frozen-evidence and
methodology gates remain enabled.

The complete ZIP contains the current repository files except the generated
`review_package/` directory, plus its per-file SHA-256 manifest. The Overleaf
ZIP contains the same two paper sources, required figures/tables, PDFs and
cover-letter text. Current archive identities are recorded outside the ZIPs in
[`review_package/PACKAGE_MANIFEST.json`](../../review_package/PACKAGE_MANIFEST.json)
to avoid self-referential hashes.

The author submits the paper. GitHub changes remain on PR #3's draft review
branch; main is not merged.

## Final delivery documentation reconciliation

The subsequent delivery check confirmed that the editorial closeout was
already present at remote commit `c841c95c4f0c546bc73cebb30e0f139a3a8d395a`,
with successful push and pull-request integrity runs. Its two PDFs, their
source and asset hashes, both archive manifests, and all 48 preserved
content-study files were independently checked against the retained checkout.
The existing content records again reproduced 63/62/0 timely-correct returns,
120 service rounds and 10,635,264 application-payload bytes.

This final documentation pass updates the cover letter, experiment landing
page, reproduction entry points and current evidence table to acknowledge the
completed separate content study. The old pre-collection checkpoint is
explicitly historical. The paper sources, both PDFs, figures, models, protocol
and measured results remain byte-identical to `c841c95`. The unchanged 14-page
main and 36-page supplement were freshly rendered and all 50 pages visually
checked; the renders match the preceding closeout page for page. Archive
contents and applicable checksums are refreshed for these documentation edits.
