# Person 4 — GAT/CIFAR10-SP + ablations, Part B

**Your share: ~7.4 h of GPU time.** Everything here is self-contained — nothing to install
beyond the `pip` cell at the top of each notebook.

> **New to the Drive setup? Read [`../README.md`](../README.md) first** — it explains where results land, why you never create the `trpe/` folder yourself, and how the four shares get merged at the end.


**Wait for Person 1's go-ahead** before starting. Run
`shared/00_setup_and_diagnostic.ipynb` (~5 min) in the meantime.

You have only five notebooks, but three of them are long.

### Your notebooks

| Notebook | ~time |
|---|---|
| `shared/00_setup_and_diagnostic` — run first | 5 min |
| `gat/cifar10sp/M2_rwpe` | ~25 min |
| `gat/cifar10sp/M3_trpe` | ~2 h |
| `gat/cifar10sp/M4_trpe_sp` | ~2 h |
| `shared/05_ablations_partB` — 5 variants: `enc-raw`, `enc-onehot`, `enc-learnable`, `weight-only`, `profile-only` | ~3 h |

The first CIFAR10-SP run downloads ~1 GB; that is once per session, not per notebook.

`05_ablations_partB` is resumable per variant, so running it across two sessions is fine. It
runs on **GCN/CLUSTER** despite being in your folder — the ablation is deliberately held to one
architecture and one dataset so that only the varied component differs.

### What Part B answers

Two things.

**Is the sinusoidal encoder load-bearing?** If `enc-onehot` and `enc-learnable` match it, report
that honestly rather than glossing: with `r ≤ 3` there are only three distinct distances, so a
smooth encoding has little room to help.

**Which injection channel carries the signal?** `weight-only` and `profile-only` split M3's two
channels apart. On CSL the weight channel provably contributes nothing — GCN and GAT both
normalise their aggregation, so the weights cancel algebraically, and a weight-only model scored
exactly chance there. CLUSTER has real node features, so that argument does not apply and the
weight channel *might* carry something. These two rows are how we find out. Flag both numbers.

## How to run

1. Upload **this folder only** (`person4/`) to your own Google Drive.
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
