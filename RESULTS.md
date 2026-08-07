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

## Phase 2 — CSL, GCN ✅ 2026-08-07

Predictions registered **before** these runs, from the dataset's distance profiles alone:
M0 pinned at chance; M3 ceiling 90%; M4 ceiling 100%.

| condition | predicted | **measured** | params |
|---|---|---|---|
| M0 no PE | 10% (provable) | **10.00 ± 0.00** | 17 930 |
| M3 T-RPE | ≤ 90% | **85.50 ± 4.97** | 20 091 |
| M4 T-RPE + #sp | ≤ 100% | **99.50 ± 2.18** | 20 395 |

20 runs each (4 seeds × 5 stratified folds), r = 6.

**Both predictions confirmed.** M0 sits exactly at chance with zero variance, as the 1-WL bound
requires. M3 approaches its 90% ceiling. The 14-point M3→M4 gap is the shortest-path channel
separating CSL(41,6) from CSL(41,16) — the single pair of CSL classes with byte-identical
distance multisets. Proposition 4 therefore has an instance on a standard benchmark, not only
on the synthetic 6-node witness.

### Superseded: the weight-only formulation

The first version injected the encoding **only** as an edge weight / attention bias and scored
`10.00 ± 0.00` on CSL — chance, zero variance, identical to M0. This is Proposition 5, not a
bug: on a vertex-transitive graph GCN's symmetric normalisation forces `Σ_u ŵ_uv = 1` for every
`v` regardless of the weights, so with uniform features the layer returns `Wx` for any `w`, and
GAT's softmax does the same. Kept as a reported negative result; the fix is the second
(node-profile) injection channel.

---

## Phase 1 — expressivity ⏳ not yet run
## Phase 2 — CSL, GAT ⏳
## Phase 3 — CLUSTER ⏳
## Phase 4 — CIFAR10-SP ⏳
## Phase 5 — ablations, efficiency ⏳
## Phase 6 — collection ⏳
