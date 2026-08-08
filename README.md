# Traversal-Based Relative Positional Encodings for Graph Neural Networks

Course project, *Machine Learning with Graphs*, Tel Aviv University.
Chen Mizrahi · Tomer Zalberg · Ofek Tovli · Itay Korenfeld

Positional encodings built from graph traversal are almost always **absolute** — a node is
described by its distance to a handful of anchor nodes, so the encoding inherits whatever
arbitrariness went into picking them. We ask whether an anchor-free **relative** encoding,
defined on node *pairs*, is a better way to inject global structure into a GNN.

Because every edge of a sparse graph joins nodes at distance 1, a pairwise encoding is vacuous
unless the graph is rewired. So we run a breadth-first traversal to depth `r` from every node,
add an edge for every pair within `r` hops, and label it with the hop distance `d(u,v)`,
sinusoidally encoded. The encoding reaches the network through two channels: an edge
weight / attention bias, and a per-node aggregated distance profile.

---

## What we found

**The method is exactly where the theory puts it.** On CSL — 4-regular, featureless, and
provably beyond 1-WL — the no-PE control sits at `10.00 ± 0.00` in *both* architectures, exact
chance with zero variance across 20 runs. Our encoding reaches `85.50` in both, just under the
**90% ceiling we computed before running anything**, and adding shortest-path counts lifts it to
`99.50`/`100.00`, the predicted 100%. Measured combinatorially, hop distance separates 97.8% of
the non-isomorphic 1-WL-colliding CSL pairs and shortest-path counts separate all of them.

**Our pre-registered prediction about *where* it would help was wrong, in the opposite
direction.** We predicted gains on sparse, long-diameter graphs (CIFAR10-SP, mean diameter 8.5)
and little on dense CLUSTER (2.2). The largest gain we measure anywhere is **+21.3 points on
CLUSTER**, the dataset we called degenerate; CIFAR10-SP moved +2.5 and −0.1. The reason is
visible in the expressivity table: **neither CLUSTER nor CIFAR10-SP produces a single 1-WL
collision.** Expressivity was never the binding constraint there, so an intervention justified
by expressivity had no route to helping on either.

**What decides the outcome is injection, not the graph.** Same dataset, same encoding, different
backbone: GCN −2.2, GAT +18.0. Across both non-CSL datasets the encoding never beats the control
under GCN. This is the mechanism of Proposition 5 — GCN and GAT both *normalise* their
aggregation, which algebraically cancels an edge-weight injection — showing up outside the
vertex-transitive case where we could prove it. The channel a relative encoding is given matters
more than the information it carries.

**The gain is not just rewiring.** Against `rewire-only` — the same rewired graph with a
*constant* edge feature, parameter-identical to our model — we gain 15.5 points at matched
budget.

Full numbers: [`RESULTS.md`](RESULTS.md). The reasoning behind each design decision, including
the predictions registered before the runs: [`PLAN.md`](PLAN.md).

## Conditions and datasets

| ID | Condition | Role |
|----|-----------|------|
| `M0` | no positional encoding | control |
| `M1` | Laplacian eigenvector PE, sign-flip augmented | baseline |
| `M2` | random-walk PE | baseline |
| `M3` | `r`-hop traversal rewiring + sinusoidal hop-distance encoding | **ours** |
| `M4` | `M3` + number of shortest paths per pair | **ours, extended** |

All datasets come from `torch_geometric.datasets.GNNBenchmarkDataset`, all with predefined
splits, none molecular — molecular graphs are largely within reach of 1-WL and so offer no
expressivity headroom.

| Dataset | Graphs | Nodes | Task | Why it is here |
|---|---|---|---|---|
| **CSL** | 150 | 41 | graph, 10-class | 4-regular and featureless, so 1-WL sees ten identical graphs and a plain GNN can only guess (10%). The cleanest test of the expressivity claim. No predefined split → stratified 5-fold. |
| **CLUSTER** | 12k | ~117 | node, 6-class | Dense SBM, average degree ≈ 37, diameter 2–3. The **dense** arm. |
| **CIFAR10-SP** | 45k | ~117 | graph, 10-class | Sparse 8-nearest-neighbour superpixel graphs, large diameter. The **sparse** arm. |

## Layout

```
shared/
  00_setup_and_diagnostic.ipynb    API checks, dataset facts, distance diagnostic  <- RUN FIRST
  01_expressivity.ipynb            theory validation, no training
  05_ablations.ipynb               10 variants, GCN/CLUSTER
  06_efficiency.ipynb              preprocessing cost and edge blow-up
  07_results_and_figures.ipynb     regenerates every table and figure
gcn/  csl|cluster|cifar10sp/  M0_baseline · M1_lappe · M2_rwpe · M3_trpe · M4_trpe_sp
gat/  csl|cluster|cifar10sp/  the same five
paper/    ACL LaTeX, with the generated tables and figures alongside
trpe/     the merged results: 240 run JSONs, ablations, expressivity, efficiency, figures
```

Every notebook is **self-contained** — nothing is imported from another notebook or a shared
module. Upload the folder to Google Drive and open any notebook in Colab.

## Reproducing

1. **`shared/00_setup_and_diagnostic.ipynb`** — mandatory, ~5 min. Verifies the PyG API the
   other 30 notebooks depend on, cross-checks the hard-coded dataset constants, and runs the
   distance diagnostic that fixes `r` per dataset. Every check must read `OK` and both `PASS`
   lines must appear. `GATConv(edge_dim=...)` is the critical one — without it the GAT half of
   the project has no mechanism.
2. **`shared/01_expressivity.ipynb`** — ~1 min of compute, CPU only, plus a dataset download on
   a fresh session. Produces Table 2.
3. **The two smoke tests**, before committing to anything long: `gcn/csl/M0_baseline` should
   land at ≈10% and `gcn/csl/M3_trpe` far above it. CSL graphs are 4-regular and featureless, so
   a 1-WL-bounded model provably cannot beat guessing. If M0 is well above 10%, structure is
   leaking into the features; if M3 is near 10%, the encoding isn't reaching the model. Either
   way, stop.
4. **The 30 leaf notebooks**, in any order, on any machine. ~27 GPU-hours in total, which is why
   step 3 exists.
5. **`shared/05_ablations.ipynb`** and **`shared/06_efficiency.ipynb`**.
6. **`shared/07_results_and_figures.ipynb`** — regenerates every table and figure, works on
   partial results, and its last cell reports which grid cells are still empty.

Results are written as one JSON file per run to
`Drive/MyDrive/trpe/results/{arch}/{dataset}/{condition}_seed{n}.json`; datasets go to
`/content/trpe_data`, local and ephemeral by design. **Runs are resumable** — a seed whose JSON
exists is skipped, so a dropped Colab session costs one seed rather than a notebook. The
corollary: **when the model changes, delete the stale JSON**, or the notebook will "finish"
instantly with old numbers.

Splitting across several people works with no coordination beyond step 3, since every run owns
its own filename. Merge the trees before notebook 07 (`cp -rn` merges without overwriting).

### If something goes wrong

| Symptom | Cause / fix |
|---|---|
| `CUDA out of memory` | Lower `BATCH_SIZE` in the config cell (CLUSTER 32→16, CIFAR10 128→64). Affects speed, not the result. |
| Session disconnects mid-notebook | Re-run it. Finished seeds are skipped. |
| `FileNotFoundError` on a dataset | The `/content` disk was wiped. Re-run; it re-downloads. |
| A dataset re-downloads every session | Expected — datasets live on local disk, not Drive. |
| M1 (LapPE) is slow on first run | The eigendecomposition is cached by `pre_transform`; only the first run pays. |
| PyG warns about a `pre_transform` mismatch | `LAP_K` or `RW_STEPS` changed after a cached run. Delete `/content/trpe_data/{DATASET}_{M1,M2}` and re-run. |
| A notebook finishes instantly | Working as intended: every run already had its JSON. Delete the files to redo. |

## Protocol

* Predefined splits throughout; CSL uses stratified 5-fold, having none.
* Model selection on **validation** accuracy; the test set is read once, at the selected epoch.
  Test accuracy is *not* averaged over the final few epochs — that conflates convergence noise
  with performance.
* Laplacian eigenvectors are sign-flip augmented, since they are defined only up to sign.
* Parameter counts are recorded in every result file and reported rather than forced to match.
  The overhead is **not** negligible — measured at **+12–14% under GCN and +35–37% under GAT**
  on an ~18k backbone — so capacity is not equalised across conditions. The `rewire-only`
  ablation is the control that settles it, being parameter-identical to `M3` with the positional
  signal replaced by a constant.

## Known limitations

Three are the method's: it is bounded below 3-WL (strongly regular graphs are exactly what it
cannot separate), it has little to say on dense short-diameter graphs, and the radius `r` is a
cost knob we measure no accuracy benefit from spending.

Two are ours. **Our M0 controls sit below published figures** for these architectures
(GCN/CLUSTER 39.89 against ~47–54), because the backbone is ~18k parameters against the
literature's ~100k and trains far fewer epochs — so read comparisons between conditions, not
against the literature. And **CIFAR10-SP ran at a single seed**, too thin to support a claim
about a two-point difference.

## Paper

[`paper/main.tex`](paper/main.tex), ACL template, 5 pages excluding references. Every table and
figure is generated by `shared/07_results_and_figures.ipynb` — nothing is transcribed by hand.
See [`paper/README.md`](paper/README.md) to build it, and [`TODO.md`](TODO.md) for what is left
to decide.
