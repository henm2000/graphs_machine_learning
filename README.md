# Traversal-Based Relative Positional Encodings for Graph Neural Networks

Course project, *Machine Learning with Graphs*, Tel Aviv University.
Chen Mizrahi · Tomer Zalberg · Ofek Tovli · Itay Korenfeld

This README is the operational guide — what to run and in what order.
[`PLAN.md`](PLAN.md) is the research plan: the question, the design decisions and the
reasoning behind them, including the theory status and the open risks.

---

## The research question

Positional encodings that use graph traversal are almost always **absolute**: each node is
encoded by its distance to a handful of anchor nodes, which makes the encoding depend on
which anchors were picked. We ask whether an anchor-free **relative** encoding — defined on
node *pairs* rather than on nodes — is a better way to inject global structure into a GNN,
in accuracy and in expressive power.

In a sparse message-passing network every edge has relative distance 1, so a pairwise
encoding is vacuous unless the graph is rewired. We therefore follow Brüel-Gabrielsson et
al. (2022): a breadth-first traversal to depth `r` from every node yields the `r`-hop rewired
graph, and each rewired edge carries its hop distance `d(u,v)`, sinusoidally encoded, as an
edge feature (GCN) or an additive attention bias (GAT).

## Conditions

| ID | Condition | Role |
|----|-----------|------|
| `M0` | no positional encoding | control |
| `M1` | Laplacian eigenvector PE, sign-flip augmented | baseline |
| `M2` | random-walk PE | baseline |
| `M3` | `r`-hop traversal rewiring + sinusoidal hop-distance bias | **ours** |
| `M4` | `M3` + number of shortest paths per pair | **ours, extended** |

## Datasets

All from `torch_geometric.datasets.GNNBenchmarkDataset`, all with predefined splits, none
molecular.

| Dataset | Graphs | Nodes | Task | Why it is here |
|---|---|---|---|---|
| **CSL** | 150 | 41 | graph, 10-class | 4-regular and featureless, so 1-WL sees ten identical graphs and a plain GNN can only guess (10%). The cleanest possible test of the expressivity claim. No predefined split → stratified 5-fold. |
| **CLUSTER** | 12k | ~117 | node, 6-class | Dense SBM (average degree ≈ 37, diameter 2–3). The **dense** arm of a deliberate contrast. |
| **CIFAR10-SP** | 45k | ~117 | graph, 10-class | Sparse 8-nearest-neighbour superpixel graphs with a large diameter. The **sparse** arm, and the best-case regime for a relative distance encoding. |

CLUSTER and CIFAR10-SP are not two attempts at the same experiment. They test the hypothesis
that a traversal encoding helps precisely when graphs are sparse and long-diameter, and
degenerates when almost every pair already sits at distance 1 or 2.
`shared/00_setup_and_diagnostic.ipynb` measures exactly this.

---

## Layout

```
project/
  shared/
    00_setup_and_diagnostic.ipynb    <- RUN FIRST
    01_expressivity.ipynb            <- theory validation, no training
    05_ablations.ipynb
    06_efficiency.ipynb
    07_results_and_figures.ipynb     <- regenerates every table and figure
  gcn/  csl|cluster|cifar10sp/  M0_baseline · M1_lappe · M2_rwpe · M3_trpe · M4_trpe_sp
  gat/  csl|cluster|cifar10sp/  (the same five)
  paper/                             <- ACL LaTeX
```

Every notebook is **self-contained** — no imports from another notebook or from a shared
module. Upload the folder to Google Drive and open any notebook in Colab.

Results are written as one JSON file per run to
`Drive/MyDrive/trpe/results/{arch}/{dataset}/{condition}_seed{n}.json`. Datasets go to
`/content/trpe_data` (local, ephemeral, re-downloadable) rather than to Drive.

**Runs are resumable.** A seed whose JSON file already exists is skipped, so a dropped Colab
session costs one seed rather than a whole notebook. The four of us can run different
notebooks in parallel on separate Colab accounts; results merge automatically because each
run owns its own file.

## Run order

1. **`shared/00_setup_and_diagnostic.ipynb`** — mandatory. Verifies the PyG API the other 30
   notebooks depend on, checks the hard-coded dataset constants, and runs the distance
   diagnostic that fixes `r` per dataset. Two minutes. If a check fails here, fix it before
   spending GPU time.
2. **`shared/01_expressivity.ipynb`** — minutes, CPU only, no training. Produces Table 2.
3. **The 30 leaf notebooks**, in any order, on any machine.
4. **`shared/05_ablations.ipynb`** and **`shared/06_efficiency.ipynb`**.
5. **`shared/07_results_and_figures.ipynb`** — run any time; it works on partial results and
   reports which grid cells are still empty.

## Compute budget (free Colab, T4)

| | CSL | CLUSTER | CIFAR10-SP |
|---|---|---|---|
| `M0`/`M1`/`M2` | ~5 min | ~30–40 min | ~20–30 min |
| `M3`/`M4` | ~10 min | ~1.5–2 h | ~2 h |

`M3`/`M4` are the slow ones because rewiring multiplies the edge count, and that multiplier
lands on every message-passing step of every epoch. `shared/06_efficiency.ipynb` measures the
exact factor. Whole grid ≈ 20 GPU-hours, which spread over four accounts is a few days.

## Protocol

* Predefined splits throughout; CSL uses stratified 5-fold because it ships without one.
* Model selection on **validation** accuracy; the test set is read once, at the selected
  epoch. Test accuracy is *not* averaged over the final few epochs — that conflates
  convergence noise with performance.
* Parameter counts are recorded in every result file. The PE modules add roughly 500–1000
  parameters to an ~18k-parameter backbone, so no condition has a meaningful capacity
  advantage; the counts are reported rather than forced to match.
* Laplacian eigenvectors are sign-flip augmented, since they are only defined up to sign.

## Two things worth knowing before reading the results

**The attribution gap.** The main grid can show that `M3` beats `M0`, but not *why*. Rewiring
alone shortens paths and relieves over-squashing, entirely independently of the positional
signal. `shared/05_ablations.ipynb` includes a `rewire-only` variant — the rewired graph with
a *constant* edge feature — which is the only condition that separates the two explanations.
If `rewire-only` matches `M3`, the honest conclusion is that the contribution is a rewiring
scheme rather than a positional encoding.

**The upper bound.** `shared/01_expressivity.ipynb` confirms that neither `M3` nor `M4`
separates the 4×4 rook's graph from the Shrikhande graph — two strongly regular graphs with
identical parameters and therefore identical distance distributions. 3-WL does separate them.
This is a genuine limitation of the method and belongs in the paper as one.
