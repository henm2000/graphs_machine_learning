# Results log

Running record of confirmed numbers, newest phase last. Everything here is measured, not
projected. Predictions made *before* a run are marked as such — that is what makes them worth
something.

---

## Phase 0 — setup and diagnostic ✅ 2026-08-07

All API checks pass, including `GATConv(edge_dim=...)`. All three dataset cross-checks `OK`.

**Distance diagnostic** — measured before any training, and the basis for the sparse-vs-dense
prediction in §6 of the paper:

| dataset | graphs | avg n | avg deg | mean diam | pairs at d≤2 | verdict |
|---|---|---|---|---|---|---|
| CSL | 150 | 41.0 | 4.0 | **6.0** | 28.5% | INFORMATIVE |
| CLUSTER | 10 000 | 117.7 | 36.7 | **2.2** | 100% | **DEGENERATE** |
| CIFAR10-SP | 45 000 | 117.8 | 8.0 | **8.5** | 22.8% | INFORMATIVE |

Edge blow-up `|E_r|/|E|` — this is the per-epoch training-cost multiplier for M3/M4:
CSL 2.9× (r=2) / 5.2× (r=3); CLUSTER 3.3× (r=2, saturated); CIFAR10-SP 2.8× (r=2) / 5.0× (r=3).

**Correctness:** algebraic hop distances and shortest-path counts match a reference BFS exactly
over 300 random graphs × r∈{1,2,3,4}.

**Equivariance:** `enc(PAP')[i] == enc(A)[P[i]]` holds 200/200 for our distance profile and
2/200 for a BFS visit-order encoding. (The first version of this test compared *sorted*
multisets and wrongly reported 200/200 for both — the sorted multiset of visit-order ranks is
always `{0,…,(n-1)/n}` regardless of traversal order. Fixed 2026-08-07; the cell now asserts on
both outcomes.)

---

## Phase 2 — CSL, GCN ✅ 2026-08-07 — **row complete**

Predictions registered **before** these runs, from the dataset's distance profiles alone:
M0 pinned at chance; M3 ceiling 90%; M4 ceiling 100%. PLAN.md additionally predicted that the
baselines would saturate.

| condition | predicted | **measured** | params |
|---|---|---|---|
| M0 no PE | 10% (provable) | **10.00 ± 0.00** | 17 930 |
| M1 LapPE | saturates | **98.83 ± 1.91** | 18 442 |
| M2 RWPE | ~100% | **100.00 ± 0.00** | 18 954 |
| M3 T-RPE | ≤ 90% | **85.50 ± 4.97** | 20 091 |
| M4 T-RPE + #sp | ≤ 100% | **99.50 ± 2.18** | 20 395 |

20 runs each (4 seeds × 5 stratified folds), r = 6.

**Every prediction confirmed.** M0 sits exactly at chance with zero variance, as the 1-WL bound
requires. M3 approaches its 90% ceiling. The 14-point M3→M4 gap is the shortest-path channel
separating CSL(41,6) from CSL(41,16) — the single pair of CSL classes with byte-identical
distance multisets. Proposition 4 therefore has an instance on a standard benchmark, not only
on the synthetic 6-node witness.

**M3 loses to both baselines here, and that is the theory working, not failing.** SPD-WL
provably cannot separate CSL(41,6) from CSL(41,16), so M3 is capped at 90%: it identifies 8
classes outright and must guess between the tied pair, giving `8 + 2×0.5 = 9` of 10. LapPE and
RWPE do not realise SPD-WL and are not bound by that ceiling, so they solve CSL outright. The
ranking on CSL is therefore not evidence about the method's quality — it is the predicted
consequence of a bound we proved. Differentiation against RWPE has to come from
CLUSTER/CIFAR10-SP accuracy and from cost, exactly as PLAN.md registered in advance.

**Why the baselines saturate so easily.** CSL's 150 graphs are 10 isomorphism classes × 15
permuted copies of the same graph, so train and test hold isomorphic copies of each other. Any
permutation-invariant encoding that separates the 10 classes scores 100% by construction; there
is no generalisation gap to bridge. CSL measures graph *discrimination* and nothing else, which
is why it belongs in §6's expressivity paragraph rather than in an accuracy comparison.

### Superseded: the weight-only formulation

The first version injected the encoding **only** as an edge weight / attention bias and scored
`10.00 ± 0.00` on CSL — chance, zero variance, identical to M0. This is Proposition 5, not a
bug: on a vertex-transitive graph GCN's symmetric normalisation forces `Σ_u ŵ_uv = 1` for every
`v` regardless of the weights, so with uniform features the layer returns `Wx` for any `w`, and
GAT's softmax does the same. Kept as a reported negative result; the fix is the second
(node-profile) injection channel.

---

## Phase 2 — CSL, GAT ✅ 2026-08-07 — **row complete**

| condition | predicted | **measured** | params |
|---|---|---|---|
| M0 no PE | 10% (provable) | **10.00 ± 0.00** | 18 442 |
| M1 LapPE | saturates | **97.50 ± 3.78** | 18 954 |
| M2 RWPE | ~100% | **99.00 ± 3.00** | 19 466 |
| M3 T-RPE | ≤ 90% | **85.50 ± 6.69** | 24 938 |
| M4 T-RPE + #sp | ≤ 100% | **100.00 ± 0.00** | 25 242 |

20 runs each, r = 6.

---

## Phase 2 complete — the CSL picture, both architectures ✅ 2026-08-07

| | M0 | M1 LapPE | M2 RWPE | M3 T-RPE | M4 +#sp |
|---|---|---|---|---|---|
| **GCN** | 10.00 ± 0.00 | 98.83 ± 1.91 | 100.00 ± 0.00 | **85.50 ± 4.97** | 99.50 ± 2.18 |
| **GAT** | 10.00 ± 0.00 | 97.50 ± 3.78 | 99.00 ± 3.00 | **85.50 ± 6.69** | 100.00 ± 0.00 |
| *predicted* | *10% (provable)* | *saturates* | *~100%* | *≤ 90%* | *≤ 100%* |

**All three registered predictions confirmed, and confirmed twice.** This is the project's main
methodological asset: the numbers were computable from the CSL distance profiles before any GPU
time was spent, and the measurements landed where the theory put them.

* **M0 is pinned at exactly `10.00 ± 0.00` in both architectures.** Zero variance, chance
  accuracy, as the 1-WL bound requires on 4-regular featureless graphs. Also the cleanest
  possible evidence that no structure is leaking through the features.
* **M3 = `85.50` in *both* architectures**, agreeing to the decimal despite entirely different
  injection mechanisms — an additive attention-logit bias in GAT, a learned scalar gate in GCN.
  Both sit just under the *proven* 90% SPD-WL ceiling. Independent architectures converging on
  the same mean is much stronger evidence that the ceiling is a property of the **encoding**
  than either run alone.
* **M4 reaches `99.50` / `100.00`**, the predicted 100%. The M3→M4 gap is 14.0 (GCN) and 14.5
  (GAT) points, and it is exactly Proposition 4: the shortest-path channel separating
  CSL(41,6) from CSL(41,16), the one class pair with byte-identical distance multisets.

**CSL is an expressivity result, not an accuracy win, and §6 must say so.** M1 and M2 also solve
CSL, and M3 loses to both — by design, because SPD-WL provably cannot exceed 90% here while
LapPE and RWPE are not bound by that ceiling. Write the paragraph as predicted-vs-measured
rather than as a ranking. Differentiation against RWPE must come from CLUSTER/CIFAR10-SP and
from cost (notebook 06), exactly as PLAN.md registered in advance.

### ⚠️ Parameter-count claim in §5 is wrong — now confirmed, not inferred

The GAT M0 run measured `18 442`, matching the value inferred from the `+512` LapPE / `+1024`
RWPE offsets. So the overheads are established:

| | M0 | M3 | M4 |
|---|---|---|---|
| GCN | 17 930 | 20 091 (**+2 161**, +12.1%) | 20 395 (**+2 465**, +13.7%) |
| GAT | 18 442 | 24 938 (**+6 496**, **+35.2%**) | 25 242 (**+6 800**, **+36.9%**) |

§5 of the paper and the protocol sections of README/PLAN claim the PE modules add "500–1000
parameters to an ~18k backbone, so no condition holds a meaningful capacity advantage". That is
false by a factor of up to seven, and 35% is large enough for a reader to call the main result
a capacity effect. Two things to do:

1. Rewrite the sentence to the measured range and acknowledge the confound rather than dismiss it.
2. Point at the control that already answers it: **`rewire-only` is capacity-matched to M3** —
   same modules, same parameters, constant edge feature instead of the positional signal. If
   `rewire-only` lands near M0 while M3 beats it, capacity is ruled out directly. This raises
   the ablation from "attribution" to "attribution *and* capacity control", and is worth
   stating explicitly in §5.

On CSL itself the confound is void: M0's failure is an information bound, not a capacity bound,
so no number of extra parameters would move it off 10%.

## Phase 1 — expressivity ✅ 2026-08-08

Notebook 01 executed. All four propositions hold on their witnesses.

| witness pair | 1-WL | SPD-WL | SPcount-WL | supports |
|---|---|---|---|---|
| decalin / bicyclopentyl | – | separates | separates | Prop. 2 |
| CSL(41,2) / CSL(41,3) | – | separates | separates | Prop. 2 |
| CSL(41,4) / CSL(41,5) | – | separates | separates | Prop. 2 |
| 4×4 rook / Shrikhande, SR(16,6,2,2) | – | – | – | Prop. 3 |

Prop. 4 witness found at **n = 6**, none at n ≤ 5, so minimality holds as §4 claims. Both graphs
carry distance multiset `{1¹⁶, 2¹², 3²}` and differ only in shortest-path counts.

**Separation on the benchmarks — and the correction that matters.**

| dataset | sampled | 1-WL-indistinguishable pairs | SPD-WL | SPcount-WL |
|---|---|---|---|---|
| CSL | 120 | 7 140 | 88.7% | 90.8% |
| CLUSTER | 120 | **0** | n/a | n/a |
| CIFAR10-SP | 120 | **0** | n/a | n/a |

Those CSL percentages understate the encoding. CSL ships 15 permuted copies per class, so **660
of the 7 140 pairs are isomorphic** and no invariant can or should separate them — a 9.2% floor.
Against the 6 480 *separable* pairs: **SPD-WL 97.8%, SPcount-WL 100.0%**. SPD-WL misses exactly
144 pairs = the 12×12 CSL(41,6)/CSL(41,16) block, which is Proposition 4 measured on a real
benchmark. (The `neither` column that makes this visible was added 2026-08-08; without it the
paper would have reported 88.7/90.8 and undersold the result.)

**CLUSTER and CIFAR10-SP have zero 1-WL collisions.** Expressivity is simply not the bottleneck
on either. This is a finding, and it is the honest frame for the accuracy tables below.

---

## Phases 3–4 — CLUSTER and CIFAR10-SP ✅ 2026-08-08 — **grid complete, 240/240**

| GCN | CSL | CLUSTER | CIFAR10-SP |
|---|---|---|---|
| M0 no PE | 10.00 ± 0.00 | 39.89 ± 4.01 | 46.62 |
| M1 LapPE | 98.83 ± 1.91 | **60.00 ± 1.00** | 47.12 |
| M2 RWPE | 100.00 ± 0.00 | 35.04 ± 2.21 | 47.01 |
| M3 T-RPE | 85.50 ± 4.97 | 37.67 ± 4.89 | **49.13** |
| M4 +#sp | 99.50 ± 2.18 | 39.04 ± 6.11 | 48.68 |

| GAT | CSL | CLUSTER | CIFAR10-SP |
|---|---|---|---|
| M0 no PE | 10.00 ± 0.00 | 48.57 ± 11.74 | 59.93 |
| M1 LapPE | 97.50 ± 3.78 | 64.97 ± 0.64 | 60.46 |
| M2 RWPE | 99.00 ± 4.36 | 53.30 ± 1.87 | **60.74** |
| M3 T-RPE | 85.50 ± 6.69 | 66.58 ± 1.43 | 60.45 |
| M4 +#sp | 100.00 ± 0.00 | **69.85 ± 0.22** | 59.80 |

CSL 20 runs/cell, CLUSTER 3, CIFAR10-SP **1** — the CIFAR10-SP column has no variance estimate,
and must never be typeset as `± 0.00`. GAT/CSL M2 was re-run 2026-08-08 (its JSON was missing
from the merge); same mean, std now 4.36 rather than the 3.00 logged on 08-07.

### ⚠️ The registered sparse-vs-dense prediction FAILED, and in the opposite direction

PLAN.md and §5 registered, before training: T-RPE should give *little or nothing* on CLUSTER
(mean diameter 2.2, 100% of pairs at d ≤ 2) and should *help* on CIFAR10-SP (8.5) and CSL (6.0).
Measured:

* **CLUSTER, GAT** — the largest gain anywhere: M4 `69.85` vs M0 `48.57`, **+21.3 points**, also
  beating LapPE by 4.9. On the dataset predicted to be degenerate.
* **CIFAR10-SP** — the predicted best case: **+2.5** (GCN M3) and **−0.1** (GAT M3). Nothing.

The prediction is wrong and the paper must say so. It was registered in advance, which is
exactly what makes reporting the failure worth something.

### What the axis actually is: architecture, not sparsity

| CLUSTER | M0 | M3 | M4 |
|---|---|---|---|
| GCN | 39.89 | 37.67 (**−2.2**) | 39.04 (**−0.9**) |
| GAT | 48.57 | 66.58 (**+18.0**) | 69.85 (**+21.3**) |

Same dataset, same encoding, opposite outcomes. Under GCN the encoding reaches the model only
through a scalar gate on a normalised aggregation; under GAT it enters as an additive attention
bias on a real edge-feature channel. That is Proposition 5's mechanism showing up again outside
CSL: **how the encoding is injected dominates what it encodes.** M3/M4 never beat M0 under GCN
on either non-CSL dataset, and beat everything under GAT on CLUSTER.

### ⚠️ M0 sits below published baselines

| | measured M0 | published (Dwivedi et al., ~100k params) |
|---|---|---|
| GCN/CLUSTER | 39.89 ± 4.01 | ~47–54 |
| GAT/CLUSTER | 48.57 ± **11.74** | ~54–57 |
| GCN/CIFAR10-SP | 46.62 | ~55 |
| GAT/CIFAR10-SP | 59.93 | ~64 |

Our backbone is ~18k parameters against their ~100k and trains 60/40 epochs, so lower is
expected — but PLAN.md's verification criterion was "within a point or two", and that is not
met. The GAT/CLUSTER M0 variance of ±11.74 across 3 seeds is itself a stability problem. Report
relative differences between conditions, not absolute standing against the literature.

---

## Phase 5 — ablations and efficiency ✅ 2026-08-08

GCN / CLUSTER, 40 epochs, 1 seed.

| variant | r | encoder | channels | test acc |
|---|---|---|---|---|
| r1 | 1 | sinusoidal | both | 35.20 |
| **r2** | 2 | sinusoidal | both | **36.11** |
| r3 | 3 | sinusoidal | both | 30.29 |
| **rewire-only** | 2 | const | both | **20.64** |
| enc-raw | 2 | raw | both | 30.81 |
| enc-onehot | 2 | onehot | both | 39.34 |
| enc-learnable | 2 | learnable | both | 31.49 |
| layerwise | 2 | sinusoidal | both | 39.57 |
| weight-only | 2 | sinusoidal | weight | 38.84 |
| profile-only | 2 | sinusoidal | profile | 20.79 |

**Attribution: `r2 − rewire-only = +15.48` points.** Both ran at the same budget, so this
comparison is internally valid. The gain is *not* explained by added connectivity — rewiring
with a constant edge feature collapses the model to 20.64, near the 16.7% chance floor for
6-class CLUSTER. The honest reading is symmetric, though: this says a constant edge feature on a
3.3×-denser graph is actively destructive, as much as it says position is worth +15.5.

**Channel split reads the same way as the main grid.** `weight-only` 38.84 ≈ M0; `profile-only`
20.79 ≈ `rewire-only`. Under GCN the profile channel *hurts* on CLUSTER — the opposite of CSL,
where it was the only channel that worked. Prop. 5 says the weight channel cancels on
vertex-transitive graphs with uniform features; CLUSTER is neither, so both channels behave
differently there, and the ablation confirms that rather than contradicting it.

### ⚠️ The "vs M0" column of the ablation is not budget-matched

The ablation notebook trains **40 epochs, 1 seed**; the main grid trains **60 epochs, 3 seeds**.
Notebook 07's Figure 2 draws the main-grid M0 (39.89) as a dashed reference line across the
ablation bars, and that comparison is invalid. Consequences:

* `r1 = 35.20` is **4.69 below** M0. The leak check asks whether `r1` *beats* M0; it does
  not, so no leak — the deficit is a training-budget artefact, not a signal.
* Every "vs M0" delta in the table above is confounded. Within-ablation comparisons
  (`r2` vs `rewire-only`, `weight-only` vs `profile-only`, the encoder sweep) are all matched
  and stand.

Fix: either drop the M0 line from Figure 2, or run one GCN/CLUSTER M0 at 40 epochs / seed 0
(~30 min) as a matched control.

### Efficiency

| dataset | T-RPE r=2 | LapPE | RWPE | blow-up r=2 | r=3 |
|---|---|---|---|---|---|
| CSL | **0.24 ms** | 1.83 | 1.98 | 2.85× | 5.20× |
| CLUSTER | 7.66 ms | 11.97 | **2.32** | 3.27× | 3.27× (saturated) |
| CIFAR10-SP | **0.83 ms** | 3.69 | 1.70 | 3.34× | 6.05× |

Preprocessing beats LapPE everywhere (1.4–7.6×) but loses to RWPE on CLUSTER. The real cost is
the 2.9–3.3× edge blow-up, which lands on every epoch.

### Parameter overheads — §5's claim confirmed wrong

| | M0 | M3 | M4 |
|---|---|---|---|
| GCN | 17 930 – 18 186 | +11.9 – 12.1% | +13.6 – 13.7% |
| GAT | 18 442 – 18 698 | **+34.7 – 35.2%** | **+36.4 – 36.9%** |

Consistent across all three datasets. §5's "500–1000 parameters" is wrong by up to 7×.

---

## Phase 6 — collection ✅ 2026-08-08

All assets regenerated and verified: 240/240 grid runs, 10/10 ablation variants,
`expressivity.json`, `efficiency.json`, four figures, `table1_main.tex`. Tree is at
`project/trpe/`.
