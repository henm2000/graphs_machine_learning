# Person 3 — GCN/CIFAR10-SP + ablations, Part A

**Your share: ~7.6 h of GPU time.** Everything here is self-contained — nothing to install
beyond the `pip` cell at the top of each notebook.

> **New to the Drive setup? Read [`../README.md`](../README.md) first** — it explains where results land, why you never create the `trpe/` folder yourself, and how the four shares get merged at the end.


**Wait for Person 1's go-ahead** before starting. Run
`shared/00_setup_and_diagnostic.ipynb` (~5 min) in the meantime.

You have only five notebooks, but three of them are long. `shared/05_ablations_partA.ipynb`
contains **the single most important row in the whole project** — see below.

### Your notebooks

| Notebook | ~time |
|---|---|
| `shared/00_setup_and_diagnostic` — run first | 5 min |
| `gcn/cifar10sp/M2_rwpe` | ~25 min |
| `gcn/cifar10sp/M3_trpe` | ~2 h |
| `gcn/cifar10sp/M4_trpe_sp` | ~2 h |
| `shared/05_ablations_partA` — 5 variants: `r1`, `r2`, `r3`, `rewire-only`, `layerwise` | ~3 h |

The first CIFAR10-SP run downloads ~1 GB; that is once per session, not per notebook.

`05_ablations_partA` is resumable per variant, so running it across two sessions is fine.

### Two numbers to flag explicitly when Part A finishes

* **`rewire-only` vs `r2`.** `rewire-only` is the rewired graph with a *constant* edge feature —
  all of M3's extra connectivity, none of its positional signal. If the two match, the benefit
  came from rewiring rather than from position, and the paper's central claim has to be
  rewritten from "a positional encoding" to "a rewiring scheme". This is the only run that can
  distinguish those.
* **`r1` vs Person 1's `gcn/cluster/M0`.** At `r=1` the rewired graph *is* the original graph and
  every edge carries distance 1, so `r1` should land on M0. If it beats M0 by a real margin,
  something is leaking.

## How to run

1. Upload **this folder only** (`person3/`) to your own Google Drive.
2. Right-click a notebook -> **Open with -> Google Colaboratory**.
3. **Runtime -> Change runtime type -> T4 GPU.** This resets every session, so check it each time.
4. **Runtime -> Run all**, and approve the Drive-mount prompt.

Results are written to `MyDrive/trpe/results/...` in *your* Drive. At the end, send your whole
`MyDrive/trpe/results/` folder to Person 1, who merges all four and runs the final collection
notebook.

**If a session drops:** just re-run the notebook. Finished runs are skipped automatically, so
you lose at most the one that was in flight.

**Send back** the final summary cell of each notebook (the block starting `GCN / ... / M0`).

## If something goes wrong

| Symptom | Fix |
|---|---|
| `CUDA out of memory` | Lower `BATCH_SIZE` in the config cell (CLUSTER 32->16, CIFAR10 128->64). Slower, same result. |
| Dataset re-downloads every session | Expected. Datasets live on local disk, not Drive, on purpose. |
| Session disconnects | Re-run; completed runs are skipped. |
| Anything reads `FAIL` in notebook 00 | Stop and report it. That is an API change and needs fixing before GPU time is spent. |

Full details: [`../../RUNBOOK.md`](../../RUNBOOK.md)
