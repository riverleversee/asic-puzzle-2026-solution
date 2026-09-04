#!/usr/bin/env python3
"""Clear mux2_1_7 ↔ a31o_2_11 pin-dependence figure.

Shows how mux A0/A1/S drive X (= a31o.A3), and how A1∧A2∧A3 trips
the sticky fail latch — with the inhibit note (hold X=0).

Usage (from rework_coded/):
  python3 phase3/and2_2_15/run_mux_dependence_figure.py
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from rework_paths import savefig_locked  # noqa: E402

OUT = HERE / "figures"


def box(ax, x, y, w, h, text, fc="#f5f5f5", ec="#333", lw=1.2, fs=8, weight="normal"):
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=fc,
            edgecolor=ec,
            lw=lw,
            zorder=3,
        )
    )
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        family="monospace",
        fontweight=weight,
        zorder=4,
    )


def arrow(ax, x0, y0, x1, y1, color="#444", lw=1.2):
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw),
        zorder=2,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 7.2), dpi=150)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title(
        "mux2_1_7 → a31o.A3  ·  pin dependence  ·  hold X=0 to block I-indep FAIL trip",
        fontsize=12,
        pad=12,
    )

    box(ax, 1.4, 6.2, 2.0, 0.7, "I\n(primary)", fc="#fce4d6", ec="#c00000", weight="bold")
    box(ax, 1.4, 4.6, 2.2, 0.9, "or2_2_7__A\n(dfrtp_2_27.Q)", fc="#fff2cc", ec="#bf8f00")
    box(
        ax,
        1.4,
        2.8,
        2.2,
        0.9,
        "inv_2_8__A\n(dfrtp_2_29.Q)\n= mux.S",
        fc="#ddebf7",
        ec="#1f4e79",
        weight="bold",
    )

    box(
        ax,
        4.2,
        5.8,
        2.4,
        1.1,
        "nand2_2_25\nA0 = ¬(A ∧ I)\nA=or2_2_7__A",
        fc="#e2efda",
        ec="#548235",
    )
    box(ax, 4.2, 4.0, 2.4, 0.9, "or2_2_7\nA1 = A ∨ I", fc="#e2efda", ec="#548235")

    arrow(ax, 2.4, 6.2, 3.0, 6.1)
    arrow(ax, 2.5, 4.8, 3.0, 5.5)
    arrow(ax, 2.5, 4.4, 3.0, 4.2)
    arrow(ax, 2.4, 6.0, 3.0, 4.3)
    ax.text(2.7, 5.35, "I", fontsize=7, color="#c00000")

    box(
        ax,
        7.2,
        4.9,
        2.8,
        2.4,
        "mux2_1_7\n\n"
        "S  = inv_2_8__A\n"
        "A0 = nand out\n"
        "A1 = or2 out\n"
        "X  = S? A1 : A0",
        fc="#f3e8ff",
        ec="#7030a0",
        lw=1.8,
        fs=8,
        weight="bold",
    )
    arrow(ax, 5.4, 5.8, 5.85, 5.5)
    arrow(ax, 5.4, 4.0, 5.85, 4.5)
    arrow(ax, 2.5, 2.8, 5.85, 4.0)
    ax.text(5.55, 5.65, "A0", fontsize=7, color="#548235")
    ax.text(5.55, 4.15, "A1", fontsize=7, color="#548235")
    ax.text(4.0, 3.2, "S", fontsize=8, color="#1f4e79", fontweight="bold")

    box(
        ax,
        10.0,
        4.9,
        2.0,
        0.8,
        "mux.X\n= a31o.A3",
        fc="#fce4d6",
        ec="#c00000",
        weight="bold",
        lw=1.6,
    )
    arrow(ax, 8.6, 4.9, 9.0, 4.9, color="#c00000", lw=1.6)
    ax.text(8.7, 5.2, "X", fontsize=8, color="#c00000", fontweight="bold")

    box(ax, 10.0, 7.0, 2.4, 0.7, "A1 inv_2_9__A\nNO-I  @≡10 mod11", fc="#c6efce", ec="#006100")
    box(ax, 10.0, 6.1, 2.4, 0.7, "A2 inv_2_7__A\nNO-I  always 1*", fc="#c6efce", ec="#006100")
    ax.text(10.0, 5.55, "*and2b.Y with A_N=0 on all0", fontsize=6, color="#555", ha="center")

    box(
        ax,
        12.5,
        5.5,
        2.2,
        1.8,
        "a31o_2_11\n\n"
        "Y=(A1∧A2∧A3)∨B1",
        fc="#fff2cc",
        ec="#833c0c",
        lw=1.6,
        weight="bold",
    )
    arrow(ax, 11.0, 7.0, 11.45, 6.2)
    arrow(ax, 11.0, 6.1, 11.45, 5.7)
    arrow(ax, 11.0, 4.9, 11.45, 5.2, color="#c00000", lw=1.5)

    box(ax, 12.5, 3.2, 2.2, 1.1, "dfrtp_2_28\nQ=inv_2_6__A\n(sticky B1)", fc="#ddebf7", ec="#1f4e79")
    box(
        ax,
        12.5,
        1.7,
        2.2,
        0.9,
        "inv_2_6.Y\n= ¬Q\n→ and2.A",
        fc="#fce4d6",
        ec="#c00000",
        weight="bold",
    )
    arrow(ax, 12.5, 4.55, 12.5, 3.8)
    arrow(ax, 12.5, 2.6, 12.5, 2.2)
    ax.annotate(
        "",
        xy=(11.4, 5.0),
        xytext=(11.4, 3.2),
        arrowprops=dict(
            arrowstyle="->", color="#1f4e79", lw=1.0, connectionstyle="arc3,rad=-0.35"
        ),
    )
    ax.text(10.55, 4.0, "B1\nfeedback", fontsize=6, color="#1f4e79", ha="center")

    box(
        ax,
        4.5,
        1.3,
        7.5,
        1.4,
        "FAIL TRIP (I-independent): at cyc ≡ 10 (mod 11), A1∧A2 live.\n"
        "If mux.X (A3) = 1 → a31o AND fires → sticky Q sets → inv.Y=0 → and2_15 blocked.\n"
        "INHIBIT: hold mux.X = 0 on those windows so (A1∧A2∧A3) cannot trip.",
        fc="#fff",
        ec="#c00000",
        lw=1.4,
        fs=8,
    )

    ax.text(
        7.2,
        3.35,
        "S=0 → X=A0=¬(A∧I)   ·   S=1 → X=A1=(A∨I)",
        ha="center",
        fontsize=8,
        family="monospace",
        color="#7030a0",
        fontweight="bold",
    )

    fig.tight_layout()
    png = savefig_locked(fig, OUT / "mux2_1_7_a31o_dependence.png")
    print(f"wrote {png}")

    phase2 = ROOT / "phase2" / "and2_2_15" / "inv_2_6"
    if phase2.is_dir():
        dest = phase2 / "mux2_1_7_a31o_dependence.png"
        shutil.copy2(png, dest)
        print(f"copied → {dest}")


if __name__ == "__main__":
    main()
