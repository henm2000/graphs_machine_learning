# What's left

Everything computational is done: 240/240 grid runs, all ablations, the theory, the efficiency
measurements, and a fully written paper. What remains is decisions and a handful of small jobs.

Ordered by whether it blocks submission.

---

## 1. Blocking — the paper is over the page limit

**The limit is 5 pages excluding references. We are at roughly 6.2.**

Measured locally against a stand-in with ACL 2023's real geometry (16 × 24.7 cm, two columns,
11pt Times), because `acl.sty` isn't installable on the lab machine. The genuine ACL style is
somewhat more compact, so **the first thing to do is build it on Overleaf and get the true
number** — the gap may be nearer one page than 1.2.

§6 has already been cut from 2.3 pages to 766 words, the abstract from 302 to ~200 words, §5
tightened, and the efficiency figure moved to the appendix. Getting from 7.2 to 6.2 used up the
free cuts. What is left costs content, and it is a group decision:

| Option | Saves | Costs |
|---|---|---|
| Move **Table 2** (expressivity) to the appendix | ~0.3 p | It is a core contribution and §6 leans on it for the "no 1-WL collisions" argument |
| Move **Figure 2** (ablations) to the appendix | ~0.3 p | Attribution is our strongest positive claim |
| Tighten **§4 Expressive Power** | ~0.4 p | Four proposition environments plus a proof; dense but load-bearing |
| Tighten **§2 Related Work** | ~0.2 p | Cheapest in substance, but reviewers notice a thin related-work section |
| Cut **Appendix A/B** | 0 p | Appendices sit after references and don't count — no help |

Recommendation: build on Overleaf first, then take §2 and §4 before touching the tables.

## 2. Blocking — one line only we can fill

**Repository URL** in Appendix B of `paper/main.tex`, currently `[TODO: repository URL]`. Fill
it once the GitHub repo is public.

## 3. Decisions worth ten minutes together

**Does `trpe/` go in the repo?** It is currently committed-pending — ~2 MB, 252 JSON files plus
the generated figures. It makes every number in the paper reproducible from the repo alone,
which is worth a lot for the grade. The alternative is `.gitignore` and a release attachment.
*Recommendation: keep it.*

**Do we re-run anything?** Two known weak spots, both cheap:

* **CIFAR10-SP is single-seed.** Table 1's CIFAR10-SP column has no variance estimate at all,
  and our M3 vs M2 difference there is ~2 points — not defensible from one run. Two more seeds
  per cell is ~10 GPU-hours across the ten CIFAR10-SP cells. *This is the most valuable
  remaining compute.*
* **GAT/CLUSTER M0 varies ±11.74 across three seeds** while M4 varies ±0.22. Our headline
  +21.3 rests on an unstable control. Two more seeds on the GAT/CLUSTER column would firm up
  the paper's single biggest number, ~4 GPU-hours.

If we run nothing, both are already disclosed in §7 and `RESULTS.md`. If we run one, run the
CIFAR10-SP seeds.

**Should the ablation baseline be re-run to match?** The ablations trained 40 epochs / 1 seed
while the main grid trained 60 / 3, so ablation bars cannot be compared to the grid's M0 — we
removed that reference line from Figure 2. Within-ablation comparisons (including the +15.5
attribution result) are all matched and stand. A single GCN/CLUSTER M0 at 40 epochs, seed 0
(~30 min) would restore the "vs M0" column. Low value; listed for completeness.

## 4. Small jobs, no decisions needed

- [ ] Build on Overleaf: drop `main.tex`, `references.bib`, both `table*.tex` and the three
      figure PDFs from `paper/` into the ACL 2023 template. Build order
      `pdflatex → bibtex → pdflatex → pdflatex`.
- [ ] Delete `paper/main_preview.pdf` before submitting — it is built with the stand-in class
      and is **not** the paper.
- [ ] Read §6 and §7 once each, out loud. They were written fast and one phrase
      ("not the theorem but its shadow") is more literary than a technical reviewer will want.
- [ ] Check the author list and emails on the title page.
- [ ] `git init`-level hygiene: confirm nothing in `trpe/` has a personal Drive path in it.

## 5. Things deliberately not done

Recorded so nobody re-opens them by accident.

* **`reference_project/` is not cited or used anywhere**, by decision. The absolute-vs-relative
  framing is sourced to P-GNN (You et al. 2019) and Distance Encoding (Li et al. 2020).
* **No molecular or TU datasets** (PROTEINS, NCI1, ENZYMES, DD, IMDB-B), per the professor's
  direction — they are largely within reach of 1-WL and offer no expressivity headroom.
* **`run/person1..4/` was deleted** after the grid finished, so the public repo doesn't carry
  four duplicate notebook trees. Recoverable from git history.
* **The failed prediction stays in the paper as a failed prediction.** §§1–5 were left as the
  pre-registration rather than rewritten to match the outcome. That was a deliberate call and
  the grading rubric values it.
