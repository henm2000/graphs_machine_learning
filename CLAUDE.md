# Traversal-Based Relative Positional Encodings for GNNs

TAU course project, *Machine Learning with Graphs*. Four students: Chen Mizrahi, Tomer Zalberg,
Ofek Tovli, Itay Korenfeld. Deliverable is a 5-page ACL paper plus the notebooks that produced it.

`project/` is ours. `reference_project/` is a previous semester's project by friends — see the
constraints below.

## Two hard constraints

1. **No molecular or TU datasets.** The professor directed us to GraphBench/OGB benchmarks with
   *predefined splits*, and away from molecular data, which "usually [is] ok with 1-WL GNNs" and
   so has no expressivity headroom. This killed the PROTEINS/NCI1/ENZYMES/DD/IMDB-B family named
   in the original proposal. Datasets are now **CSL, CLUSTER, CIFAR10-SP** from
   `GNNBenchmarkDataset`.
2. **`reference_project/` is never cited or used.** The user decided the paper stands purely on
   published literature. The absolute-vs-relative comparison is sourced to P-GNN (You et al.
   2019) and Distance Encoding (Li et al. 2020) instead. Do not reintroduce it without asking.

## The method, and the one thing that is easy to get wrong

BFS to depth `r` from every node → rewired graph `E_r = {(u,v) : 1 ≤ d(u,v) ≤ r}`, each edge
carrying its hop distance `d(u,v)` sinusoidally encoded. A pairwise encoding is vacuous on a
sparse graph (every edge is at distance 1), which is why rewiring is required at all.

The encoding enters through **two channels, and channel 2 is not optional**:

1. *Edge weighting* — GAT: attention-logit bias via `GATConv(edge_dim=)`. GCN: learned scalar
   gate as `edge_weight`.
2. *Node distance profile* — `p_v = Σ_{u : 1≤d(u,v)≤r} γ(d(u,v))`, concatenated to `x_v`.

**Channel 1 alone is provably useless on vertex-transitive graphs with uniform features.** GCN's
symmetric normalisation forces `Σ_u ŵ_uv = 1` for every `v` regardless of the weights, so the
layer returns `Wx` for any `w`; GAT's softmax does the same. We found this the hard way — the
weight-only model scored exactly chance on CSL. It is now Proposition 5 in the paper, with proof.
A *sum* is not renormalised, which is why channel 2 survives.

Conditions: **M0** no PE (control) · **M1** LapPE · **M2** RWPE · **M3** T-RPE (ours) ·
**M4** M3 + shortest-path counts. Each × {GCN, GAT} × 3 datasets = 30 cells.

## Layout

`project/` is the git repository root, and this file sits in it.

```
project/
  README.md    front page: findings, layout, protocol, how to reproduce
  PLAN.md      the research plan and the reasoning behind each decision
  TODO.md      what is left to decide, for the group session
  RESULTS.md   log of confirmed numbers   <- read this first for status
  shared/      00 setup+diagnostic · 01 expressivity · 05 ablations · 06 efficiency · 07 collect
  gcn/ gat/    {csl,cluster,cifar10sp}/M0..M4  — 30 self-contained leaf notebooks
  paper/       main.tex (ACL) + generated tables/figures, references.bib, README.md
  trpe/        merged results: 240 run JSONs, ablations, expressivity, efficiency, figures
```

`run/person1..4/` held per-person copies for the parallel run. **Deleted 2026-08-08** now that
the grid is complete, so the repo can be pushed publicly without four duplicate notebook trees.
Recoverable from git history; the only files unique to it were `05_ablations_partA/partB.ipynb`,
whose ten variants are all present in the canonical `shared/05_ablations.ipynb`.

**Every notebook is self-contained** — no shared module, no cross-notebook imports. That was the
user's explicit instruction; do not refactor into a package.

**The 30 leaf notebooks were generated from one template** by a script in a session scratchpad
that no longer exists. To change all of them, write a new script that edits the `.ipynb` JSON
programmatically — never hand-edit 30 files, they will drift.

There is no longer a second copy of any notebook, so edits no longer need mirroring.

## Status

**All phases complete (2026-08-08).** 240/240 grid runs, 10/10 ablations, theory, efficiency.
The merged result tree lives in the repo at `project/trpe/`. Read
[`RESULTS.md`](RESULTS.md) for every number. The three that matter:

* **The registered sparse-vs-dense prediction FAILED, in the opposite direction.** The largest
  gain anywhere is GAT/CLUSTER M4 `69.85` vs M0 `48.57` (+21.3) — on the dataset the diagnostic
  called DEGENERATE. CIFAR10-SP, the predicted best case, moved +2.5 (GCN) and −0.1 (GAT).
  Reported as a failed prediction; §§1–5 were deliberately left as the pre-registration.
* **The real axis is injection, not sparsity.** Same dataset and encoding, different backbone:
  GCN −2.2, GAT +18.0. M3/M4 never beat M0 under GCN on any non-CSL dataset. This is
  Proposition 5's mechanism outside the setting where it was proved, and it is now the paper's
  one positive claim.
* **Attribution holds.** `r2 − rewire-only = +15.48` at matched budget, so the gain is not the
  rewiring. But `rewire-only` collapses to `20.64` (chance is 16.7%), so the honest reading is
  symmetric — a constant edge feature on a 3.3×-denser graph is destructive.

Known caveats, all recorded in RESULTS.md and §7: M0 controls sit below published figures
(GCN/CLUSTER 39.89 vs ~47–54); CIFAR10-SP is single-seed; ablations ran a shorter schedule than
the grid, so only within-ablation comparisons are valid (Figure 2's M0 line was removed).

## Paper

`project/paper/main.tex`, ACL template, 5 pages excluding references. **Fully written** —
§6, the conclusion and the abstract headline were filled 2026-08-08. The only hand-filled item
left is the repository URL in Appendix B. All tables and figures are generated by
`shared/07_results_and_figures.ipynb` (which now also emits `table2_expressivity.tex`) and
copied into `paper/` — nothing is transcribed by hand. **Page count is unverified**: `acl.sty`
is not installed locally, so the 5-page limit must be checked in Overleaf.

Five propositions, all with executable witnesses: 1-WL ⊊ T-RPE (decalin/bicyclopentyl, CSL);
T-RPE ⊉ 3-WL (rook vs Shrikhande, SR(16,6,2,2)); shortest-path counts strictly help (minimal
6-node witness, and CSL(41,6) vs CSL(41,16) on a real benchmark); permutation equivariance; and
Prop. 5, the injection-cancellation result above.

## Working notes

* **Results are resumable via skip-if-exists.** A run whose JSON exists is skipped. So **when the
  model changes, stale JSON must be deleted** or notebooks "finish" instantly with old numbers.
* Results live in the user's Drive at `MyDrive/trpe/results/{arch}/{dataset}/`; datasets go to
  `/content/trpe_data`, local and ephemeral by design.
* Each person mounts their own Drive, so results must be merged into one tree before notebook 07.
* The smoke-test gates in README.md's *Reproducing* section exist because the grid is ~27
  GPU-hours. They have already paid for themselves once.
* Predictions computed before a run are the project's main methodological asset. The CSL
  ceilings were registered in advance **and held**; the sparse-vs-dense contrast was registered
  in advance **and failed**. Both are worth more than an unregistered result either way — keep
  registering, and never retrofit §§1–5 to match an outcome.
* Report negative results as findings. Prop. 5, the failed prediction, and the sub-3-WL ceiling
  all belong in the paper; the grading rubric explicitly values them.
* When a comparison isn't budget-matched, say so or drop it. The ablations ran 40 epochs / 1
  seed against the grid's 60 / 3, which invalidated every "vs M0" delta in that table.

## What the user wants next

The compute is finished. Open items live in [`TODO.md`](TODO.md) — the page limit is the only
blocking one. The user runs notebooks and pastes output back; numbers go into `RESULTS.md`
first, then the paper, and every table and figure comes from notebook 07 rather than by hand.
