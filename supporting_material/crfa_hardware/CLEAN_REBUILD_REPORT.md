# Clean ZIP rebuild report

Status: PASS.

A preflight ZIP was extracted into a new directory. All 94 delivery-manifest
entries verified before rebuilding. Generated PDFs, auxiliary files and logs were removed
from the extracted copy, then `bash build/rebuild.sh` was executed from source.

Outcomes: candidate checks 84/84 PASS; integration checks 21/21 PASS;
analytical checks 13/13 groups PASS (6555 cases). Main: 13 pages; supplement: 28 pages.

All 13 main and 28 supplementary pages rendered identically to the delivered working
build at 72 dpi (SHA-256 equality on every page's raw raster buffer). This comparison
ignores potentially varying PDF metadata by comparing page renderings, not PDF bytes.
No empirical experiment or original bootstrap analysis was executed.

This report was added after the clean test. The final ZIP manifest was regenerated and
independently verified after addition; no manuscript, figure, table or evidence file
was changed between this rebuild and the final packaging.
