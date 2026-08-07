# Person 1 — GCN/CSL + GCN/CLUSTER (+ gates and final collection)

**Your share: ~7.2 h of GPU time.** Everything here is self-contained — nothing to install
beyond the `pip` cell at the top of each notebook.

> **New to the Drive setup? Read [`../README.md`](../README.md) first** — it explains where results land, why you never create the `trpe/` folder yourself, and how the four shares get merged at the end.


You hold the **two gates** and the **final collection**, so you start first and finish last.

> ### ⚠️ Delete the stale M3 results first
>
> The 2026-08-07 fix changed the M3/M4 model. Runs are skipped when their JSON already exists,
> so the old files must go or the notebook will "finish" instantly with the broken numbers:
>
> ```
> Delete: MyDrive/trpe/results/gcn/CSL/M3_seed*.json
> ```
>
> `M0` is unaffected (it has no positional encoding) — keep those files.

### Step 1 — run these two before anyone starts a long run (~20 min)

1. `shared/00_setup_and_diagnostic.ipynb` (already done — re-run only to confirm the two
   corrected checks now read cleanly)
2. `gcn/csl/M0_baseline.ipynb` (already done — `10.00 ± 0.00`, keep it)
3. `gcn/csl/M3_trpe.ipynb` — **re-run after deleting the stale JSON.** Expect well above 10%,
   with a computed ceiling of **90%**.
4. `gcn/csl/M4_trpe_sp.ipynb` — expect it to beat M3, ceiling **100%**.

Then report:

* **all output from notebook 00** — the API checks, dataset facts and distance diagnostic must
  all read `OK`/`PASS`, and notebook 00's CLUSTER verdict decides whether Phase 3 goes ahead as
  planned.
* **M0's test accuracy on CSL**, which should be **≈ 10%**. CSL graphs are 4-regular and
  featureless, so a 1-WL-bounded model provably cannot beat guessing. If M0 is well above 10%,
  something is leaking structure into the features and every later number is suspect.

Then run `gcn/csl/M3_trpe.ipynb` (~10 min) and report its accuracy — it should be **far above
10%**. That is the check that the encoding actually reaches the model.

**Tell persons 2–4 to go once both numbers look right.** Until then they should only run
notebook 00.

### Step 2 — the rest, any order

| Notebook | ~time |
|---|---|
| `shared/01_expressivity.ipynb` (CPU only) | 10 min |
| `gcn/csl/M1_lappe`, `M2_rwpe`, `M4_trpe_sp` | 5–10 min each |
| `gcn/cluster/M0_baseline`, `M1_lappe`, `M2_rwpe` | 30–40 min each |
| `gcn/cluster/M3_trpe`, `M4_trpe_sp` | ~1.5–2 h each |
| `gcn/cifar10sp/M0_baseline`, `M1_lappe` | 25–30 min each |

### Step 3 — last, after everyone has sent you their results

Merge all four `MyDrive/trpe/results/` trees into one (the paths never collide), then run
`shared/07_results_and_figures.ipynb`. Send its full output plus the four PDFs from
`MyDrive/trpe/figures/`.

## How to run

1. Upload **this folder only** (`person1/`) to your own Google Drive.
2. Right-click a notebook -> **Open with -> Google Colaboratory**.
3. **Runtime -> Change runtime type -> T4 GPU.** This resets every session, so check it each time.
4. **Runtime -> Run all**, and approve the Drive-mount prompt.

Results are written to `MyDrive/trpe/results/...` in *your* Drive. At the end, send your whole
`MyDrive/trpe/results/` folder to you, who merges all four and runs the final collection
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
