#!/usr/bin/env python3
"""Phase-1 writeup figures: overview, operator matches, Status A/B, die maps.

Reads operator_matches.json (+ cone / instance CSV for die maps).
Writes PNG@200dpi and SVG under rework/phase1/figures/.

Per-group die maps (style of 04) are written twice:
  figures/die_maps_technical/  — original group / operator jargon
  figures/die_maps_plain/      — plain labels from fingerprint class/motifs/size only
                               (no post-solve narrative)
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.transforms import blended_transform_factory

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p  # rework_coded/
import sys
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

import match_complex_operators as mco
from match_complex_operators import fanin_nodes
from structural_drivers import parse_structural

MATCH_JSON = ROOT / "phase1" / "operator_matches.json"
STRUCTURAL_V = ROOT / "netlist" / "puzzle_structural.v"
CSV = ROOT / "netlist" / "puzzle_instances.csv"
CONF = ROOT / "lib" / "exclude_bbox.conf"
OUT = ROOT / "phase1" / "figures"

CLASS_COLOR = {
    "shift_register": "#1f4e79",
    "wide_and_reduce": "#c45911",
    "ripple_adder": "#548235",
    "equality_comparator": "#7030a0",
    "fsm_control": "#7f7f7f",
    "lfsr_crc": "#2e75b6",
    "serial_deserializer": "#c45911",
}
CLASS_LABEL = {
    "shift_register": "SIPO / shift register",
    "wide_and_reduce": "AND-reduce / check",
    "ripple_adder": "FA / adder-like chain",
    "equality_comparator": "Comparator",
    "fsm_control": "Control / FSM",
    "lfsr_crc": "LFSR / CRC-like",
    "serial_deserializer": "Serial gather + check",
}

PER_GROUP_ROOTS = {
    "G_set_inv": "sky130_fd_sc_hd__inv_2_23__A",
    "G_set_and2": "sky130_fd_sc_hd__and2_2_15__X",
    "G_hold_B2": "sky130_fd_sc_hd__a32o_2_4__B2",
    "G_main_check": "sky130_fd_sc_hd__and3_2_6__X",
    "G_and4b_join": "sky130_fd_sc_hd__and4b_2_3__X",
    "G_status_A": "sky130_fd_sc_hd__or2_2_11__A",
    "G_status_B": "sky130_fd_sc_hd__or2_2_11__B",
    "G_success_glue": "sky130_fd_sc_hd__a32o_2_4__X",
}

# Combo groupings = union of G_* fan-ins (same defs as match_complex_operators).
COMBO_PARTS = {
    "C_status_A_plus_B": ["G_status_A", "G_status_B"],
    "C_and4b_all_inputs": ["G_main_check", "G_status_A", "G_status_B"],
    "C_full_set_path": ["G_and4b_join", "G_set_and2", "G_set_inv"],
    "C_set_plus_hold": ["G_and4b_join", "G_set_and2", "G_set_inv", "G_hold_B2"],
    "C_main_plus_statusA": ["G_main_check", "G_status_A"],
    "C_entire_a32o": ["G_success_glue"],
}

DIE_GROUPS = [
    ("G_set_inv", "SIPO", "shift_register", True),
    ("G_status_A", "Status A", "wide_and_reduce", True),
    # AND-join fan-in bbox spans most of the cone — points only on the overview.
    ("G_set_and2", "AND join", "wide_and_reduce", False),
    ("G_main_check", "Main check", "ripple_adder", False),
]

FRIENDLY_GROUP = {
    "G_set_inv": "Shift / SIPO bank",
    "G_set_and2": "SET AND path",
    "G_hold_B2": "Hold (B2)",
    "G_main_check": "Main leaf bank",
    "G_and4b_join": "Main+D join",
    "G_status_A": "Status A",
    "G_status_B": "Status B",
    "G_success_glue": "Success glue",
    "C_status_A_plus_B": "Status A+B combo",
    "C_and4b_all_inputs": "Main+status combo",
    "C_full_set_path": "Full set-path combo",
    "C_set_plus_hold": "Set+hold combo",
    "C_main_plus_statusA": "Main+Status A combo",
    "C_entire_a32o": "Entire a32o combo",
}

# Plain labels: designed from fingerprint class / motifs / size only
# (no post-solve narrative). See agent-designed copy in PLAIN_* below.
PLAIN_GROUP = {
    "G_set_inv": {
        "title": "Eight-bit shift bank",
        "purpose": "Takes bits in over successive clocks and holds\nthem as a parallel group (enable + latch motifs).",
    },
    "G_set_and2": {
        "title": "Medium all-ones check",
        "purpose": "Combines roughly five signals so the output\nis true only if every bit is high.",
    },
    "G_hold_B2": {
        "title": "Compact all-ones check",
        "purpose": "Same style of all-high check as the medium\nblock, but on a smaller set of signals.",
    },
    "G_main_check": {
        "title": "Large ripple-style adder",
        "purpose": "Adds multi-bit values by carrying from one\nbit stage to the next across a large cone.",
    },
    "G_and4b_join": {
        "title": "Wide adder-like datapath",
        "purpose": "Slightly larger cluster in the same adder\nfamily of linked full-adder style stages.",
    },
    "G_status_A": {
        "title": "Latched all-ones flag",
        "purpose": "Wide all-high check with sticky OR so a\nonce-true condition can stay asserted.",
    },
    "G_status_B": {
        "title": "Second latched flag",
        "purpose": "Companion sticky/all-ones style flag block\npaired with the first status flag.",
    },
    "G_success_glue": {
        "title": "Top mixed adder cone",
        "purpose": "Upper cone whose strongest match is\nripple-adder arithmetic (likely mixed logic).",
    },
    "C_status_A_plus_B": {
        "title": "Both status-flag blocks",
        "purpose": "Union of the two latched all-ones / sticky\nflag groupings.",
    },
    "C_and4b_all_inputs": {
        "title": "Adder plus both flags",
        "purpose": "Union of the large adder-like bank with\nboth status-flag groupings.",
    },
    "C_full_set_path": {
        "title": "Join, AND-check, and shift",
        "purpose": "Union of the wide join, medium all-ones\ncheck, and eight-bit shift bank.",
    },
    "C_set_plus_hold": {
        "title": "Set path plus hold check",
        "purpose": "Full set-path union plus the compact\nall-ones / hold-side check.",
    },
    "C_main_plus_statusA": {
        "title": "Adder plus one flag",
        "purpose": "Union of the large ripple-style adder\nwith the latched all-ones flag.",
    },
    "C_entire_a32o": {
        "title": "Top mixed adder cone",
        "purpose": "Same upper cone as the top mixed adder\ngrouping (alias of that fan-in).",
    },
}

PLAIN_CLASS = {
    "shift_register": "Clocked chain: serial in, parallel out",
    "wide_and_reduce": "True only when every input bit is high",
    "ripple_adder": "Binary adder from linked full-adder stages",
    "equality_comparator": "Equality comparator",
    "fsm_control": "Control / state machine",
    "lfsr_crc": "Linear feedback / CRC-style bit mix",
    "serial_deserializer": "Serial gather into a parallel check",
}


def save(fig: plt.Figure, stem: str, subdir: Path | None = None) -> None:
    dest = OUT if subdir is None else subdir
    dest.mkdir(parents=True, exist_ok=True)
    png = dest / f"{stem}.png"
    svg = dest / f"{stem}.svg"
    fig.savefig(png, dpi=200, bbox_inches="tight", pad_inches=0.35, facecolor="white")
    fig.savefig(svg, bbox_inches="tight", pad_inches=0.35, facecolor="white")
    plt.close(fig)
    try:
        print(f"wrote {png.relative_to(OUT)}")
    except ValueError:
        print(f"wrote {png}")


def rounded(ax, xy, w, h, **kw):
    p = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        **kw,
    )
    ax.add_patch(p)
    return p


def fig_chip_overview() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("Chip overview — success path", fontsize=16, fontweight="bold", pad=12)

    boxes = [
        (0.3, 1.3, 1.6, 1.4, "#1f4e79", "Serial I"),
        (2.3, 1.3, 2.0, 1.4, "#2e75b6", "Shift /\nhistory\n(SIPO)"),
        (4.7, 1.3, 2.2, 1.4, "#548235", "FA / phase\ndecode\n(or4)"),
        (7.3, 1.3, 2.2, 1.4, "#c45911", "Sticky leaf\nchecks\n(Σ = 2)"),
        (9.9, 1.3, 1.7, 1.4, "#833c0c", "success"),
    ]
    for x, y, w, h, color, label in boxes:
        rounded(ax, (x, y), w, h, facecolor=color, edgecolor="#222", lw=1.2, alpha=0.92)
        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            color="white",
            fontsize=11,
            fontweight="bold",
            linespacing=1.25,
        )

    for i in range(len(boxes) - 1):
        x0 = boxes[i][0] + boxes[i][2]
        x1 = boxes[i + 1][0]
        ymid = boxes[i][1] + boxes[i][3] / 2
        ax.annotate(
            "",
            xy=(x1 - 0.05, ymid),
            xytext=(x0 + 0.05, ymid),
            arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.6),
        )

    ax.text(
        6.0,
        0.45,
        "Pattern matching recovered familiar blocks (SIPO, AND-reduce, FA-like chain)\n"
        "before exact leaf / FA-period rules locked the input sequence.",
        ha="center",
        va="center",
        fontsize=10,
        color="#333",
    )
    save(fig, "01_chip_overview")


def fig_operator_matches(ranking: list[dict]) -> None:
    rows = [r for r in ranking if r["group"].startswith("G_") and r["score"] >= 0.55]
    rows = sorted(rows, key=lambda r: -r["score"])[:7]

    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.axis("off")
    ax.set_title(
        "Operator pattern matches — success-cone groupings",
        fontsize=16,
        fontweight="bold",
        pad=14,
    )

    headers = ["Group", "Best match", "Score", "Nodes", "Notes"]
    col_x = [0.04, 0.28, 0.58, 0.68, 0.78]
    y0 = 0.88
    for hx, h in zip(col_x, headers):
        ax.text(hx, y0, h, transform=ax.transAxes, fontsize=11, fontweight="bold", color="#222")
    ax.plot([0.03, 0.97], [0.84, 0.84], transform=ax.transAxes, color="#bbb", lw=1.0)

    y = 0.76
    for r in rows:
        op_id = r["best_id"]
        color = CLASS_COLOR.get(op_id, "#444")
        label = FRIENDLY_GROUP.get(r["group"], r["group"])
        note = (r.get("granular_summary") or "")[:42]
        if len(r.get("granular_summary") or "") > 42:
            note = note.rstrip() + "…"

        ax.add_patch(
            Rectangle(
                (0.58, y - 0.025),
                0.08 * float(r["score"]),
                0.05,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="none",
                clip_on=False,
            )
        )
        ax.text(0.04, y, label, transform=ax.transAxes, fontsize=10.5, color="#222", va="center")
        ax.text(
            0.28,
            y,
            CLASS_LABEL.get(op_id, r["best_op"]),
            transform=ax.transAxes,
            fontsize=10.5,
            color=color,
            fontweight="bold",
            va="center",
        )
        ax.text(
            0.585,
            y,
            f"{r['score']:.3f}",
            transform=ax.transAxes,
            fontsize=10.5,
            family="monospace",
            va="center",
        )
        ax.text(
            0.69,
            y,
            str(r["n_nodes"]),
            transform=ax.transAxes,
            fontsize=10.5,
            family="monospace",
            va="center",
        )
        ax.text(0.78, y, note, transform=ax.transAxes, fontsize=9, color="#555", va="center")
        y -= 0.095

    handles = [
        mpatches.Patch(color=CLASS_COLOR[k], label=CLASS_LABEL[k])
        for k in ("shift_register", "wide_and_reduce", "ripple_adder")
    ]
    ax.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.02),
        ncol=3,
        frameon=False,
        fontsize=10,
    )
    ax.text(
        0.5,
        -0.02,
        "Scores compare cone subgraphs to a library of known RTL operator fingerprints.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9.5,
        color="#444",
    )
    save(fig, "02_operator_matches")


def fig_status_ab() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.set_title("Status A / Status B — one-cycle SET window", fontsize=16, fontweight="bold", pad=10)

    rounded(ax, (0.4, 1.2), 5.6, 4.2, facecolor="#eef5fb", edgecolor="#1f4e79", lw=1.6)
    ax.text(3.2, 5.0, "Status A  (arm)", ha="center", fontsize=13, fontweight="bold", color="#1f4e79")
    ax.text(
        3.2,
        3.5,
        "Sticky OR status bit\n\n"
        "• Arms when FA/state decode matches\n"
        "• Once high, stays high\n"
        "• Gates enable into the shift path",
        ha="center",
        va="center",
        fontsize=11,
        color="#222",
        linespacing=1.35,
    )

    rounded(ax, (8.0, 1.2), 5.6, 4.2, facecolor="#fbf3eb", edgecolor="#c45911", lw=1.6)
    ax.text(10.8, 5.0, "Status B  (close)", ha="center", fontsize=13, fontweight="bold", color="#c45911")
    ax.text(
        10.8,
        3.5,
        "Sticky lag of A\n\n"
        "• B ← A ∨ B\n"
        "• Rises one cycle after A\n"
        "• Ends the SET pulse window",
        ha="center",
        va="center",
        fontsize=11,
        color="#222",
        linespacing=1.35,
    )

    rounded(ax, (5.3, 0.25), 3.4, 0.75, facecolor="#fff", edgecolor="#333", lw=1.2)
    ax.text(
        7.0,
        0.62,
        "SET needs  A ∧ ¬B  (and leaf banks)",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#333",
    )

    ax.annotate(
        "",
        xy=(8.0, 3.3),
        xytext=(6.0, 3.3),
        arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.5),
    )
    ax.text(7.0, 3.55, "A feeds B", ha="center", fontsize=9, color="#555")

    save(fig, "03_status_ab")


def load_bbox() -> dict[str, float]:
    b: dict[str, float] = {}
    if not CONF.exists():
        return {
            "EXCLUDE_XMIN": 148.0,
            "EXCLUDE_XMAX": 220.0,
            "EXCLUDE_YMIN": 80.0,
            "EXCLUDE_YMAX": 262.0,
        }
    for line in CONF.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        b[k.strip()] = float(v.strip())
    return b


def load_positions() -> dict[str, tuple[float, float]]:
    pos: dict[str, tuple[float, float]] = {}
    with CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                pos[row["instance"]] = (float(row["x_um"]), float(row["y_um"]))
            except (KeyError, ValueError):
                continue
    return pos


def points_for(nodes, drivers, pos):
    pts = []
    for n in nodes:
        info = drivers.get(n)
        if not info:
            continue
        inst = info.get("instance")
        if inst and inst in pos:
            pts.append(pos[inst])
    return pts


def _data_extent(bg_pts, bbox) -> tuple[float, float, float, float]:
    xs = [bbox["EXCLUDE_XMAX"]]
    ys = [bbox["EXCLUDE_YMAX"]]
    if bg_pts:
        xs.extend(x for x, _ in bg_pts)
        ys.extend(y for _, y in bg_pts)
    return -5.0, max(xs) + 8.0, -5.0, max(ys) + 8.0


def _draw_og_and_bg(ax, bbox, bg_pts) -> None:
    ax.set_facecolor("#fafafa")
    ox0, oy0 = bbox["EXCLUDE_XMIN"], bbox["EXCLUDE_YMIN"]
    ox1, oy1 = bbox["EXCLUDE_XMAX"], bbox["EXCLUDE_YMAX"]
    ax.add_patch(
        Rectangle(
            (ox0, oy0),
            ox1 - ox0,
            oy1 - oy0,
            facecolor="#ececec",
            edgecolor="#999",
            lw=1.0,
            ls="--",
            alpha=0.7,
            zorder=0,
        )
    )
    # Right-side margin tag — stays off the die cells.
    trans = blended_transform_factory(ax.transAxes, ax.transData)
    ax.annotate(
        "Output generator\n(ignored early)",
        xy=(1.0, (oy0 + oy1) / 2),
        xycoords=trans,
        xytext=(1.02, (oy0 + oy1) / 2),
        textcoords=trans,
        ha="left",
        va="center",
        fontsize=8,
        color="#666",
        clip_on=False,
        arrowprops=dict(arrowstyle="-", color="#999", lw=0.8, shrinkA=0, shrinkB=0),
        zorder=1,
    )
    if bg_pts:
        xs, ys = zip(*bg_pts)
        ax.scatter(xs, ys, s=8, c="#d0d0d0", alpha=0.5, zorder=2, label="Other success-cone cells")


def _draw_cluster_box(ax, pts, color: str, pad: float = 4.0):
    xs, ys = zip(*pts)
    xmin, xmax = min(xs) - pad, max(xs) + pad
    ymin, ymax = min(ys) - pad, max(ys) + pad
    ax.add_patch(
        FancyBboxPatch(
            (xmin, ymin),
            xmax - xmin,
            ymax - ymin,
            boxstyle="round,pad=0.3,rounding_size=1.5",
            fill=False,
            edgecolor=color,
            lw=1.6,
            zorder=6,
        )
    )
    return xmin, xmax, ymin, ymax


def _exterior_tag(
    ax,
    *,
    label: str,
    color: str,
    box: tuple[float, float, float, float],
    slot: int = 0,
    n_slots: int = 1,
) -> None:
    """Short tag above the axes; color matches the cluster box (no leader over the die)."""
    if n_slots <= 1:
        x_frac = 0.50
    else:
        x_frac = 0.18 + 0.64 * slot / max(n_slots - 1, 1)
    ax.text(
        x_frac,
        1.06,
        label,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        color=color,
        clip_on=False,
        zorder=8,
        bbox=dict(boxstyle="round,pad=0.28", fc="white", ec=color, alpha=0.96, lw=1.1),
    )


def _setup_die_figure(title: str, subtitle: str | None = None):
    fig = plt.figure(figsize=(12.0, 10.4))
    # Leave right margin for OG label; top margin for cluster tags + title.
    ax = fig.add_axes([0.08, 0.11, 0.78, 0.66])
    fig.text(0.48, 0.97, title, ha="center", va="top", fontsize=14, fontweight="bold", color="#222")
    if subtitle:
        fig.text(
            0.48,
            0.935,
            subtitle.replace("\n", " "),
            ha="center",
            va="top",
            fontsize=10,
            color="#444",
            linespacing=1.25,
        )
    return fig, ax


def _finish_die_axes(ax, bbox, bg_pts) -> None:
    ax.set_xlabel("X (µm)", fontsize=11)
    ax.set_ylabel("Y (µm)", fontsize=11)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.2)
    x0, x1, y0, y1 = _data_extent(bg_pts, bbox)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)


def _legend_below(ax, handles=None) -> None:
    kw = dict(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=2,
        fontsize=9,
        frameon=False,
        borderaxespad=0,
    )
    if handles is not None:
        ax.legend(handles=handles, **kw)
    else:
        ax.legend(**kw)


def fig_die_hotspots() -> None:
    drivers, stubs, _meta = parse_structural(STRUCTURAL_V)
    pos = load_positions()
    bbox = load_bbox()
    bg_pts = points_for(fanin_nodes(PER_GROUP_ROOTS["G_success_glue"], drivers, stubs), drivers, pos)

    fig, ax = _setup_die_figure(
        "Die hotspots — strong operator matches on the success cone",
        "Colored boxes mark high-confidence groupings; name tags sit above the die.",
    )
    _draw_og_and_bg(ax, bbox, bg_pts)
    _finish_die_axes(ax, bbox, bg_pts)

    legend_handles = []
    boxed: list[tuple] = []
    order = sorted(DIE_GROUPS, key=lambda t: (t[3], t[0]))
    for gid, nice, op_id, draw_box in order:
        nodes = fanin_nodes(PER_GROUP_ROOTS[gid], drivers, stubs)
        pts = points_for(nodes, drivers, pos)
        color = CLASS_COLOR.get(op_id, "#444")
        if not pts:
            continue
        xs, ys = zip(*pts)
        ax.scatter(
            xs,
            ys,
            s=14 if not draw_box else 26,
            c=color,
            alpha=0.55 if not draw_box else 0.9,
            zorder=3 if not draw_box else 5,
            edgecolors="#222" if draw_box else "none",
            linewidths=0.25 if draw_box else 0,
        )
        if draw_box:
            box = _draw_cluster_box(ax, pts, color, pad=3.0)
            boxed.append((nice, color, box))
        legend_handles.append(
            mpatches.Patch(
                color=color,
                label=f"{nice} · {CLASS_LABEL[op_id]}" + ("" if draw_box else " (points)"),
            )
        )

    for slot, (nice, color, box) in enumerate(boxed):
        _exterior_tag(ax, label=nice, color=color, box=box, slot=slot, n_slots=len(boxed))

    _legend_below(ax, legend_handles)
    save(fig, "04_die_hotspots")


def _render_one_group_map(
    *,
    gid: str,
    pts: list,
    bg_pts: list,
    bbox: dict,
    color: str,
    title: str,
    subtitle: str,
    tag: str,
    stem: str,
    subdir: Path,
    legend_label: str | None = None,
) -> None:
    fig, ax = _setup_die_figure(title, subtitle)
    _draw_og_and_bg(ax, bbox, bg_pts)
    _finish_die_axes(ax, bbox, bg_pts)

    if pts:
        xs, ys = zip(*pts)
        ax.scatter(
            xs,
            ys,
            s=28,
            c=color,
            alpha=0.9,
            zorder=5,
            edgecolors="#222",
            linewidths=0.3,
            label=legend_label or gid,
        )
        _draw_cluster_box(ax, pts, color, pad=4.0)
    else:
        ax.text(0.5, 0.5, "No plotted instances", transform=ax.transAxes, ha="center")

    _legend_below(ax)
    save(fig, stem, subdir=subdir)


def _nodes_for_group(gid: str, drivers, stubs) -> set[str]:
    if gid in PER_GROUP_ROOTS:
        return fanin_nodes(PER_GROUP_ROOTS[gid], drivers, stubs)
    if gid in COMBO_PARTS:
        merged: set[str] = set()
        for part in COMBO_PARTS[gid]:
            merged |= fanin_nodes(PER_GROUP_ROOTS[part], drivers, stubs)
        return merged
    return set()


def fig_per_group_die_maps(ranking: list[dict]) -> None:
    by_id = {r["group"]: r for r in ranking}
    drivers, stubs, _meta = parse_structural(STRUCTURAL_V)
    pos = load_positions()
    bbox = load_bbox()
    bg_pts = points_for(fanin_nodes(PER_GROUP_ROOTS["G_success_glue"], drivers, stubs), drivers, pos)

    tech_dir = OUT / "die_maps_technical"
    plain_dir = OUT / "die_maps_plain"
    tech_dir.mkdir(parents=True, exist_ok=True)
    plain_dir.mkdir(parents=True, exist_ok=True)

    index_tech: list[str] = [
        "# Die maps — technical labels",
        "",
        "One map per strong success-cone grouping (score ≥ 0.8), including combo unions.",
        "Uses original group IDs and operator fingerprint names.",
        "",
    ]
    index_plain: list[str] = [
        "# Die maps — plain-language (pre-solve)",
        "",
        "Same groupings as the technical set.",
        "Titles/purposes follow fingerprint class, motifs, and size only — not solve narrative.",
        "",
    ]

    # All ranked G_* / C_* matches at the same threshold as the old XY maps.
    strong = [
        r
        for r in ranking
        if r["score"] >= 0.8 and (r["group"].startswith("G_") or r["group"].startswith("C_"))
    ]
    for r in strong:
        gid = r["group"]
        nodes = _nodes_for_group(gid, drivers, stubs)
        if not nodes and gid not in PER_GROUP_ROOTS and gid not in COMBO_PARTS:
            print(f"skip {gid}: no root/combo definition")
            continue
        op_id = r["best_id"]
        color = CLASS_COLOR.get(op_id, "#c0392b")
        pts = points_for(nodes, drivers, pos)
        stem = re.sub(r"[^\w.\-]+", "_", f"{gid}_{op_id}")

        tech_title = f"{gid} — {r['best_op']}"
        tech_bits = [f"score {r['score']:.3f}", f"n={r['n_nodes']}"]
        if r.get("granular_summary"):
            tech_bits.append(r["granular_summary"][:72])
        tech_subtitle = " · ".join(tech_bits)
        _render_one_group_map(
            gid=gid,
            pts=pts,
            bg_pts=bg_pts,
            bbox=bbox,
            color=color,
            title=tech_title,
            subtitle=tech_subtitle,
            tag=gid,
            stem=stem,
            subdir=tech_dir,
            legend_label=gid,
        )
        index_tech.append(
            f"- `{stem}.png` — **{gid}** → {r['best_op']} (score {r['score']:.3f}, n={r['n_nodes']})"
        )

        plain = PLAIN_GROUP.get(
            gid, {"title": FRIENDLY_GROUP.get(gid, gid), "purpose": r["best_op"]}
        )
        plain_class = PLAIN_CLASS.get(op_id, r["best_op"])
        _render_one_group_map(
            gid=gid,
            pts=pts,
            bg_pts=bg_pts,
            bbox=bbox,
            color=color,
            title=f"{plain['title']}  ·  {plain_class}",
            subtitle=plain["purpose"].replace("\n", " "),
            tag=plain["title"],
            stem=stem,
            subdir=plain_dir,
            legend_label=plain["title"],
        )
        index_plain.append(
            f"- `{stem}.png` — **{plain['title']}** ({plain_class}, score {r['score']:.3f})"
        )

    index_tech.append("")
    index_plain.append("")
    (tech_dir / "README.md").write_text("\n".join(index_tech), encoding="utf-8")
    (plain_dir / "README.md").write_text("\n".join(index_plain), encoding="utf-8")
    print(f"wrote {tech_dir / 'README.md'}")
    print(f"wrote {plain_dir / 'README.md'}")


def write_readme(ranking: list[dict]) -> None:
    top = [r for r in ranking if r["group"].startswith("G_")][:5]
    lines = [
        "# Phase 1 figures",
        "",
        "Writeup figures for the netlist → pattern-match checkpoint.",
        "",
        "| File | Caption |",
        "|------|---------|",
        "| `01_chip_overview` | High-level success path. |",
        "| `02_operator_matches` | Ranked operator fingerprint matches. |",
        "| `03_status_ab` | Status A / B one-cycle SET window. |",
        "| `04_die_hotspots` | Combined die overview of strong matches. |",
        "| `die_maps_technical/` | **One map per grouping** — original IDs / operator names. |",
        "| `die_maps_plain/` | **Same maps** — plain-language circuit purpose. |",
        "",
        "Each stem is written as `.png` (200 dpi) and `.svg`.",
        "",
        "## Top G_* matches (this run)",
        "",
    ]
    for r in top:
        lines.append(
            f"- **{FRIENDLY_GROUP.get(r['group'], r['group'])}** → "
            f"{r['best_op']} (score {r['score']:.3f}, n={r['n_nodes']})"
        )
    lines.append("")
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT / 'README.md'}")


def main() -> None:
    data = json.loads(MATCH_JSON.read_text(encoding="utf-8"))
    ranking = data["ranking"]
    fig_chip_overview()
    fig_operator_matches(ranking)
    fig_status_ab()
    fig_die_hotspots()
    fig_per_group_die_maps(ranking)
    write_readme(ranking)


if __name__ == "__main__":
    main()
