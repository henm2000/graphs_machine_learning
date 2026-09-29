#!/usr/bin/env python3
"""Appendix C ablation table, built from the ten ablation run JSONs.

Self-contained, like the notebooks: no imports from this repo. Reads
trpe/results/ablations/*.json and writes paper/table3_ablations.tex.

The figure in Appendix C shows these ten numbers as bars; this table prints them, so
`rewire-only` and `r=1` -- the two controls the attribution argument in section 6 rests
on -- are readable as values rather than estimated off an axis. Every variant here ran
40 epochs at seed 0 on GCN/CLUSTER, which is NOT the grid's budget, so these rows compare
only to each other and never to Table 1.

    python3 shared/10_ablation_table.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "trpe", "results", "ablations")
OUT = os.path.join(ROOT, "paper", "table3_ablations.tex")

# (json stem, printed name, note) in the order the paper discusses them.
ROWS = [
    ("r1",            r"$r{=}1$ (unrewired control)", "control"),
    ("r2",            r"$r{=}2$ (= M3)",              "reference"),
    ("r3",            r"$r{=}3$",                     ""),
    ("rewire-only",   r"\textbf{rewire-only}",        "control"),
    ("enc-raw",       r"raw scalar encoder",          ""),
    ("enc-onehot",    r"one-hot encoder",             ""),
    ("enc-learnable", r"learned-table encoder",       ""),
    ("layerwise",     r"layerwise injection",         ""),
    ("weight-only",   r"\textbf{weight-only}",        "channel"),
    ("profile-only",  r"\textbf{profile-only}",       "channel"),
]

def load(stem):
    with open(os.path.join(SRC, f"{stem}_seed0.json")) as fh:
        return json.load(fh)

def main():
    lines = [r"\begin{tabular}{lccrr}", r"\toprule",
             r"variant & $r$ & channels & \#Param & test acc. \\", r"\midrule"]
    for stem, name, _note in ROWS:
        d = load(stem)
        chan = {"both": "both", "weight": "weight", "profile": "profile"}[d["channels"]]
        lines.append(f"{name} & {d['radius']} & {chan} & "
                     f"{d['params']:,} & {100 * d['test_acc']:.2f} \\\\".replace(",", r"\,"))
    lines += [r"\bottomrule", r"\end{tabular}"]
    with open(OUT, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("written ->", OUT)
    for stem, name, _ in ROWS:
        d = load(stem)
        print(f"  {stem:<14} r={d['radius']} {d['channels']:<8} "
              f"{d['params']:>7} {100 * d['test_acc']:6.2f}")

if __name__ == "__main__":
    main()
