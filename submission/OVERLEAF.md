# Compiling the standalone source package

The separately delivered `NetShield_ToN_Overleaf.zip` contains both current
LaTeX documents, their figures and tables, the compiled PDFs and cover-letter
text. Its document filenames and assets are copied from this `submission/`
directory without source changes.

1. Import the ZIP as a new Overleaf project.
2. Use **pdfLaTeX** and select `netshield_manuscript.tex` as the main document.
3. To compile the supplement, select `netshield_supplementary.tex` instead.
4. Both documents use the genuine `IEEEtran` class and standard TeX packages.
   Citations are included in the sources; there is no separate BibTeX build.

The ZIP root corresponds to the repository's `submission/` directory. The
complete review ZIP also supplies the experimental evidence and repository
verification scripts. The standalone source package supplies the files needed
to compile the two papers; it is not a second experimental dataset.

The supplied PDFs were built with three pdfLaTeX passes per document. A
different TeX distribution may change PDF metadata, hashes or line breaks.
The complete-package build metadata identifies the exact delivered binaries.
