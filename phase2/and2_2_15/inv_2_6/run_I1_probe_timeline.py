#!/usr/bin/env python3
"""Timeline: a31o_2_11 pins + sticky Q/Y under all0 and sparse I=1 probes.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py
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
TAG = "and215_a31o_I1"

LANES = [
    ("inv9_A", "sky130_fd_sc_hd__inv_2_9__A", "NO-I  inv_2_9__A → a31o.A1", "#548235"),
    ("inv7_A", "sky130_fd_sc_hd__inv_2_7__A", "NO-I  inv_2_7__A → a31o.A2", "#c45911"),
    ("A3", "sky130_fd_sc_hd__mux2_1_7__X", "a31o.A3 mux2_1_7__X (→I)", "#1f4e79"),
    ("B1", "sky130_fd_sc_hd__inv_2_6__A", "a31o.B1 sticky Q", "#7030a0"),
    ("a31o_X", "sky130_fd_sc_hd__a31o_2_11__X", "a31o.X", "#c00000"),
    ("inv_Y", "sky130_fd_sc_hd__inv_2_6__Y", "inv_2_6.Y → and2.A", "#833c0c"),
]

STUB_LABS = ["inv9_A", "inv7_A"]

MODES = [
    ("all0", pat_bits(N_CYC)),
    ("all1", pat_bits(N_CYC, fill="1")),
    ("I1_cyc1", pat_bits(N_CYC, [1])),
    ("I1_cyc10", pat_bits(N_CYC, [10])),
    ("I1_cyc1_12", pat_bits(N_CYC, [1, 12])),
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

    out_csv = OUT / "I1_probe_timeline.csv"
    fields = ["mode", "cyc"] + [a for a, *_ in LANES]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in MODES:
            for r in by_mode[name]:
                w.writerow({k: r[k] if k != "mode" else name for k in fields})

    # Stub independence: inv_2_7__A / inv_2_9__A identical all0 vs all1
    stub_indep = True
    for lab in STUB_LABS:
        s0 = [int(r[lab]) for r in by_mode["all0"]]
        s1 = [int(r[lab]) for r in by_mode["all1"]]
        if s0 != s1:
            stub_indep = False
            print(f"  WARN {lab} differs all0 vs all1")

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
        ax.set_title(
            f"{name} · a31o.X n={len(ones(rs, 'a31o_X'))} · inv.Y n={len(ones(rs, 'inv_Y'))}",
            fontsize=9,
            loc="left",
        )
    axes[-1].set_xlabel("cycle (enable=1 after reset)")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in LANES],
        loc="upper right",
        ncol=3,
        fontsize=7,
        frameon=False,
    )
    fig.suptitle(
        "a31o_2_11 / inv_2_6 · probes  ·  NO-I lanes = inv_2_9__A + inv_2_7__A",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "I1_probe_timeline.png")

    def fmt(xs: list[int], lim: int = 20) -> str:
        if len(xs) <= lim:
            return str(xs)
        return str(xs[:lim])[:-1] + f", …] (n={len(xs)})"

    md = [
        "# `a31o_2_11` / `inv_2_6` I=1 probe timelines (A-arm)",
        "",
        "Observational structural sims (not a confirmed phase-3 rule).",
        "",
        "## NO-I stubs (`inv_2_7` / `inv_2_9`)",
        "",
        f"- `inv_2_7__A` / `inv_2_9__A` identical on **all0 vs all1**: **{stub_indep}**",
        f"- `inv_2_9__A` high (all0) @ `{fmt(ones(by_mode['all0'], 'inv9_A'))}`",
        f"- `inv_2_7__A` high (all0) @ `{fmt(ones(by_mode['all0'], 'inv7_A'))}`",
        "",
        "Dedicated stub figure + FA priors: [`noI_stub_timeline.md`](noI_stub_timeline.md).",
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
        "python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "I1_probe_timeline.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {png}")
    print(f"stub all0==all1: {stub_indep}")
    for name, _ in MODES:
        rs = by_mode[name]
        print(
            f"  {name}: a31o.X n={len(ones(rs, 'a31o_X'))}  inv.Y n={len(ones(rs, 'inv_Y'))}"
        )


if __name__ == "__main__":
    main()
