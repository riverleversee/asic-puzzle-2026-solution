#!/usr/bin/env python3
"""Timeline: o211a_2_8 pins + I-independent stub outputs into this cone.

NO-I stubs (from only-I fan-in):
  inv_2_7__A / __Y · inv_2_9__A / __Y

Usage (from rework_coded/):
  python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_timeline.py
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
TAG = "and215_o211a_2_8"

# I-independent outputs that feed this section (fan-in stubs).
NOI_LANES = [
    (
        "inv7_A",
        "sky130_fd_sc_hd__inv_2_7__A",
        "NO-I  inv_2_7__A  → o211a.C1 / a22o.A1 / mux6.S",
        "#c45911",
    ),
    (
        "inv7_Y",
        "sky130_fd_sc_hd__inv_2_7__Y",
        "NO-I  inv_2_7__Y  → a22o.A1",
        "#e67e22",
    ),
    (
        "inv9_A",
        "sky130_fd_sc_hd__inv_2_9__A",
        "NO-I  inv_2_9__A  → mux6.A0 / inv_2_8.A",
        "#548235",
    ),
    (
        "inv9_Y",
        "sky130_fd_sc_hd__inv_2_9__Y",
        "NO-I  inv_2_9__Y  → a22o.B2",
        "#70ad47",
    ),
]

# Y = (A1 ∨ A2) ∧ B1 ∧ C1   (+ sink)
PIN_LANES = [
    ("A1", "sky130_fd_sc_hd__inv_2_8__A", "A1  inv_2_8__A (=mux.S)", "#1f4e79"),
    ("A2", "sky130_fd_sc_hd__mux2_1_7__A0", "A2  mux2_1_7__A0 =¬(A∧I)", "#5b9bd5"),
    ("B1", "sky130_fd_sc_hd__or2_2_7__X", "B1  or2_2_7__X =A∨I", "#7030a0"),
    ("C1", "sky130_fd_sc_hd__inv_2_7__A", "C1  = inv_2_7__A (same as NO-I)", "#c45911"),
    ("o211a_X", "sky130_fd_sc_hd__o211a_2_8__X", "o211a.X", "#c00000"),
    ("a22o_X", "sky130_fd_sc_hd__a22o_2_1__X", "a22o_2_1.X (sink)", "#833c0c"),
]

# C1 duplicates inv7_A net — keep both labels for pin clarity; probe once.
LANES = NOI_LANES + [L for L in PIN_LANES if L[0] != "C1"] + [
    # C1 kept as alias lane using same net (already probed as inv7_A)
    PIN_LANES[3],
]

# Probe unique nets only
STUB_LABS = [lab for lab, *_ in NOI_LANES]

MODES = [
    ("all0", pat_bits(N_CYC)),
    ("all1", pat_bits(N_CYC, fill="1")),
    ("I1_cyc1", pat_bits(N_CYC, [1])),
    ("I1_cyc10", pat_bits(N_CYC, [10])),
    ("I1_cyc1_12", pat_bits(N_CYC, [1, 12])),
]


def fmt(xs: list[int], lim: int = 20) -> str:
    if len(xs) <= lim:
        return str(xs)
    return str(xs[:lim])[:-1] + f", …] (n={len(xs)})"


def main() -> None:
    # Unique (lab, net) for probe — C1 shares net with inv7_A so skip C1 in probe
    seen_nets: set[str] = set()
    probes: list[tuple[str, str]] = [("I", "I"), ("enable", "enable")]
    for lab, net, *_ in NOI_LANES + PIN_LANES:
        if net in seen_nets:
            continue
        seen_nets.add(net)
        probes.append((lab, net))

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

    # Alias C1 ← inv7_A for plotting / CSV clarity
    for r in rows:
        r["C1"] = r["inv7_A"]

    display_lanes = NOI_LANES + PIN_LANES

    out_csv = OUT / "o211a_pins.csv"
    fields = ["mode", "cyc"] + [a for a, *_ in display_lanes]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in MODES:
            for r in by_mode[name]:
                w.writerow({k: r[k] if k != "mode" else name for k in fields})

    stub_indep = True
    for lab in STUB_LABS:
        s0 = [int(r[lab]) for r in by_mode["all0"]]
        s1 = [int(r[lab]) for r in by_mode["all1"]]
        if s0 != s1:
            stub_indep = False
            print(f"  WARN {lab} differs all0 vs all1")

    n_m = len(MODES)
    fig_h = 1.15 + 0.38 * len(display_lanes)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, fig_h * n_m), dpi=140, sharex=True)
    if n_m == 1:
        axes = [axes]
    for ax, (name, _) in zip(axes, MODES):
        rs = by_mode[name]
        for yi, (lab, _net, title, col) in enumerate(reversed(display_lanes)):
            for c in ones(rs, lab):
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
            # separator between NO-I block and pin block
        n_noi = len(NOI_LANES)
        sep_y = len(display_lanes) - n_noi - 0.5
        ax.axhline(sep_y, color="#999", lw=0.9, ls="--", zorder=0)
        ax.set_yticks(range(len(display_lanes)))
        ax.set_yticklabels(
            [t for _a, _n, t, _c in reversed(display_lanes)],
            fontsize=6.5,
            family="monospace",
        )
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=9, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5)
        ax.set_title(
            f"{name} · o211a.X n={len(ones(rs, 'o211a_X'))} · a22o.X n={len(ones(rs, 'a22o_X'))}",
            fontsize=9,
            loc="left",
        )
    axes[-1].set_xlabel("cycle (enable=1 after reset)")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in display_lanes],
        loc="upper right",
        ncol=5,
        fontsize=6.5,
        frameon=False,
    )
    fig.suptitle(
        "o211a_2_8 · top NO-I stubs (inv_2_7/9) · bottom pins (A1∨A2)∧B1∧C1 → a22o",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "o211a_pins.png")

    md = [
        "# `o211a_2_8` pin timelines (+ I-independent stub inputs)",
        "",
        "```text",
        "o211a_2_8.X  =  (A1 ∨ A2) ∧ B1 ∧ C1   →  a22o_2_1.B1",
        "A1 = inv_2_8__A          # mux.S",
        "A2 = mux2_1_7__A0        # ¬(or2_2_7__A ∧ I)",
        "B1 = or2_2_7__X          # or2_2_7__A ∨ I",
        "C1 = inv_2_7__A          # NO-I stub",
        "```",
        "",
        "## I-independent stub outputs into this section",
        "",
        "From only-I fan-in (`o211a_2_8__X_fanin_depth5`):",
        "",
        "| Net | Feeds | high (all0) |",
        "|-----|-------|-------------|",
    ]
    roles = {
        "inv7_A": "o211a.C1 · a22o.A1 · mux2_1_6.S",
        "inv7_Y": "a22o_2_1.A1",
        "inv9_A": "mux2_1_6.A0 · inv_2_8.A (prior)",
        "inv9_Y": "a22o_2_1.B2",
    }
    for lab, net, _t, _c in NOI_LANES:
        md.append(
            f"| `{net.replace('sky130_fd_sc_hd__', '')}` | {roles[lab]} | "
            f"`{fmt(ones(by_mode['all0'], lab))}` |"
        )
    md += [
        "",
        f"- All four NO-I lanes identical **all0 vs all1**: **{stub_indep}**",
        f"- `o211a.X` high (all0) @ `{fmt(ones(by_mode['all0'], 'o211a_X'))}`",
        "",
        "Figure (dashed line separates NO-I block from pin block): "
        f"[`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "Parent: [`../README.md`](../README.md)",
        "",
    ]
    for name, _ in MODES:
        rs = by_mode[name]
        md.append(f"## `{name}`")
        md.append("")
        md.append("### NO-I stubs")
        md.append("")
        for lab, _n, title, _c in NOI_LANES:
            md.append(f"- `{lab}` ({title}) high @ `{fmt(ones(rs, lab))}`")
        md.append("")
        md.append("### o211a pins / sink")
        md.append("")
        for lab, _n, title, _c in PIN_LANES:
            md.append(f"- `{lab}` ({title}) high @ `{fmt(ones(rs, lab))}`")
        md.append("")
    md += [
        "```bash",
        "python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "o211a_pins.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {png}")
    print(f"NO-I stubs all0==all1: {stub_indep}")
    for name, _ in MODES:
        rs = by_mode[name]
        print(
            f"  {name}: o211a.X n={len(ones(rs, 'o211a_X'))}  a22o.X n={len(ones(rs, 'a22o_X'))}"
        )


if __name__ == "__main__":
    main()
