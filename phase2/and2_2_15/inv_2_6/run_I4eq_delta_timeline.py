#!/usr/bin/env python3
"""Timeline stack: 4 equal-spaced I=1, Δ = 1..11 (I_REF=2).

  I@{2, 2+Δ, 2+2Δ, 2+3Δ}  for Δ = 1,2,…,11

Lanes: mux2_1_7 S/A0/A1/X + a31o.X + sticky Q.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/inv_2_6/run_I4eq_delta_timeline.py
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
TAG = "and215_I4eq_delta"
I_REF = 2
DELTAS = range(1, 12)  # 1..11

LANES = [
    ("S", "sky130_fd_sc_hd__inv_2_8__A", "mux.S  inv_2_8__A", "#1f4e79"),
    ("A0", "sky130_fd_sc_hd__mux2_1_7__A0", "mux.A0  ¬(A∧I)", "#548235"),
    ("A1", "sky130_fd_sc_hd__or2_2_7__X", "mux.A1  A∨I", "#c45911"),
    ("X", "sky130_fd_sc_hd__mux2_1_7__X", "mux.X → a31o.A3", "#c00000"),
    ("a31o_X", "sky130_fd_sc_hd__a31o_2_11__X", "a31o.X", "#7030a0"),
    ("sticky_Q", "sky130_fd_sc_hd__inv_2_6__A", "sticky Q", "#833c0c"),
]


def build_modes() -> list[tuple[str, str, list[int]]]:
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for d in DELTAS:
        pos = [I_REF + i * d for i in range(4)]
        assert max(pos) < N_CYC
        name = f"I4eq_d{d:02d}_@{','.join(map(str, pos))}"
        out.append((name, pat_bits(N_CYC, pos), pos))
    return out


def fmt(xs: list[int], lim: int = 24) -> str:
    if len(xs) <= lim:
        return str(xs)
    return str(xs[:lim])[:-1] + f", …] (n={len(xs)})"


def main() -> None:
    mode_defs = build_modes()
    modes = [(n, b) for n, b, _ in mode_defs]
    ones_by = {n: pos for n, _b, pos in mode_defs}

    probes = [("I", "I"), ("enable", "enable")] + [(a, b) for a, b, *_ in LANES]
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=OUT,
        tag=TAG,
        probes=probes,
        modes=modes,
        n_cyc=N_CYC,
    )
    by_mode = {name: [r for r in rows if r["mode_name"] == name] for name, _ in modes}

    out_csv = OUT / "I4eq_delta.csv"
    fields = ["mode", "cyc"] + [a for a, *_ in LANES]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in modes:
            for r in by_mode[name]:
                w.writerow({k: r[k] if k != "mode" else name for k in fields})

    n_m = len(modes)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, 1.55 * n_m), dpi=120, sharex=True)
    if n_m == 1:
        axes = [axes]
    # band covers densest (Δ=1 → last=5) through widest (Δ=11 → last=35)
    band0, band1 = I_REF - 0.5, I_REF + 3 * 11 + 0.5
    for ax, (name, _) in zip(axes, modes):
        rs = by_mode[name]
        for yi, (lab, _net, title, col) in enumerate(reversed(LANES)):
            for c in ones(rs, lab):
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
        for p in ones_by[name]:
            ax.axvline(p, color="#c00000", lw=0.7, alpha=0.45, zorder=0)
        ax.axvspan(band0, band1, color="#fff3cd", alpha=0.3, zorder=0)
        ax.set_yticks(range(len(LANES)))
        ax.set_yticklabels(
            [t for _a, _n, t, _c in reversed(LANES)], fontsize=6.2, family="monospace"
        )
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=7, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5)
        xh = ones(rs, "X")
        ax.set_title(
            f"{name} · mux.X n={len(xh)} · S/A0/A1="
            f"{len(ones(rs, 'S'))}/{len(ones(rs, 'A0'))}/{len(ones(rs, 'A1'))} "
            f"· sticky n={len(ones(rs, 'sticky_Q'))}",
            fontsize=8,
            loc="left",
        )
    axes[-1].set_xlabel("cycle (yellow = I4 span · red = I=1)")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in LANES],
        loc="upper right",
        ncol=6,
        fontsize=6.5,
        frameon=False,
    )
    fig.suptitle(
        f"4 equal-spaced I=1 · Δ=1..11 · I_REF={I_REF}  ·  mux S/A0/A1/X",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "I4eq_delta.png")

    md = [
        f"# 4 equal-spaced I=1 — Δ = 1..11 (I_REF={I_REF})",
        "",
        "```text",
        f"I@{{{I_REF}, {I_REF}+Δ, {I_REF}+2Δ, {I_REF}+3Δ}}   Δ = 1,2,…,11",
        "```",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "## Observe summary",
        "",
        "| mode | Δ | I ones | S n | A0 n | A1 n | X n | a31o.X n | sticky n |",
        "|------|--:|--------|----:|-----:|-----:|----:|---------:|---------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        pos = ones_by[name]
        d = (pos[1] - pos[0]) if len(pos) >= 2 else 0
        md.append(
            f"| `{name}` | {d} | `{pos or '∅'}` | {len(ones(rs, 'S'))} | "
            f"{len(ones(rs, 'A0'))} | {len(ones(rs, 'A1'))} | {len(ones(rs, 'X'))} | "
            f"{len(ones(rs, 'a31o_X'))} | {len(ones(rs, 'sticky_Q'))} |"
        )
    md += ["", "## Per-mode lanes", ""]
    for name, _ in modes:
        rs = by_mode[name]
        md.append(f"### `{name}`  I=`{ones_by[name] or '∅'}`")
        md.append("")
        for lab, _n, title, _c in LANES:
            md.append(f"- `{lab}` ({title}) high @ `{fmt(ones(rs, lab))}`")
        md.append("")
    md += [
        "Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/inv_2_6/run_I4eq_delta_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "I4eq_delta.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {png}  ({n_m} modes)")
    for name, _ in modes:
        rs = by_mode[name]
        print(
            f"  {name}: S/A0/A1/X="
            f"{len(ones(rs,'S'))}/{len(ones(rs,'A0'))}/{len(ones(rs,'A1'))}/{len(ones(rs,'X'))} "
            f"sticky n={len(ones(rs,'sticky_Q'))}"
        )


if __name__ == "__main__":
    main()
