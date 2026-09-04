#!/usr/bin/env python3
"""Timeline: k=2..5 equal-spaced I + all-11 ones in first 11 cycles (a31o arm).

Ones confined to cycles 0..10. Anchor I_REF=1 for k-sweeps.

  k-I : I@{1, 1+Δ, …, 1+(k-1)Δ}  while 1+(k-1)Δ ≤ 10
  all11: I high every cycle in 0..10

Usage (from rework_coded/):
  python3 phase2/and2_2_15/inv_2_6/run_Ik_all11_timeline.py
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
TAG = "and215_a31o_Ik_all11"
I_REF = 1
WIN_LAST = 10  # first 11 bits: cycles 0..10
K_RANGE = range(2, 6)  # 2..5

LANES = [
    ("inv9_A", "sky130_fd_sc_hd__inv_2_9__A", "NO-I  inv_2_9__A → a31o.A1", "#548235"),
    ("inv7_A", "sky130_fd_sc_hd__inv_2_7__A", "NO-I  inv_2_7__A → a31o.A2", "#c45911"),
    ("A3", "sky130_fd_sc_hd__mux2_1_7__X", "a31o.A3 mux2_1_7__X (→I)", "#1f4e79"),
    ("B1", "sky130_fd_sc_hd__inv_2_6__A", "a31o.B1 sticky Q", "#7030a0"),
    ("a31o_X", "sky130_fd_sc_hd__a31o_2_11__X", "a31o.X", "#c00000"),
    ("inv_Y", "sky130_fd_sc_hd__inv_2_6__Y", "inv_2_6.Y → and2.A", "#833c0c"),
    ("o211a_X", "sky130_fd_sc_hd__o211a_2_8__X", "o211a_2_8.X (observe)", "#bf8f00"),
]


def build_modes() -> list[tuple[str, str, list[int]]]:
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for k in K_RANGE:
        max_d = (WIN_LAST - I_REF) // (k - 1)
        for d in range(1, max_d + 1):
            pos = [I_REF + i * d for i in range(k)]
            assert max(pos) <= WIN_LAST
            name = f"I{k}eq_d{d:02d}_@{','.join(map(str, pos))}"
            out.append((name, pat_bits(N_CYC, pos), pos))
    all11 = list(range(0, WIN_LAST + 1))
    out.append((f"all11_@{all11[0]}..{all11[-1]}", pat_bits(N_CYC, all11), all11))
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

    out_csv = OUT / "Ik_all11.csv"
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
    for ax, (name, _) in zip(axes, modes):
        rs = by_mode[name]
        for yi, (lab, _net, title, col) in enumerate(reversed(LANES)):
            for c in ones(rs, lab):
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
        for p in ones_by[name]:
            ax.axvline(p, color="#c00000", lw=0.7, alpha=0.45, zorder=0)
        ax.axvspan(-0.5, WIN_LAST + 0.5, color="#fff3cd", alpha=0.35, zorder=0)
        ax.set_yticks(range(len(LANES)))
        ax.set_yticklabels(
            [t for _a, _n, t, _c in reversed(LANES)], fontsize=6.2, family="monospace"
        )
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=7, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5)
        sticky = ones(rs, "B1")
        ax.set_title(
            f"{name} · stickyQ n={len(sticky)} first={sticky[0] if sticky else '—'} "
            f"· inv.Y n={len(ones(rs, 'inv_Y'))} · a31o.X n={len(ones(rs, 'a31o_X'))}",
            fontsize=8,
            loc="left",
        )
    axes[-1].set_xlabel("cycle (yellow = first 11 · red ticks = I=1)")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in LANES],
        loc="upper right",
        ncol=4,
        fontsize=6.5,
        frameon=False,
    )
    fig.suptitle(
        "inv_2_6 / a31o_2_11 · k=2..5 equal-spaced I + all11 in first 11 cycles",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "Ik_all11.png")

    md = [
        "# `inv_2_6` / `a31o_2_11` — k=2..5 + all11 (first 11 cycles)",
        "",
        f"Ones only in cycles `0..{WIN_LAST}` (first 11 bits). Anchor `I_REF={I_REF}` for k-sweeps.",
        "",
        "```text",
        "k-I : I@{1, 1+Δ, …, 1+(k-1)Δ}   k=2..5, Δ while last ≤ 10",
        "all11: I high on every cycle 0..10",
        "```",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "Sibling (o211a): "
        "[`../o211a_2_8/timelines/Ik_all11.md`](../o211a_2_8/timelines/Ik_all11.md)",
        "",
        "Earlier (2/3 in first 14): [`I2_I3_spacing.md`](I2_I3_spacing.md)",
        "",
        "## Sticky / fail observe",
        "",
        "| mode | #I | I ones | sticky Q n | first Q | inv.Y n | a31o.X n | o211a.X n |",
        "|------|---:|--------|-----------:|--------:|--------:|---------:|----------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        q = ones(rs, "B1")
        pos = ones_by[name]
        md.append(
            f"| `{name}` | {len(pos)} | `{pos or '∅'}` | {len(q)} | "
            f"{q[0] if q else '—'} | {len(ones(rs, 'inv_Y'))} | "
            f"{len(ones(rs, 'a31o_X'))} | {len(ones(rs, 'o211a_X'))} |"
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
        "python3 phase2/and2_2_15/inv_2_6/run_Ik_all11_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "Ik_all11.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {png}  ({n_m} modes)")
    for name, _ in modes:
        rs = by_mode[name]
        q = ones(rs, "B1")
        print(
            f"  {name}: sticky n={len(q)} first={q[0] if q else '—'} "
            f"inv.Y n={len(ones(rs, 'inv_Y'))}"
        )


if __name__ == "__main__":
    main()
