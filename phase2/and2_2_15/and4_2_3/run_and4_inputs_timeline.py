#!/usr/bin/env python3
"""Timeline: and4_2_3 A/B/C/D + X under all0 and sparse ones I patterns.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from probe_timeline import ones, pat_bits, run_probe  # noqa: E402
from rework_paths import savefig_locked  # noqa: E402

OUT = HERE / "timelines"
BUILD = ROOT / "phase2" / "build"
N_CYC = 121
TAG = "and215_and4_inputs"

LANES = [
    ("and4_A", "sky130_fd_sc_hd__and4_2_3__A", "and4.A (dfrtp_2_24.Q)", "#c45911"),
    ("and4_B", "sky130_fd_sc_hd__and4_2_3__B", "and4.B (dfrtp_2_25.Q)", "#548235"),
    ("and4_C", "sky130_fd_sc_hd__and4_2_3__C", "and4.C (dfrtp_2_20.Q)", "#1f4e79"),
    ("and4_D", "sky130_fd_sc_hd__nor3_2_2__Y", "and4.D (nor3_2_2.Y)", "#7030a0"),
    ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X (output)", "#c00000"),
]

MODES = [
    ("all0", pat_bits(N_CYC)),
    ("one_at_1", pat_bits(N_CYC, [1])),
    ("one_at_10", pat_bits(N_CYC, [10])),
    ("ones_1_12", pat_bits(N_CYC, [1, 12])),
]


def main() -> None:
    probes = [("I", "I"), ("enable", "enable")] + [(a, b) for a, b, *_ in LANES]
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=OUT,
        tag=TAG,
        probes=probes,
        modes=MODES,
        n_cyc=N_CYC,
    )
    by_mode = {name: [r for r in rows if r["mode_name"] == name] for name, _ in MODES}

    # CSV: all modes
    out_csv = OUT / "and4_inputs.csv"
    fields = ["mode", "cyc"] + [a for a, *_ in LANES]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in MODES:
            for r in by_mode[name]:
                w.writerow({k: r[k] if k != "mode" else name for k in fields})

    # Figure: one panel per mode
    n_m = len(MODES)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, 2.2 * n_m), dpi=140, sharex=True)
    if n_m == 1:
        axes = [axes]
    for ax, (name, _) in zip(axes, MODES):
        rs = by_mode[name]
        for yi, (lab, _net, title, col) in enumerate(reversed(LANES)):
            for c in ones(rs, lab):
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
        ax.set_yticks(range(len(LANES)))
        ax.set_yticklabels([t for _a, _n, t, _c in reversed(LANES)], fontsize=7, family="monospace")
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=9, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5)
        x_hi = ones(rs, "and4_X")
        ax.set_title(f"{name} · and4.X high @ n={len(x_hi)}", fontsize=9, loc="left")
    axes[-1].set_xlabel("cycle (enable=1 after reset)")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in LANES],
        loc="upper right",
        ncol=5,
        fontsize=7,
        frameon=False,
    )
    fig.suptitle("and4_2_3 inputs A/B/C/D + X · sparse I probes", fontsize=11)
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "and4_inputs.png")

    def fmt(xs: list[int], lim: int = 20) -> str:
        if len(xs) <= lim:
            return str(xs)
        return str(xs[:lim])[:-1] + f", …] (n={len(xs)})"

    md = [
        "# `and4_2_3` input timelines (B-arm)",
        "",
        "Structural sim. Lanes: A/B/C (flop Qs), D=`nor3_2_2.Y`, X=output.",
        "",
        "When **X is high**, all four inputs are high that cycle.",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
    ]
    for name, _ in MODES:
        rs = by_mode[name]
        md.append(f"## `{name}`")
        md.append("")
        for lab, _n, title, _c in LANES:
            md.append(f"- `{lab}` ({title}) high @ `{fmt(ones(rs, lab))}`")
        md.append("")
    md += [
        "Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "and4_inputs.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {png}")
    for name, _ in MODES:
        print(f"  {name}: and4.X n={len(ones(by_mode[name], 'and4_X'))}")


if __name__ == "__main__":
    main()
