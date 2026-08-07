# Person 2 — GAT/CSL + GAT/CLUSTER + efficiency

**Your share: ~7.1 h of GPU time.** Everything here is self-contained — nothing to install
beyond the `pip` cell at the top of each notebook.

> **New to the Drive setup? Read [`../README.md`](../README.md) first** — it explains where results land, why you never create the `trpe/` folder yourself, and how the four shares get merged at the end.


**Wait for Person 1's go-ahead** before starting anything long. In the meantime run
`shared/00_setup_and_diagnostic.ipynb` (~5 min) to confirm your own Colab environment passes
the API checks — it is environment-specific, so everyone runs it.

### Your notebooks

| Notebook | ~time |
|---|---|
| `shared/00_setup_and_diagnostic` — run first | 5 min |
| `gat/csl/M0_baseline` … `M4_trpe_sp` (all five) | 5–10 min each |
| `gat/cluster/M0_baseline`, `M1_lappe`, `M2_rwpe` | 30–40 min each |
| `gat/cluster/M3_trpe`, `M4_trpe_sp` | ~1.5–2 h each |
| `gat/cifar10sp/M0_baseline`, `M1_lappe` | 25–30 min each |
| `shared/06_efficiency` (CPU only) | 10 min |

Do the five CSL notebooks first — they are quick, and they confirm your environment produces
the same CSL numbers Person 1 saw before you commit to the multi-hour runs.

## How to run

1. Upload **this folder only** (`person2/`) to your own Google Drive.
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
