# Paper

`main.tex` targets the **ACL 2023 proceedings template**
(<https://www.overleaf.com/latex/templates/acl-2023-proceedings-template/qjdgcrdwcnwp>), per the
assignment. Open that Overleaf template and replace its `main.tex` with this one, keeping
`acl.sty`, `acl_natbib.bst` and the ACL style files in place. Add `references.bib`.

Build: `pdflatex → bibtex → pdflatex → pdflatex`.

Limit is **5 pages excluding references**; the appendix is short and can be cut first if the
body runs over.

## What is already written

Sections 1–5 are complete and do **not** depend on any experimental result:

| § | Status |
|---|---|
| 1 Introduction | done |
| 2 Related Work | done |
| 3 Method | done |
| 4 Expressive Power | done — all three propositions and their witnesses are confirmed by `shared/01_expressivity.ipynb`, which has already been run and produces exactly the claims stated |
| 5 Experimental Setup | done |
| 6 Results and Discussion | `TODO` markers, one per paragraph |
| 7 Limitations and Conclusion | limitations written; conclusion is a `TODO` |
| Abstract | written except the headline sentence |

## Filling in the results

`shared/07_results_and_figures.ipynb` writes every asset to Drive. Copy them next to `main.tex`:

| Asset | Written to | Goes in |
|---|---|---|
| `table1_main.tex` | `trpe/paper_tables/` | Table 1 — uncomment the `\input{table1_main}` line in §6 |
| `fig_ablations.pdf` | `trpe/figures/` | Figure 2 (radius sweep + the rewire-only control) |
| `fig_efficiency.pdf` | `trpe/figures/` | Figure 3 (preprocessing cost, edge blow-up) |
| `fig_distance_profile.pdf` | `trpe/figures/` | Appendix A |
| `fig_curves.pdf` | `trpe/figures/` | Appendix, if space allows |

Table 1 uses `multirow` and `\rotatebox` (from `graphicx`); both are already in the preamble.

Then write the four `TODO` paragraphs in §6, the conclusion, and the abstract's headline
sentence. Each `TODO` says what the paragraph has to establish, in the order that makes the
argument follow.

## Two things not to lose in the write-up

**Proposition 3 is our own upper bound.** Neither variant separates the 4×4 rook's graph from
the Shrikhande graph. A paper that states an expressivity result without stating its ceiling
invites the reader to assume there isn't one, and the rubric explicitly values negative results
that come from sound methodology.

**The rewire-only control decides how §6 is phrased.** The main grid shows whether M3 beats M0;
it cannot show why, because rewiring helps on its own by relieving over-squashing. If
`rewire-only` matches M3 in the ablation, the accurate claim is that we contribute a rewiring
scheme, not a positional encoding — and the paper should say that plainly rather than lean on
the M3-vs-M0 gap.
