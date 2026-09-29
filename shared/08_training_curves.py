#!/usr/bin/env python3
"""Training-curve figures for the appendix, built from the 240 grid run JSONs.

Self-contained, like the notebooks: no imports from this repo. Reads
trpe/results/{gcn,gat}/{CSL,CLUSTER,CIFAR10}/*.json and writes two PDFs into paper/.

Each run JSON carries `history` = [{epoch, loss, val_acc}, ...] plus a single
end-of-run `test_acc` read once at the selected epoch. There is therefore NO
per-epoch test curve to plot -- by design, see the Protocol paragraph. We plot
the per-epoch training loss and validation accuracy, and mark the final test
accuracy as a tick on the right spine.

    python3 shared/08_training_curves.py
"""

import json
import glob
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "trpe", "results")
OUT = os.path.join(ROOT, "paper")

DATASETS = ["CSL", "CLUSTER", "CIFAR10"]
PRETTY = {"CSL": "CSL", "CLUSTER": "CLUSTER", "CIFAR10": "CIFAR10-SP"}
ARCHS = ["gcn", "gat"]
CONDS = ["M0", "M1", "M2", "M3", "M4"]
LABEL = {
    "M0": "M0 no PE",
    "M1": "M1 LapPE",
    "M2": "M2 RWPE",
    "M3": "M3 T-RPE",
    "M4": "M4 T-RPE+#sp",
}
# Colour-blind safe; M3/M4 (ours) are the two warm ones so they read as a pair.
COLOUR = {
    "M0": "#4c4c4c",
    "M1": "#0173b2",
    "M2": "#029e73",
    "M3": "#d55e00",
    "M4": "#cc78bc",
}


def load():
    runs = {}
    for f in glob.glob(os.path.join(RESULTS, "g*", "*", "*.json")):
        d = json.load(open(f))
        runs.setdefault((d["arch"], d["dataset"], d["condition"]), []).append(d)
    return runs


def curves(rs, key):
    """Stack per-epoch series of unequal length into a (runs x maxlen) masked array."""
    series = [[h[key] for h in r["history"]] for r in rs]
    n = max(len(s) for s in series)
    a = np.full((len(series), n), np.nan)
    for i, s in enumerate(series):
        a[i, : len(s)] = s
    return a


def panel(ax, rs_by_cond, key, ylabel, logy=False):
    for c in CONDS:
        rs = rs_by_cond.get(c)
        if not rs:
            continue
        a = curves(rs, key)
        x = np.arange(1, a.shape[1] + 1)
        # Runs stop at different epochs (early stopping). Averaging over the
        # survivors past that point produces spurious tail dips -- the "mean"
        # becomes one run. Show mean/band only while at least half the runs are
        # still alive; individual faint lines still run to their full length.
        alive = np.sum(~np.isnan(a), axis=0)
        keep = alive >= max(1, np.ceil(0.5 * len(rs)))
        with np.errstate(invalid="ignore"):
            mean = np.nanmean(a, axis=0)
            sd = np.nanstd(a, axis=0)
        mean = np.where(keep, mean, np.nan)
        # every individual run, faint -- so the figure really does show each run
        for row in a:
            ax.plot(x, row, color=COLOUR[c], alpha=0.13, lw=0.5, zorder=1)
        ax.plot(x, mean, color=COLOUR[c], lw=1.4, label=LABEL[c], zorder=3)
        if len(rs) > 1:
            ax.fill_between(x, np.where(keep, mean - sd, np.nan),
                            np.where(keep, mean + sd, np.nan),
                            color=COLOUR[c], alpha=0.13, lw=0, zorder=2)
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel("epoch")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25, lw=0.4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def figure(key, ylabel, fname, title_metric, logy=False, mark_test=False):
    runs = load()
    fig, axes = plt.subplots(2, 3, figsize=(10.6, 5.4))
    for i, arch in enumerate(ARCHS):
        for j, ds in enumerate(DATASETS):
            ax = axes[i][j]
            by = {c: runs.get((arch, ds, c), []) for c in CONDS}
            panel(ax, by, key, ylabel if j == 0 else "", logy=logy)
            if j != 0:
                ax.set_ylabel("")
            if mark_test:
                for c in CONDS:
                    rs = by.get(c)
                    if rs:
                        t = float(np.mean([r["test_acc"] for r in rs]))
                        ax.axhline(t, color=COLOUR[c], ls=(0, (1, 2)), lw=0.8,
                                   alpha=0.75, zorder=4)
            n = len(by[CONDS[0]])
            ax.set_title("%s / %s  (%d run%s per condition)"
                         % (arch.upper(), PRETTY[ds], n, "" if n == 1 else "s"),
                         fontsize=8.5)
            ax.tick_params(labelsize=7.5)
            ax.xaxis.label.set_size(8)
            ax.yaxis.label.set_size(8)
    # Share y-limits down each dataset column. Without this the GCN/CSL panel
    # auto-scales to start near 0.2 and the M0 chance line at 0.10 is clipped to
    # the axis floor, which is exactly the thing that panel is supposed to show.
    for j in range(len(DATASETS)):
        lo = min(axes[i][j].get_ylim()[0] for i in range(len(ARCHS)))
        hi = max(axes[i][j].get_ylim()[1] for i in range(len(ARCHS)))
        for i in range(len(ARCHS)):
            axes[i][j].set_ylim(lo, hi)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, frameon=False,
               fontsize=8.5, bbox_to_anchor=(0.5, -0.015))
    fig.suptitle(title_metric, fontsize=10)
    fig.tight_layout(rect=(0, 0.045, 1, 0.97))
    out = os.path.join(OUT, fname)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    figure("val_acc", "validation accuracy",
           "fig_curves_acc.pdf",
           "Validation accuracy per epoch. Faint lines are individual runs; "
           "bold is the mean, band is $\\pm1$ s.d.; dotted line is final test accuracy.",
           mark_test=True)
    figure("loss", "training loss",
           "fig_curves_loss.pdf",
           "Training loss per epoch. Faint lines are individual runs; "
           "bold is the mean, band is $\\pm1$ s.d.",
           logy=False)
