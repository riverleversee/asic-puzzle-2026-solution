#!/usr/bin/env python3
"""Timeline: mux2_1_7 inputs S/A0/A1 (+ X) under 1/2/3 I ones from cyc 2.

Higher-level (inv_2_6 / a31o arm) observe of the fail-trip mux:

  S  = inv_2_8__A
  A0 = mux2_1_7__A0 = ¬(or2_2_7__A ∧ I)
  A1 = or2_2_7__X   = or2_2_7__A ∨ I
  X  = S ? A1 : A0  → a31o.A3

Patterns (I_REF=2):
  1-I : I@{2+d}              d = 0..12
  2-I : I@{2, 2+Δ}           Δ = 1..12
  3-I : I@{2, 2+Δ, 2+2Δ}     Δ = 1..6

Usage (from rework_coded/):
  python3 phase2/and2_2_15/inv_2_6/run_mux_pins_I123_from2_timeline.py
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
TAG = "and215_mux_I123_from2"
I_REF = 2

LANES = [
    ("S", "sky130_fd_sc_hd__inv_2_8__A", "mux.S  inv_2_8__A", "#1f4e79"),
    ("A0", "sky130_fd_sc_hd__mux2_1_7__A0", "mux.A0  ¬(A∧I)", "#548235"),
    ("A1", "sky130_fd_sc_hd__or2_2_7__X", "mux.A1  A∨I", "#c45911"),
    ("X", "sky130_fd_sc_hd__mux2_1_7__X", "mux.X → a31o.A3", "#c00000"),
    ("a31o_X", "sky130_fd_sc_hd__a31o_2_11__X", "a31o.X (observe)", "#7030a0"),
    ("sticky_Q", "sky130_fd_sc_hd__inv_2_6__A", "sticky Q", "#833c0c"),
]


def build_modes() -> list[tuple[str, str, list[int]]]:
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for d in range(0, 13):
        pos = [I_REF + d]
        assert max(pos) < N_CYC
        name = f"I1_@{pos[0]}"
        out.append((name, pat_bits(N_CYC, pos), pos))
    for d in range(1, 13):
        pos = [I_REF, I_REF + d]
        assert max(pos) < N_CYC
        name = f"I2_d{d:02d}_@{','.join(map(str, pos))}"
        out.append((name, pat_bits(N_CYC, pos), pos))
    for d in range(1, 7):
        pos = [I_REF, I_REF + d, I_REF + 2 * d]
        assert max(pos) < N_CYC
        name = f"I3eq_d{d:02d}_@{','.join(map(str, pos))}"
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

    out_csv = OUT / "mux_pins_I123_from2.csv"
    fields = ["mode", "cyc"] + [a for a, *_ in LANES]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in modes:
            for r in by_mode[name]:
                w.writerow({k: r[k] if k != "mode" else name for k in fields})

    n_m = len(modes)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, 1.45 * n_m), dpi=110, sharex=True)
    if n_m == 1:
        axes = [axes]
    band0, band1 = I_REF - 0.5, I_REF + 12.5
    for ax, (name, _) in zip(axes, modes):
        rs = by_mode[name]
        for yi, (lab, _net, title, col) in enumerate(reversed(LANES)):
            for c in ones(rs, lab):
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
        for p in ones_by[name]:
            ax.axvline(p, color="#c00000", lw=0.7, alpha=0.45, zorder=0)
        ax.axvspan(band0, band1, color="#fff3cd", alpha=0.35, zorder=0)
        ax.set_yticks(range(len(LANES)))
        ax.set_yticklabels(
            [t for _a, _n, t, _c in reversed(LANES)], fontsize=6.0, family="monospace"
        )
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=6.5, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5)
        xh = ones(rs, "X")
        ax.set_title(
            f"{name} · mux.X n={len(xh)} first={xh[0] if xh else '—'} "
            f"· S n={len(ones(rs, 'S'))} A0 n={len(ones(rs, 'A0'))} A1 n={len(ones(rs, 'A1'))}",
            fontsize=7.5,
            loc="left",
        )
    axes[-1].set_xlabel(f"cycle (yellow ≈ cyc {I_REF}..{I_REF+12} · red = I=1)")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in LANES],
        loc="upper right",
        ncol=6,
        fontsize=6,
        frameon=False,
    )
    fig.suptitle(
        f"mux2_1_7 pins S/A0/A1/X · 1/2/3 I from I_REF={I_REF}  ·  X=S?A1:A0 → a31o.A3",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "mux_pins_I123_from2.png")

    md = [
        f"# mux2_1_7 pins — 1/2/3 I from cyc {I_REF}",
        "",
        "Higher-level (inv_2_6) timeline of the three mux inputs + output.",
        "",
        "```text",
        "mux2_1_7:",
        "  S  = inv_2_8__A",
        "  A0 = mux2_1_7__A0 = ¬(or2_2_7__A ∧ I)",
        "  A1 = or2_2_7__X   = or2_2_7__A ∨ I",
        "  X  = S ? A1 : A0  → a31o.A3",
        "",
        f"1-I : I@{{{I_REF}+d}}           d = 0..12",
        f"2-I : I@{{{I_REF}, {I_REF}+Δ}}        Δ = 1..12",
        f"3-I : I@{{{I_REF}, {I_REF}+Δ, {I_REF}+2Δ}}  Δ = 1..6",
        "```",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "## Observe summary",
        "",
        "| mode | I ones | S n | A0 n | A1 n | X n | first X | a31o.X n | sticky n |",
        "|------|--------|----:|-----:|-----:|----:|--------:|---------:|---------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        xh = ones(rs, "X")
        md.append(
            f"| `{name}` | `{ones_by[name] or '∅'}` | {len(ones(rs, 'S'))} | "
            f"{len(ones(rs, 'A0'))} | {len(ones(rs, 'A1'))} | {len(xh)} | "
            f"{xh[0] if xh else '—'} | {len(ones(rs, 'a31o_X'))} | "
            f"{len(ones(rs, 'sticky_Q'))} |"
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
        "python3 phase2/and2_2_15/inv_2_6/run_mux_pins_I123_from2_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "mux_pins_I123_from2.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {png}  ({n_m} modes)")
    for name, _ in modes:
        rs = by_mode[name]
        xh = ones(rs, "X")
        print(
            f"  {name}: X n={len(xh)} first={xh[0] if xh else '—'} "
            f"S/A0/A1={len(ones(rs,'S'))}/{len(ones(rs,'A0'))}/{len(ones(rs,'A1'))}"
        )


if __name__ == "__main__":
    main()
