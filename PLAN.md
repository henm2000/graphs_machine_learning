# Research & Writing Plan

Traversal-Based Relative Positional Encodings for Graph Neural Networks
Course project, *Machine Learning with Graphs*, Tel Aviv University.

This is the working plan the project was built from, updated to match what actually exists.
[`README.md`](README.md) is the operational guide (how to run things); this file is the
*why* — the research question, the design decisions and the reasoning behind them.

---

## Context

**The starting point.** [`proposal.tex`](proposal.tex) proposes a deterministic **relative**
positional encoding derived from BFS traversal, sinusoidally activated, evaluated on GCN and
GAT against no-PE / LapPE / RWPE controls, with a formal expressivity claim.

**Two constraints reshaped it.**

1. **The professor's directive** — use GraphBench and/or OGB datasets with *predefined
   splits*, and avoid molecular datasets, which "usually are ok with 1-WL GNNs" and so offer
   no expressivity headroom. This ruled out the entire TU family (PROTEINS, NCI1, ENZYMES, DD,
   IMDB-B) named in the proposal. Replacements: **CSL, CLUSTER, CIFAR10-SP**, all from
   `GNNBenchmarkDataset`, all with predefined splits, none molecular.
2. **Independence** — the paper is framed purely against published literature. The
   absolute-vs-relative comparison is sourced to P-GNN \[You et al. 2019] and Distance
   Encoding \[Li et al. 2020] rather than to any unpublished work.

## The research question

Traversal-based positional encodings are almost always **absolute**: a node is described by
its distance to a handful of anchors, so the encoding inherits whatever arbitrariness went
into choosing them — a heuristic (highest degree, say) whose ties must then be broken somehow.
We ask whether an anchor-free **relative** encoding, defined on node *pairs*, is a better way
to inject global structure into a GNN, in accuracy and in expressive power.

**Design consequence.** In a sparse MPNN every edge joins nodes at distance 1, so a pairwise
encoding restricted to `E` is constant. A relative encoding is only meaningful on a rewired
graph. We follow Brüel-Gabrielsson et al. (2022): BFS to depth `r` from every node gives the
`r`-hop rewired graph, and each rewired edge carries its hop distance as a sinusoidally
encoded feature.

**The confound this creates, and why we take it seriously.** Rewiring independently helps, by
shortening paths and relieving over-squashing. So M3 beating M0 does *not* by itself credit
the positional signal. The `rewire-only` variant in [`shared/05_ablations.ipynb`](shared/05_ablations.ipynb) —
the rewired graph with a *constant* edge feature — is the only condition that separates the
two explanations, and the main result should be read against it.

---

## Method: T-RPE

For a graph `G=(V,E)` and radius `r`:

- **Traversal.** BFS from each `u ∈ V` to depth `r` gives `d(u,v)` for every `v` within `r`
  hops, and at no extra cost the number `#sp(u,v)` of shortest paths realising it.
  `O(|V|+|E|)` per traversal.
- **Rewiring.** `E_r = {(u,v) : 1 ≤ d(u,v) ≤ r}`. At `r=1` this is the original graph and the
  encoding is constant, which makes `r=1` a built-in degenerate control.
- **Encoding.** `γ(d)` = sinusoidal embedding of the hop distance; a small MLP maps it —
  optionally concatenated with `log(1 + #sp)` — to the edge representation.
- **Injection.** GAT: an additive bias on the attention logit, via `GATConv(edge_dim=...)`.
  GCN: no edge-feature channel, so a learned scalar gate `σ(wᵀe)` supplied as `edge_weight`.

**Implementation note.** Distances and path counts are computed algebraically, not with a
per-source BFS — `|V|` interpreter-level traversals per graph is far too slow for 45k graphs.
`(A^k)_{uv}` counts *walks* of length `k`, so the first `k` with `(A^k)_{uv} > 0` is exactly
`d(u,v)`; and at `k = d(u,v)` every length-`k` walk is necessarily a shortest *path*, so
`(A^d)_{uv} = #sp(u,v)`. Both fall out of `r` matrix products. **Verified** against a reference
BFS over 400 random graphs × `r ∈ {1,2,3,4}` — exact match on both quantities. The test ships
in [`shared/00_setup_and_diagnostic.ipynb`](shared/00_setup_and_diagnostic.ipynb).

**Invariance.** `d(u,v)` and `#sp(u,v)` are isomorphism invariants of the pair, so the model is
permutation invariant. Worth stating because the obvious alternative is not: a BFS *visit-order*
index depends on neighbour enumeration order, so relabelling the nodes changes the encoding and
the model is not a function of the graph. Notebook 00 tests both.

### Conditions

| ID | Condition | Role |
|----|-----------|------|
| M0 | no PE | control |
| M1 | LapPE (k eigenvectors, sign-flip augmented) | baseline |
| M2 | RWPE (random-walk return probabilities) | baseline |
| M3 | `r`-hop rewiring + sinusoidal hop-distance bias | **ours** |
| M4 | M3 + shortest-path-count channel | **ours, extended** |

Each runs under both GCN and GAT on all three datasets — 30 cells, one notebook each.

---

## Structure

One notebook per (architecture, dataset, condition), under `model/dataset/`. Every notebook is
**self-contained**: no shared module, no cross-notebook imports. Layout and run order are in
[`README.md`](README.md).

The tradeoff taken here: 30 notebooks duplicate their code, which is the price of each one
being independently runnable in Colab with nothing to install or clone. The mitigation is that
they were generated from a single template, so they started identical — if one needs editing,
check whether the other 29 need the same edit.

**Resumability is mandatory on free Colab.** Every run writes
`results/{arch}/{dataset}/{cond}_seed{n}.json` to Drive; a run whose file exists is skipped.
Datasets go to local ephemeral disk, not Drive.

### Compute budget (free Colab, T4)

| | CSL | CLUSTER | CIFAR10-SP |
|---|---|---|---|
| M0/M1/M2 | ~5 min | ~30–40 min | ~20–30 min |
| M3/M4 | ~10 min | ~1.5–2 h | ~2 h |

M3/M4 are the slow ones because rewiring multiplies the edge count, and that multiplier lands
on every message-passing step of every epoch. Whole grid ≈ 20 GPU-hours; spread over four
accounts, a few days.

### Fairness protocol

Predefined splits throughout (CSL uses stratified 5-fold, having none). Model selection on
**validation** accuracy, test set read once at the selected epoch — *not* averaged over final
epochs, which conflates convergence noise with performance. Parameter counts recorded in every
result file rather than forced to match: the PE modules add 500–1000 parameters to an ~18k
backbone, so no condition holds a meaningful capacity advantage.

---

## Theory — status: **verified**

Write `c^t(v)` for the colour after `t` rounds. Define SPD-WL by
`c^{t+1}(v) = HASH(c^t(v), {{ (d(u,v), c^t(u)) : u ≠ v }})`, and SPC-WL identically with the
pair label `(d, #sp)`. For `r ≥ diam`, M3 realises SPD-WL and M4 realises SPC-WL.

[`shared/01_expressivity.ipynb`](shared/01_expressivity.ipynb) has been run; all three
propositions hold on explicit witnesses.

| | Claim | Witness | Result |
|---|---|---|---|
| **Prop. 2** | SPD-WL ⊋ 1-WL | decalin / bicyclopentyl; CSL(41,2)/CSL(41,3) | 1-WL fails, SPD-WL separates ✓ |
| **Prop. 3** | SPD-WL, SPC-WL ⊉ 3-WL | 4×4 rook / Shrikhande, both SR(16,6,2,2) | neither variant separates ✓ |
| **Prop. 4** | SPC-WL ⊋ SPD-WL | 6 nodes, 8 edges, found by exhaustive search | SPD-WL fails, SPC-WL separates ✓ |

The Prop. 4 witness is **minimal**: exhaustive search found none on ≤5 nodes. The two graphs
share size, degree sequence *and* the complete multiset of pairwise distances `{1¹⁶, 2¹², 3²}`,
differing only in how many shortest paths realise those distances — so hop distance provably
cannot separate them. That is exactly what M4's extra channel is for, and it is a small
original result.

Together: `1-WL ⊊ T-RPE ⊆ GD-WL ⊊ 3-WL`. Prop. 3 is our own upper bound and belongs in the
paper as a limitation — a method whose ceiling is never stated invites the reader to assume it
has none.

**One implementation trap, recorded because it produced a convincing false negative.** Colour
refinement must hash by *content*, not re-index signatures per graph. Per-graph re-indexing
makes colours incomparable across graphs, and every pair comes back "indistinguishable" — which
looks exactly like a real finding.

---

## Paper plan

ACL template, 5 pages excluding references. Draft in [`paper/main.tex`](paper/main.tex);
asset mapping in [`paper/README.md`](paper/README.md).

| § | Content | Budget | Status |
|---|---|---|---|
| 1 Introduction | 1-WL bound; absolute vs relative gap; the rewiring confound; contributions | 0.75 p | **written** |
| 2 Related Work | LapPE/RWPE; P-GNN & Distance Encoding; Graphormer/GraphGPS; rewiring & over-squashing; WL hierarchy | 0.6 p | **written** |
| 3 Method | construction, encoder, injection, complexity, invariance | 1.0 p | **written** |
| 4 Expressive Power | Props 2–4 with witnesses | 0.8 p | **written** |
| 5 Experimental Setup | datasets, conditions, protocol, ablations | 0.5 p | **written** |
| 6 Results & Discussion | Table 1 main; Table 2 expressivity; Fig 2 ablations; Fig 3 cost | 1.1 p | `TODO` per paragraph |
| 7 Limitations & Conclusion | sub-3-WL bound; dense-graph degeneracy; `r` as a cost knob | 0.35 p | limitations written |

Sections 1–5 were written before any results because none of them depend on results. What
remains is four marked paragraphs in §6, the conclusion, and the abstract's headline sentence.
Every table and figure is regenerated from JSON by
[`shared/07_results_and_figures.ipynb`](shared/07_results_and_figures.ipynb) — nothing is
transcribed by hand.

Both positive and negative results are explicitly valued by the grading rubric. The Prop. 3
ceiling and any dense-graph degeneracy are reported as findings.

---

## Risks

**CLUSTER may be degenerate.** ~117 nodes, ~4300 edges → average degree ≈ 37, diameter 2–3.
Two-hop rewiring nearly completes the graph and every distance is 1 or 2, so the relative
signal may carry almost nothing. *Handling:* this is framed as design rather than accident —
CIFAR10-SP (sparse 8-NN, large diameter) versus CLUSTER (dense, tiny diameter) is a deliberate
contrast testing the hypothesis that traversal encodings help precisely when graphs are sparse
and long-diameter. Notebook 00's distance diagnostic decides before ~2h is spent: if CLUSTER
comes back degenerate, either report it as the dense regime at `r=2`, or swap CLUSTER →
MNIST-SP (same 8-NN sparsity, predefined split, non-molecular).

**Edge blow-up at `r=3`.** Notebook 06 measures `|E_r|/|E|` per dataset. `r` is an ablation
axis, not a fixed commitment; cap at `r=2` if memory requires.

**CSL saturates.** RWPE also solves CSL (~100%) while M0 sits at chance (10%). Report honestly:
CSL shows the method is in the right expressivity class, and differentiation against RWPE has
to come from CLUSTER/CIFAR10 accuracy and from cost.

**Attribution.** The `rewire-only` ablation is the one row that makes the main result
interpretable. It is currently a single CLUSTER run (~40 min). Without it, §6 cannot claim a
positional encoding — only a rewiring scheme.

---

## Verification

- **RPE correctness** (notebook 00): algebraic distances and path counts vs reference BFS.
  *Passing.*
- **Permutation invariance** (notebook 00): relabel, recompute, compare — and confirm a
  visit-order encoding fails the same test. *Passing.*
- **API surface** (notebook 00): `GNNBenchmarkDataset` splits, the two PE transforms, and
  `GATConv(edge_dim=...)`. The last is critical — without it the GAT half of the project has no
  mechanism.
- **Dataset constants** (notebook 00): the hard-coded `N_CLASSES` / `NODE_VOCAB` / `TASK` in
  every leaf notebook, cross-checked against the data.
- **Sanity floor**: M0 should reproduce published GCN/GAT numbers on CLUSTER and CIFAR10-SP
  within a point or two, and should sit at ~10% on CSL. If M0 is off, nothing downstream means
  anything.
- **`r=1` control** (notebook 05): should land on M0. If it beats M0 by a real margin, something
  is leaking.
- **End-to-end**: notebook 07 runs clean on partial results and reports which grid cells are
  still empty.

## Where things stand

Built and verified: all 35 notebooks, the theory (notebook 01 executed, all propositions
confirmed), and paper §§1–5.

Remaining: run notebook 00 and settle the CLUSTER question, run the grid, then fill §6, the
conclusion and the abstract from the generated assets.
