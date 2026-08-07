# Runbook — what to run, in what order, and what to send back

> **Running in parallel across four people? Go to [`run/`](run/) instead.** Each of you gets a
> folder with only your notebooks and your own README. The rest of this file is the single-person
> sequence and the reference for what each phase means — see
> [Running in parallel](#running-in-parallel) below for how the split works.

Work top to bottom. Each phase has a **gate**: a cheap check that must pass before the next
phase is worth the GPU time. The whole grid is ~27 GPU-hours; the gates exist so that a broken
run costs you ten minutes instead of two days.

After each phase, paste the output back to me and I'll write it into the paper. The
**"send me"** column says exactly which cell output I need — the last cell of a notebook,
unless stated otherwise.

---

## One-time setup

1. Upload the `project/` folder to Google Drive (anywhere in `MyDrive`).
2. In Drive, right-click a notebook → **Open with → Google Colaboratory**.
   (If Colab isn't listed: *Open with → Connect more apps → Colaboratory*.)
3. In Colab: **Runtime → Change runtime type → T4 GPU**. Do this for every notebook — it
   resets per session.
4. **Runtime → Run all.** Approve the Drive-mount prompt when it appears.

Notebooks are self-contained, so nothing needs installing beyond the `pip` cell at the top.

**Where things land.** Results go to `MyDrive/trpe/results/…` (one JSON per run, survives the
session). Datasets go to `/content/trpe_data`, which is local and wiped when the session ends —
that's intentional, they re-download in a couple of minutes and would otherwise eat your Drive
quota.

**If a session drops mid-run:** just re-run the notebook. Completed seeds are skipped
automatically; you lose at most the seed that was in flight.

**Splitting across the four of you:** each run writes its own file, so there are no conflicts.
Everyone should point at *their own* Drive, then at the end one person collects all the JSON
into a single `MyDrive/trpe/results/` tree and runs notebook 07 there.

---

## Phase 0 — Setup and diagnostic · ~5 min

| # | Notebook | Time | Send me |
|---|---|---|---|
| 1 | `shared/00_setup_and_diagnostic.ipynb` | ~5 min | **all output from the API-check cell onward** (4 cells: API checks, dataset facts, distance diagnostic, correctness/invariance tests) |

**Gate — do not continue unless all three hold:**

- Every API check reads `OK`. `GATConv(edge_dim=...)` is the critical one; without it the GAT
  half of the project has no mechanism.
- Every dataset-facts line reads `OK`. A mismatch means a leaf notebook has a wrong
  `N_CLASSES` or `NODE_VOCAB` and would train against a malformed target.
- Both `PASS` lines appear (BFS correctness, permutation invariance).

This notebook also decides the CLUSTER question. If its verdict for CLUSTER is `DEGENERATE`,
tell me before Phase 3 — we either report CLUSTER as the dense-graph regime or swap it for
MNIST-SP, and that decision changes how §6 of the paper is framed.

---

## Phase 1 — Expressivity · ~10 min, CPU only

| # | Notebook | Time | Send me |
|---|---|---|---|
| 2 | `shared/01_expressivity.ipynb` | ~10 min | **the three result cells**: witness-pair table, Prop. 4 witness search, separation rates |

No GPU needed. The Prop. 4 exhaustive search takes ~60s at `n=6`; that's expected, not a hang.
This produces Table 2 of the paper.

---

## Phase 2 — CSL · ~1 h total · **this is the smoke test**

Run these two first, alone:

| # | Notebook | Time | Expect |
|---|---|---|---|
| 3 | `gcn/csl/M0_baseline.ipynb` | ~5 min | test accuracy **≈ 10%** |
| 4 | `gcn/csl/M3_trpe.ipynb` | ~10 min | test accuracy **well above 10%**, ceiling **90%** |
| 4b | `gcn/csl/M4_trpe_sp.ipynb` | ~10 min | should beat M3, ceiling **100%** |

The two ceilings are not guesses. The CSL distance profiles are fixed by the dataset, so we
computed in advance that at $r\ge4$ the hop distance separates 9 of the 10 classes and that the
last tied pair — CSL(41,6) vs CSL(41,16) — is separated only by shortest-path counts. M3 should
therefore plateau near 90% and M4 reach 100%.

**Gate.** CSL graphs are 4-regular and featureless, so a 1-WL-bounded model provably cannot do
better than guessing. M0 near 10% confirms the pipeline is honest; M3 far above 10% confirms
the encoding actually escapes the 1-WL bound. Send me both numbers before running anything else.

- If **M0 is well above 10%**, something is leaking structure into the features — stop, and
  send me the output.
- If **M3 is also near 10%**, the encoding isn't reaching the model — stop, and send me the
  output.

Then the remaining eight:

| # | Notebook | Time |
|---|---|---|
| 5–8 | `gcn/csl/` → `M1_lappe`, `M2_rwpe`, `M4_trpe_sp` | ~5–10 min each |
| 9–13 | `gat/csl/` → all five `M0`–`M4` | ~5–10 min each |

**Send me:** the final summary cell of each (the block starting `GCN / CSL / M0 …`).

---

## Phase 3 — CLUSTER · ~10.5 h total

| # | Notebook | Time |
|---|---|---|
| 14–16 | `gcn/cluster/M0_baseline`, `M1_lappe`, `M2_rwpe` | ~30–40 min each |
| 17–18 | `gcn/cluster/M3_trpe`, `M4_trpe_sp` | ~1.5–2 h each |
| 19–23 | `gat/cluster/` → all five | same, per condition |

The M3/M4 notebooks are the slow ones because rewiring multiplies the edge count and that
multiplier hits every epoch. Start one, leave the tab open, don't let the machine sleep.

**Send me:** the final summary cell of each.

---

## Phase 4 — CIFAR10-SP · ~10.5 h total

| # | Notebook | Time |
|---|---|---|
| 24–26 | `gcn/cifar10sp/M0_baseline`, `M1_lappe`, `M2_rwpe` | ~20–30 min each |
| 27–28 | `gcn/cifar10sp/M3_trpe`, `M4_trpe_sp` | ~2 h each |
| 29–33 | `gat/cifar10sp/` → all five | same, per condition |

First run downloads CIFAR10-SP (~1 GB) — a few minutes, once per session.

**Send me:** the final summary cell of each.

---

## Phase 5 — Ablations and cost · ~5 h

| # | Notebook | Time | Send me |
|---|---|---|---|
| 34 | `shared/05_ablations.ipynb` | ~4–5 h | the final variant table (8 rows) |
| 35 | `shared/06_efficiency.ipynb` | ~10 min | the timing table |

Notebook 05 is resumable per variant, so it's fine to run it across two sessions.

**The row that matters most is `rewire-only`.** It's the rewired graph with a *constant* edge
feature — all of M3's extra connectivity, none of its positional signal. If it matches `r2`,
then the gain came from rewiring rather than from position, and §6 of the paper has to say so
plainly instead of leaning on the M3-vs-M0 gap. Flag that number to me specifically.

Also check `r1` lands on the M0 baseline. At `r=1` the rewired graph *is* the original graph
and every edge carries distance 1, so there is nothing for the encoding to say. If `r1` beats
M0 by a real margin, something is leaking.

---

## Phase 6 — Collect · ~5 min

| # | Notebook | Send me |
|---|---|---|
| 36 | `shared/07_results_and_figures.ipynb` | **everything it prints**, plus the four PDFs from `MyDrive/trpe/figures/` |

Run this on whichever account has all the JSON collected. It works on partial results too, so
run it early to see the grid filling in — the last cell reports which cells are still empty.

It writes:

- `MyDrive/trpe/paper_tables/table1_main.tex` → Table 1
- `MyDrive/trpe/figures/fig_ablations.pdf` → Figure 2
- `MyDrive/trpe/figures/fig_efficiency.pdf` → Figure 3
- `MyDrive/trpe/figures/fig_distance_profile.pdf`, `fig_curves.pdf` → appendix

---

## Progress checklist

```
Phase 0  [ ] 00_setup_and_diagnostic          GATE: all OK + both PASS
Phase 1  [ ] 01_expressivity

Phase 2  [ ] gcn/csl/M0    [ ] gcn/csl/M3     GATE: M0 ~10%, M3 >> 10%
         [ ] gcn/csl/M1    [ ] gcn/csl/M2    [ ] gcn/csl/M4
         [ ] gat/csl/M0    [ ] gat/csl/M1    [ ] gat/csl/M2
         [ ] gat/csl/M3    [ ] gat/csl/M4

Phase 3  [ ] gcn/cluster/M0  [ ] M1  [ ] M2  [ ] M3  [ ] M4
         [ ] gat/cluster/M0  [ ] M1  [ ] M2  [ ] M3  [ ] M4

Phase 4  [ ] gcn/cifar10sp/M0  [ ] M1  [ ] M2  [ ] M3  [ ] M4
         [ ] gat/cifar10sp/M0  [ ] M1  [ ] M2  [ ] M3  [ ] M4

Phase 5  [ ] 05_ablations                     CHECK: rewire-only vs r2, and r1 vs M0
         [ ] 06_efficiency
Phase 6  [ ] 07_results_and_figures
```

---

## If something goes wrong

| Symptom | Cause / fix |
|---|---|
| `CUDA out of memory` | Lower `BATCH_SIZE` in the config cell (CLUSTER 32→16, CIFAR10 128→64). Only affects speed, not the result. |
| Session disconnects mid-notebook | Re-run it. Finished seeds are skipped. |
| `FileNotFoundError` on a dataset | The `/content` disk was wiped; just re-run — it re-downloads. |
| A dataset re-downloads every session | Expected. Datasets are deliberately on local disk, not Drive. |
| M1 (LapPE) is slow on first run | The eigendecomposition is cached to disk by `pre_transform`, so only the first run pays. A re-run is fast. |
| Two people ran the same notebook | Harmless — same filename, same content. |
| PyG warns about a `pre_transform` mismatch | You changed `LAP_K` or `RW_STEPS` after a cached run. Delete `/content/trpe_data/{DATASET}_{M1,M2}` and re-run. |
| Anything reads `FAIL` in notebook 00 | Stop and send it to me — that's an API change, and the fix belongs in the notebooks before you spend GPU time. |

## Running in parallel

**It works.** Every run writes its own file at
`MyDrive/trpe/results/{arch}/{dataset}/{condition}_seed{n}.json`, and the four shares below are
disjoint, so no two people ever write the same path. Nothing is shared at runtime — no locks,
no coordination, no ordering constraints beyond the one gate.

Four ready-made folders are in [`run/`](run/). **Each person uploads only their own folder** to
their own Drive and follows the README inside it.

| | Share | Notebooks | Time |
|---|---|---|---|
| [**Person 1**](run/person1/README.md) | GCN/CSL + GCN/CLUSTER, both gates, final collection | 15 | ~7.2 h |
| [**Person 2**](run/person2/README.md) | GAT/CSL + GAT/CLUSTER + efficiency | 14 | ~7.1 h |
| [**Person 3**](run/person3/README.md) | GCN/CIFAR10-SP + ablations Part A | 5 | ~7.0 h |
| [**Person 4**](run/person4/README.md) | GAT/CIFAR10-SP + ablations Part B | 5 | ~6.8 h |

Notebook counts are lopsided because the times are not: a CIFAR10-SP `M3` run alone is worth
two dozen CSL runs. The split balances *hours*, which is what actually matters.

### The three things that make parallel work

**Everyone runs `shared/00` first.** It is a five-minute check of *your* Colab environment — PyG
versions differ between accounts, and `GATConv(edge_dim=...)` is the check that decides whether
the GAT half of the project has a mechanism at all. It is the one notebook that is deliberately
duplicated across all four folders.

**One gate, held by Person 1.** Before anyone commits to a multi-hour run, Person 1 runs
`gcn/csl/M0` and `gcn/csl/M3` (~20 min total) and reports both numbers. M0 must land near
**10%** and M3 far above it — CSL graphs are 4-regular and featureless, so a 1-WL-bounded model
provably cannot beat guessing. Persons 2–4 run only `shared/00` until Person 1 gives the go-ahead.
Skipping this risks four people burning seven hours each on a pipeline that was broken from the
start.

**Merge at the end.** Each person mounts their own Drive, so there are four separate result
trees. When everyone is done they send their whole `MyDrive/trpe/results/` folder to Person 1,
who copies all four into one tree — the paths never collide — and runs
`shared/07_results_and_figures.ipynb` over the union. That notebook's last cell reports which
grid cells are still empty, so a missed run is visible rather than silently absent.

### The ablation split

`shared/05_ablations.ipynb` is the one notebook that had to be divided rather than assigned, at
~4.5 h. It is split by variant into two halves that write disjoint filenames:

* **Part A** (Person 3) — `r1`, `r2`, `r3`, `rewire-only`
* **Part B** (Person 4) — `enc-raw`, `enc-onehot`, `enc-learnable`, `layerwise`

Part A carries `rewire-only`, the row that determines whether the paper's central claim is "a
positional encoding" or "a rewiring scheme". If Person 3 runs nothing else, they should run that.

## What I'll do with each batch

As results arrive I'll fill the paper in this order, so partial results are still useful:

1. **Phase 0–1** → Table 2, §4 finalised, Appendix A.
2. **Phase 2** (CSL) → the expressivity paragraph of §6, the sharpest single result in the paper.
3. **Phases 3–4** → Table 1, the sparse-vs-dense paragraph.
4. **Phase 5** → Figures 2–3, the attribution paragraph, and the framing of the central claim.
5. **Phase 6** → abstract headline, conclusion, final numbers throughout.
