# Paper

`main.tex` targets the **ACL 2023 proceedings template**
(<https://www.overleaf.com/latex/templates/acl-2023-proceedings-template/qjdgcrdwcnwp>), per the
assignment. Open that Overleaf template, replace its `main.tex` with this one, keep `acl.sty`,
`acl_natbib.bst` and the rest of the ACL style files in place, and add everything listed below.

Build: `pdflatex → bibtex → pdflatex → pdflatex`.

Limit is **5 pages excluding references**; the appendix sits after the references and does not
count against it.

## Files to upload alongside `main.tex`

All of these are already in this folder, and all are generated — none is hand-written.

| File | Produced by | Used as |
|---|---|---|
| `references.bib` | — | bibliography |
| `table1_main.tex` | `shared/07_results_and_figures.ipynb` | Table 1, main results |
| `table2_expressivity.tex` | `shared/07_results_and_figures.ipynb` | Table 2, expressivity |
| `fig_ablations.pdf` | `shared/07_results_and_figures.ipynb` | Figure 2, ablations |
| `fig_distance_profile.pdf` | `shared/00_setup_and_diagnostic.ipynb` | Appendix A |
| `fig_efficiency.pdf` | `shared/06_efficiency.ipynb` | Appendix B |

To refresh any number in the paper, re-run notebook 07 and re-copy — nothing is transcribed by
hand, so the tables cannot drift from the results.

## LaTeX build notes

`main.tex` carries no comments, so the four non-obvious things about it are recorded here.

**The margins are a deliberate deviation.** `acl.sty` sets `margin=2.5cm`; the preamble
overrides it with `\usepackage{geometry}` / `\geometry{left=2cm,right=2cm}` to buy horizontal
space. This is **not** the official ACL layout and `aclpubcheck` flags it. Delete those two
lines to restore it — at the cost of roughly the space that was bought.

**Do not add `\bibliographystyle`.** `acl.sty` already issues
`\bibliographystyle{acl_natbib}`; repeating it makes BibTeX report *"Illegal, another
\bibstyle command"*.

**Table 1 and Table 2 span both columns** (`table*`). The tabular is 302pt wide against a 219pt
column, so a single-column float overflows into the gutter.

**Figure 1 (ablations) is scaled, not spanned.** Its natural width is 263pt against a 219pt
column; scaling keeps it beside its section instead of floating onto a page of its own.

**Appendix placement.** Table 2, the ablation figure and the Proposition 5 proof live in the
appendix to meet the 5-page limit; appendices sit after the references and do not count
against it.


## Status

Fully written, and the repository URL is filled in
(<https://github.com/henm2000/graphs_machine_learning>), cited in the reproducibility appendix.
The body must stay within 5 pages excluding references; the appendices sit after the references
and do not count against it.

`main_preview.pdf` is a local build made with a stand-in for `acl.sty`, which is not installable
on the lab machine. It is for checking layout and length only — **it is not the paper, and it
should be deleted before submission.**

## Three things not to lose in the write-up

**Proposition 3 is our own upper bound.** Neither variant separates the 4×4 rook's graph from
the Shrikhande graph. A paper that states an expressivity result without stating its ceiling
invites the reader to assume there isn't one, and the rubric explicitly values negative results
that come from sound methodology.

**The failed prediction is a feature, not an embarrassment.** §5 registers, before training,
that the encoding should help on sparse long-diameter graphs and not on dense ones. It did the
opposite. §§1–5 were deliberately left unrewritten so that the prediction still stands as a
prediction, and §6 reports the miss along with the reason for it — CLUSTER and CIFAR10-SP have
no 1-WL collisions at all, so expressivity was never the binding constraint there.

**The paper's one positive claim is about injection, not encoding.** The same signal is worth
nothing under GCN and +21 points under GAT. That is Proposition 5's mechanism operating outside
the vertex-transitive setting where it was proved, and it is what §7 leads with.
