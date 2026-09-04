#!/usr/bin/env python3
"""Draw visual logic schematics of fan-in cones from TRUSTED structural Verilog.

Standalone under rework/:
  rework/netlist/puzzle_gates.spice
    → rework/tools/spice_to_structural_verilog.py
    → rework/netlist/puzzle_structural.v
    → rework/tools/structural_drivers.py

Does NOT read puzzle_core.v, puzzle_success_cone.v (core-derived), or stub_og cones.

Features:
  - Bounded-depth BFS back from a root net
  - Behind-tracer: count nodes / gates / leaf terminals in the full fan-in
  - AO/OA pin-labeled edges + formula on compound cells
  - Depth-cut tags: deeper fan-in reaches FA endpoint and/or primary I
  - Bundle mode: depth-2 overview from success + depth-4 map per visible net

Usage:
  python3 tools/identify_fa_endpoints.py   # once / when netlist changes
  python3 tools/render_success_logic_depth.py --bundle
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

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
if str(ROOT / "phase2") not in sys.path:
    sys.path.insert(0, str(ROOT / "phase2"))

from structural_drivers import (  # noqa: E402
    PRIMARY,
    STRUCTURAL_V,
    is_clk,
    parse_structural,
    write_provenance,
)
from ao_oa_labels import (  # noqa: E402
    ao_oa_formula,
    pin_edge_style,
    pins_for_net,
)
from identify_fa_endpoints import (  # noqa: E402
    build_report,
    endpoint_sets,
    fanin_hits,
    find_fa_pairs,
)

# short() for net display — strip sky130 prefix
def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


OUT_DIR = HERE  # phase2/success/
GATE_REF = ROOT / "phase2" / "gate_types.md"
PROVENANCE = ROOT / "phase2" / "PROVENANCE.md"
FA_JSON = ROOT / "phase2" / "fa_endpoints.json"

CLASS_COLOR = {
    "flop": "#1f4e79",
    "and": "#c45911",
    "nand": "#c45911",
    "or": "#548235",
    "nor": "#548235",
    "xor": "#7030a0",
    "xnor": "#7030a0",
    "aoi": "#2e75b6",
    "mux": "#bf8f00",
    "inv": "#7f7f7f",
    "buf": "#7f7f7f",
    "leaf": "#833c0c",
    "primary": "#c00000",
    "stub": "#595959",
    "?": "#444444",
}

REACH_FA = "#1f4e79"
REACH_I = "#c00000"


def _data_deps(name: str, drivers: dict) -> set[str]:
    info = drivers.get(name)
    if not info:
        return set()
    return {d for d in info["deps"] if not is_clk(d) and d != "rst_n"}


def fanin_bounded(
    root: str,
    drivers: dict,
    stubs: set[str],
    max_depth: int,
) -> tuple[dict[str, int], list[tuple[str, str]], set[str]]:
    """BFS back from root. depth[root]=0; stop expanding past max_depth."""
    depth: dict[str, int] = {root: 0}
    edges: list[tuple[str, str]] = []
    q: deque[str] = deque([root])
    seen_edge: set[tuple[str, str]] = set()
    frontier: set[str] = set()

    while q:
        n = q.popleft()
        d = depth[n]
        if d >= max_depth:
            if n in drivers and _data_deps(n, drivers):
                frontier.add(n)
            continue
        if n not in drivers:
            continue
        for dep in sorted(_data_deps(n, drivers)):
            e = (dep, n)
            if e not in seen_edge:
                seen_edge.add(e)
                edges.append(e)
            nd = d + 1
            if dep not in depth or nd < depth[dep]:
                depth[dep] = nd
                if dep in drivers and nd < max_depth:
                    q.append(dep)
                elif dep in drivers and nd == max_depth:
                    depth[dep] = nd
                    frontier.add(dep)
                else:
                    depth[dep] = nd
            elif dep not in drivers:
                depth.setdefault(dep, nd)

    return depth, edges, frontier


def count_behind(root: str, drivers: dict, stubs: set[str]) -> dict:
    """Full fan-in tracer: everything that can affect `root` (excluding root)."""
    if root not in drivers and root not in PRIMARY and root not in stubs:
        return {
            "nodes": 0,
            "gates": 0,
            "flops": 0,
            "leaves": 0,
            "primaries": 0,
            "stubs": 0,
            "by_class": {},
            "node_set": set(),
            "leaf_set": set(),
        }

    nodes: set[str] = set()
    leaves: set[str] = set()
    q: deque[str] = deque([root])
    seen: set[str] = set()
    while q:
        n = q.popleft()
        if n in seen:
            continue
        seen.add(n)
        if n == root:
            for d in _data_deps(n, drivers) if n in drivers else []:
                q.append(d)
            continue
        if n in drivers:
            nodes.add(n)
            for d in _data_deps(n, drivers):
                if d not in seen:
                    q.append(d)
        else:
            leaves.add(n)

    by_class = Counter(drivers[n].get("class", "?") for n in nodes)
    flops = sum(1 for n in nodes if drivers[n].get("kind") == "flop")
    primaries = sorted(x for x in leaves if x in PRIMARY)
    other_leaves = sorted(x for x in leaves if x not in PRIMARY)
    return {
        "nodes": len(nodes),
        "gates": len(nodes),
        "flops": flops,
        "leaves": len(leaves),
        "primaries": len(primaries),
        "stubs": 0,
        "undriven": len(other_leaves),
        "by_class": dict(by_class),
        "node_set": nodes,
        "leaf_set": leaves,
        "primary_names": primaries,
        "stub_names": [],
        "undriven_names": other_leaves,
    }


def load_fa_endpoints(drivers: dict) -> dict[str, set[str]]:
    """Build FA endpoint sets; refresh JSON artifact."""
    pairs = find_fa_pairs(drivers)
    ends = endpoint_sets(pairs)
    report = build_report(drivers)
    FA_JSON.parent.mkdir(parents=True, exist_ok=True)
    FA_JSON.write_text(
        __import__("json").dumps(report, indent=2),
        encoding="utf-8",
    )
    md = ROOT / "phase2" / "fa_endpoints.md"
    from identify_fa_endpoints import write_md

    write_md(report)
    print(f"FA endpoints: {len(ends['fa_any'])} nets ({len(pairs)} pairs) → {FA_JSON.name}")
    return ends


def reach_tags(
    name: str,
    drivers: dict,
    fa_any: set[str],
) -> dict:
    """What deeper fan-in of this net eventually reaches (FA endpoint / I)."""
    hits_fa = fanin_hits(name, drivers, fa_any, include_root=True)
    hits_i = fanin_hits(name, drivers, {"I"}, include_root=True)
    is_fa = name in fa_any
    is_i = name == "I"
    return {
        "reaches_fa": bool(hits_fa),
        "reaches_i": bool(hits_i),
        "is_fa": is_fa,
        "is_i": is_i,
        "fa_hits": sorted(short(x) for x in hits_fa)[:8],
        "fa_hit_count": len(hits_fa),
    }


def _node_kind(name: str, drivers: dict, stubs: set[str]) -> str:
    if name in PRIMARY:
        return "primary"
    if name in stubs or name.startswith("stub_og"):
        return "stub"
    if name not in drivers:
        return "leaf"
    return drivers[name].get("class") or "?"


def _label(
    name: str,
    drivers: dict,
    stubs: set[str],
    behind: dict | None = None,
    reach: dict | None = None,
    *,
    truncated: bool = False,
) -> str:
    formula = None
    if name in PRIMARY:
        base = name
    elif name in stubs or name.startswith("stub_og"):
        base = short(name)
    elif name not in drivers:
        base = short(name)
    else:
        info = drivers[name]
        cell = info.get("cell") or "?"
        cell_s = re.sub(r"_2$", "", cell) if isinstance(cell, str) else "?"
        net = short(name)
        if info.get("kind") == "flop":
            base = f"FF\n{net}"
        else:
            formula = ao_oa_formula(cell) if info.get("class") == "aoi" else None
            if formula:
                # Keep formula short on the box
                base = f"{cell_s}\n{formula}\n{net}"
            else:
                base = f"{cell_s}\n{net}"

    parts = [base]
    if behind is not None:
        parts.append(f"↓ {behind['nodes']}n · {behind['flops']}ff · {behind['leaves']}L")

    if truncated and reach is not None:
        tags = []
        if reach["is_fa"]:
            tags.append("FA★")
        elif reach["reaches_fa"]:
            tags.append(f"→FA×{reach['fa_hit_count']}")
        if reach["is_i"]:
            tags.append("I★")
        elif reach["reaches_i"]:
            tags.append("→I")
        if tags:
            parts.append(" ".join(tags))
        elif name in drivers and _data_deps(name, drivers):
            parts.append("cut")

    return "\n".join(parts)


X_PITCH = 4.4
Y_PITCH = 2.2
BACK_EDGE_COLOR = "#b00020"


def _dst_pins(src: str, dst: str, drivers: dict) -> list[str]:
    info = drivers.get(dst)
    if not info:
        return []
    return pins_for_net(info.get("in_pins") or {}, src)


def _edge_kind(src: str, dst: str, depth: dict[str, int]) -> str:
    """forward = deeper→shallower (left→right); back = right→left; same = within layer."""
    ds, dd = depth.get(src, -1), depth.get(dst, -1)
    if ds > dd:
        return "forward"
    if ds < dd:
        return "back"
    return "same"


def _pin_rank(pin: str) -> tuple:
    m = re.match(r"^([A-Za-z]+?)(\d*)(_N)?$", pin)
    if not m:
        return (99, 99, pin)
    letter, num, neg = m.group(1), m.group(2), m.group(3)
    return (letter, int(num) if num else 0, 1 if neg else 0)


def _dep_order_key(dep: str, consumer: str, drivers: dict) -> tuple:
    pins = _dst_pins(dep, consumer, drivers)
    if pins:
        return (min(_pin_rank(p) for p in pins), dep)
    return ((99, 99, 0), dep)


def _seed_layer_order(
    root: str,
    depth: dict[str, int],
    edges: list[tuple[str, str]],
    drivers: dict,
    max_depth: int,
) -> dict[int, list[str]]:
    """Order each layer by walking from the root, sorting deps by destination pin."""
    fwd_children: dict[str, list[str]] = defaultdict(list)
    for src, dst in edges:
        if _edge_kind(src, dst, depth) == "forward":
            fwd_children[dst].append(src)

    by_layer: dict[int, list[str]] = {d: [] for d in range(max_depth + 1)}
    seen: set[str] = set()
    if root in depth:
        by_layer[0].append(root)
        seen.add(root)

    for d in range(max_depth):
        for parent in by_layer[d]:
            kids = sorted(
                fwd_children.get(parent, []),
                key=lambda k: _dep_order_key(k, parent, drivers),
            )
            for k in kids:
                if k in seen:
                    continue
                if depth.get(k) == d + 1:
                    by_layer[d + 1].append(k)
                    seen.add(k)
        for n in sorted(x for x, dd in depth.items() if dd == d + 1 and x not in seen):
            by_layer[d + 1].append(n)
            seen.add(n)

    for n, dd in depth.items():
        if n not in seen:
            by_layer.setdefault(dd, []).append(n)
    return by_layer


def _barycenter(node: str, neighbors: list[str], index_of: dict[str, int]) -> float:
    idxs = [index_of[n] for n in neighbors if n in index_of]
    if not idxs:
        return float(index_of.get(node, 0))
    return sum(idxs) / len(idxs)


def _reduce_crossings(
    by_layer: dict[int, list[str]],
    depth: dict[str, int],
    edges: list[tuple[str, str]],
    drivers: dict,
    max_depth: int,
    passes: int = 4,
) -> dict[int, list[str]]:
    """Barycentric sweeps, then parent-block + pin order (circuit-friendly)."""
    fwd = [(s, d) for s, d in edges if _edge_kind(s, d, depth) == "forward"]
    for _ in range(passes):
        for d in range(1, max_depth + 1):
            if not by_layer.get(d) or not by_layer.get(d - 1):
                continue
            parent_idx = {n: i for i, n in enumerate(by_layer[d - 1])}
            neigh: dict[str, list[str]] = defaultdict(list)
            for s, dst in fwd:
                if depth.get(s) == d and depth.get(dst) == d - 1:
                    neigh[s].append(dst)
            by_layer[d].sort(
                key=lambda n: (_barycenter(n, neigh[n], parent_idx), n)
            )
        for d in range(max_depth - 1, -1, -1):
            if not by_layer.get(d) or not by_layer.get(d + 1):
                continue
            child_idx = {n: i for i, n in enumerate(by_layer[d + 1])}
            neigh = defaultdict(list)
            for s, dst in fwd:
                if depth.get(s) == d + 1 and depth.get(dst) == d:
                    neigh[dst].append(s)
            by_layer[d].sort(
                key=lambda n: (_barycenter(n, neigh[n], child_idx), n)
            )

    # Final pass: cluster each layer by primary shallower parent, pin order within cluster
    for d in range(1, max_depth + 1):
        if not by_layer.get(d) or not by_layer.get(d - 1):
            continue
        parent_idx = {n: i for i, n in enumerate(by_layer[d - 1])}
        node_pars: dict[str, list[str]] = defaultdict(list)
        for s, dst in fwd:
            if depth.get(s) == d and depth.get(dst) == d - 1:
                node_pars[s].append(dst)

        def block_key(n: str) -> tuple:
            pars = node_pars.get(n, [])
            if not pars:
                return (10_000, (99, 99, 0), n)
            p = min(pars, key=lambda x: parent_idx.get(x, 10_000))
            return (parent_idx[p], _dep_order_key(n, p, drivers)[0], n)

        by_layer[d].sort(key=block_key)
    return by_layer


def layout_layers(
    depth: dict[str, int],
    max_depth: int,
    *,
    root: str,
    edges: list[tuple[str, str]],
    drivers: dict,
) -> dict[str, tuple[float, float]]:
    by_layer = _seed_layer_order(root, depth, edges, drivers, max_depth)
    by_layer = _reduce_crossings(by_layer, depth, edges, drivers, max_depth)

    fwd = [(s, d) for s, d in edges if _edge_kind(s, d, depth) == "forward"]
    pos: dict[str, tuple[float, float]] = {}
    for d, names in by_layer.items():
        x = (max_depth - d) * X_PITCH
        if d == 0 or not by_layer.get(d - 1):
            n = len(names)
            for i, name in enumerate(names):
                y = (i - (n - 1) / 2.0) * Y_PITCH
                pos[name] = (x, y)
            continue

        # Vertical gaps between parent clusters
        parent_idx = {n: i for i, n in enumerate(by_layer[d - 1])}
        node_pars: dict[str, list[str]] = defaultdict(list)
        for s, dst in fwd:
            if depth.get(s) == d and depth.get(dst) == d - 1:
                node_pars[s].append(dst)

        def primary_parent(n: str) -> int:
            pars = node_pars.get(n, [])
            if not pars:
                return -1
            return parent_idx[min(pars, key=lambda p: parent_idx.get(p, 10_000))]

        slots: list[float] = []
        y_cursor = 0.0
        prev_p = None
        for name in names:
            p = primary_parent(name)
            if prev_p is not None and p != prev_p:
                y_cursor += 0.55  # gap between clusters
            slots.append(y_cursor)
            y_cursor += 1.0
            prev_p = p
        mid = (slots[0] + slots[-1]) / 2.0 if slots else 0.0
        for name, slot in zip(names, slots):
            pos[name] = (x, (slot - mid) * Y_PITCH)
    return pos


def render(
    depth: dict[str, int],
    edges: list[tuple[str, str]],
    frontier: set[str],
    drivers: dict,
    stubs: set[str],
    max_depth: int,
    out: Path,
    *,
    root: str,
    behind_map: dict[str, dict] | None = None,
    reach_map: dict[str, dict] | None = None,
    title: str | None = None,
    subtitle: str | None = None,
) -> None:
    pos = layout_layers(depth, max_depth, root=root, edges=edges, drivers=drivers)
    if not pos:
        raise SystemExit("empty cone")

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    pad_x, pad_y = 2.8, 3.0
    fig_w = max(12.0, (max(xs) - min(xs)) * 0.55 + 4.5)
    fig_h = max(8.5, (max(ys) - min(ys)) * 0.55 + 4.5)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_facecolor("#fafafa")
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y + 0.6)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    ax.set_title(
        title or f"Logic fan-in from {short(root)}  ·  max depth {max_depth}",
        fontsize=13,
        fontweight="bold",
        pad=22,
    )
    ax.text(
        0.5,
        1.035,
        subtitle
        or (
            "Left = deeper · Right = root"
            "  ·  solid = forward  ·  dashed ↩ = back-edge"
            "  ·  AO/OA pin colors  ·  cut tags →FA / →I"
        ),
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#444",
    )

    classified = [(src, dst, _edge_kind(src, dst, depth)) for src, dst in edges]
    draw_order = (
        [(s, d, k) for s, d, k in classified if k == "forward"]
        + [(s, d, k) for s, d, k in classified if k == "same"]
        + [(s, d, k) for s, d, k in classified if k == "back"]
    )

    back_i = 0
    for src, dst, ekind in draw_order:
        if src not in pos or dst not in pos:
            continue
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        pins = _dst_pins(src, dst, drivers)
        dst_cls = drivers.get(dst, {}).get("class")
        pin_label = "+".join(pins) if pins else ""

        if ekind == "back":
            rad = 0.35 + 0.08 * (back_i % 3)
            if back_i % 2:
                rad = -rad
            back_i += 1
            label = f"↩ {pin_label}" if pin_label else "↩ back"
            ax.add_patch(
                FancyArrowPatch(
                    (x0 - 0.15, y0),
                    (x1 + 0.15, y1),
                    arrowstyle="-|>",
                    mutation_scale=11,
                    lw=1.8,
                    color=BACK_EDGE_COLOR,
                    alpha=0.95,
                    linestyle=(0, (5, 3)),
                    connectionstyle=f"arc3,rad={rad}",
                    zorder=2,
                )
            )
            mx = (x0 + x1) / 2.0
            my = (y0 + y1) / 2.0 + (1.15 if rad > 0 else -1.15)
            ax.text(
                mx,
                my,
                label,
                ha="center",
                va="center",
                fontsize=7.5,
                color=BACK_EDGE_COLOR,
                fontweight="bold",
                zorder=5,
                bbox=dict(
                    boxstyle="round,pad=0.18",
                    facecolor="#fff0f0",
                    edgecolor=BACK_EDGE_COLOR,
                    lw=0.8,
                    alpha=0.95,
                ),
            )
            continue

        if ekind == "same":
            rad = 0.4 if y0 <= y1 else -0.4
            ax.add_patch(
                FancyArrowPatch(
                    (x0, y0 + 0.55),
                    (x1, y1 + 0.55),
                    arrowstyle="-|>",
                    mutation_scale=9,
                    lw=1.1,
                    color="#666",
                    alpha=0.75,
                    linestyle=(0, (2, 2)),
                    connectionstyle=f"arc3,rad={rad}",
                    zorder=1,
                )
            )
            if pin_label and dst_cls == "aoi":
                ax.text(
                    (x0 + x1) / 2,
                    max(y0, y1) + 1.0,
                    pin_label,
                    ha="center",
                    fontsize=6.5,
                    color="#666",
                    fontweight="bold",
                    zorder=2,
                )
            continue

        # Forward: deeper → shallower (left → right)
        if dst_cls == "aoi" and pins:
            label, color = pin_edge_style(pins)
            lw = 1.35
        else:
            label, color = (pin_label, "#777")
            lw = 0.95
        ax.add_patch(
            FancyArrowPatch(
                (x0 + 1.15, y0),
                (x1 - 1.15, y1),
                arrowstyle="-|>",
                mutation_scale=9,
                lw=lw,
                color=color,
                alpha=0.85,
                zorder=1,
            )
        )
        if label and dst_cls == "aoi":
            mx = (x0 + x1) / 2.0
            my = (y0 + y1) / 2.0
            dy = 0.22 if abs(y1 - y0) < 0.05 else 0.12
            ax.text(
                mx,
                my + dy,
                label,
                ha="center",
                va="bottom",
                fontsize=6.5,
                color=color,
                fontweight="bold",
                zorder=2,
                bbox=dict(
                    boxstyle="round,pad=0.12",
                    facecolor="white",
                    edgecolor="none",
                    alpha=0.85,
                ),
            )

    for name, (x, y) in pos.items():
        kind = _node_kind(name, drivers, stubs)
        color = CLASS_COLOR.get(kind, CLASS_COLOR["?"])
        truncated = name in frontier
        reach = reach_map.get(name) if reach_map else None
        is_aoi = kind == "aoi"
        box_w = 2.45 if is_aoi else 2.2
        box_h = 1.7 if (is_aoi or (behind_map and truncated)) else (1.4 if behind_map else 1.1)
        if truncated and reach and (reach.get("reaches_fa") or reach.get("reaches_i")):
            face = "#e8f0ff" if reach.get("reaches_fa") and not reach.get("reaches_i") else (
                "#ffe8e8" if reach.get("reaches_i") and not reach.get("reaches_fa") else "#f3e8ff"
            )
        else:
            face = "#fff8e7" if truncated else "white"
        ax.add_patch(
            FancyBboxPatch(
                (x - box_w / 2, y - box_h / 2),
                box_w,
                box_h,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=face,
                edgecolor=color,
                lw=1.7 if name == root else 1.2,
                zorder=3,
            )
        )
        bh = behind_map.get(name) if behind_map else None
        ax.text(
            x,
            y,
            _label(name, drivers, stubs, bh, reach, truncated=truncated),
            ha="center",
            va="center",
            fontsize=6.6 if is_aoi else 7.0,
            color="#222",
            linespacing=1.08,
            zorder=4,
            fontweight="bold" if name == root else "normal",
        )

    for d in range(max_depth + 1):
        x = (max_depth - d) * X_PITCH
        ax.text(
            x,
            max(ys) + 1.7,
            f"d={d}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#888",
        )

    from matplotlib.lines import Line2D

    handles = [
        mpatches.Patch(facecolor="white", edgecolor=CLASS_COLOR["flop"], label="flop"),
        mpatches.Patch(facecolor="white", edgecolor=CLASS_COLOR["and"], label="AND/NAND"),
        mpatches.Patch(facecolor="white", edgecolor=CLASS_COLOR["or"], label="OR/NOR"),
        mpatches.Patch(facecolor="white", edgecolor=CLASS_COLOR["xor"], label="XOR/XNOR"),
        mpatches.Patch(facecolor="white", edgecolor=CLASS_COLOR["aoi"], label="AO/OA"),
        mpatches.Patch(facecolor="white", edgecolor=CLASS_COLOR["primary"], label="primary"),
        Line2D([0], [0], color="#777", lw=1.2, label="forward edge"),
        Line2D(
            [0],
            [0],
            color=BACK_EDGE_COLOR,
            lw=1.8,
            linestyle="--",
            label="↩ back-edge",
        ),
        mpatches.Patch(facecolor="#e8f0ff", edgecolor=REACH_FA, label="cut → FA"),
        mpatches.Patch(facecolor="#ffe8e8", edgecolor=REACH_I, label="cut → I"),
    ]
    ax.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.10),
        ncol=5,
        frameon=False,
        fontsize=8,
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.45, facecolor="white")
    fig.savefig(out.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.45, facecolor="white")
    plt.close(fig)
    n_back = sum(1 for s, d in edges if _edge_kind(s, d, depth) == "back")
    print(
        f"wrote {out}  (nodes={len(depth)} edges={len(edges)} "
        f"cuts={len(frontier)} back-edges={n_back})"
    )

def _stem(name: str) -> str:
    return re.sub(r"[^\w.\-]+", "_", short(name))


def write_summary(
    path: Path,
    root: str,
    depth: dict[str, int],
    edges: list[tuple[str, str]],
    frontier: set[str],
    behind_map: dict[str, dict] | None,
    reach_map: dict[str, dict] | None = None,
) -> None:
    lines = [
        f"# Fan-in from `{short(root)}`",
        "",
        f"- Root: `{root}`",
        f"- Visible nodes: **{len(depth)}**",
        f"- Edges: **{len(edges)}**",
        f"- Truncated at depth cut: **{len(frontier)}**",
        "",
    ]
    if reach_map and frontier:
        lines += [
            "## Depth-cut reachability (deeper fan-in)",
            "",
            "| Net | →FA | →I | FA hits (sample) |",
            "|-----|:--:|:--:|------------------|",
        ]
        for n in sorted(frontier, key=lambda x: (depth.get(x, 99), x)):
            r = reach_map.get(n) or {}
            fa = "yes" if r.get("reaches_fa") else ""
            ii = "yes" if r.get("reaches_i") else ""
            sample = ", ".join(f"`{x}`" for x in (r.get("fa_hits") or [])[:4])
            if (r.get("fa_hit_count") or 0) > 4:
                sample += ", …"
            lines.append(f"| `{short(n)}` | {fa} | {ii} | {sample} |")
        lines.append("")
    if behind_map:
        lines += ["## Behind counts (full fan-in under each visible net)", ""]
        lines.append("| Net | depth | nodes behind | flops | leaves | primaries | undriven |")
        lines.append("|-----|------:|-------------:|------:|-------:|----------:|---------:|")
        for n in sorted(depth, key=lambda x: (depth[x], x)):
            b = behind_map[n]
            lines.append(
                f"| `{short(n)}` | {depth[n]} | {b['nodes']} | {b['flops']} | "
                f"{b['leaves']} | {b['primaries']} | {b.get('undriven', 0)} |"
            )
        lines.append("")
    lines += ["## Nodes by depth", ""]
    by = defaultdict(list)
    for n, d in depth.items():
        by[d].append(short(n))
    for d in sorted(by):
        lines.append(f"- **d={d}** ({len(by[d])}): " + ", ".join(f"`{x}`" for x in by[d]))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}")


def render_one(
    root: str,
    drivers: dict,
    stubs: set[str],
    max_depth: int,
    out: Path,
    *,
    with_behind: bool,
    fa_ends: dict[str, set[str]],
    title: str | None = None,
) -> dict[str, dict]:
    depth, edges, frontier = fanin_bounded(root, drivers, stubs, max_depth)
    behind_map = None
    if with_behind:
        behind_map = {n: count_behind(n, drivers, stubs) for n in depth}
    reach_map = {n: reach_tags(n, drivers, fa_ends["fa_any"]) for n in frontier}
    # Also tag visible FA endpoints / I even if not truncated
    for n in depth:
        if n in fa_ends["fa_any"] or n == "I":
            reach_map.setdefault(n, reach_tags(n, drivers, fa_ends["fa_any"]))
    render(
        depth,
        edges,
        frontier,
        drivers,
        stubs,
        max_depth,
        out,
        root=root,
        behind_map=behind_map,
        reach_map=reach_map,
        title=title,
    )
    write_summary(out.with_suffix(".md"), root, depth, edges, frontier, behind_map, reach_map)
    return behind_map or {}


def run_bundle(drivers: dict, stubs: set[str], fa_ends: dict[str, set[str]]) -> None:
    """Depth-2 overview from success + depth-4 map per visible net."""
    overview_dir = OUT_DIR
    per_dir = OUT_DIR / "fanin_depth4_from_depth2"
    per_dir.mkdir(parents=True, exist_ok=True)

    depth2, edges2, frontier2 = fanin_bounded("success", drivers, stubs, 2)
    behind_map = {n: count_behind(n, drivers, stubs) for n in depth2}
    reach_map = {n: reach_tags(n, drivers, fa_ends["fa_any"]) for n in frontier2}
    for n in depth2:
        if n in fa_ends["fa_any"] or n == "I":
            reach_map.setdefault(n, reach_tags(n, drivers, fa_ends["fa_any"]))

    overview = overview_dir / "success_fanin_depth2.png"
    render(
        depth2,
        edges2,
        frontier2,
        drivers,
        stubs,
        2,
        overview,
        root="success",
        behind_map=behind_map,
        reach_map=reach_map,
        title="Logic fan-in from success  ·  max depth 2  (with behind counts)",
    )
    write_summary(
        overview.with_suffix(".md"), "success", depth2, edges2, frontier2, behind_map, reach_map
    )

    index = [
        "# Depth-4 fan-in maps for each depth-2 success net",
        "",
        "Source cone: `rework/netlist/puzzle_structural.v` (from trusted `puzzle_gates.spice`).",
        "",
        "Parent overview: [`success_fanin_depth2.png`](../success_fanin_depth2.png)",
        "",
        "FA endpoints: [`../fa_endpoints.md`](../fa_endpoints.md)",
        "",
        "Provenance: [`../PROVENANCE.md`](../PROVENANCE.md) · Gate reference: [`../gate_types.md`](../gate_types.md)",
        "",
        "Depth-cut boxes tinted when deeper fan-in reaches an FA endpoint (`→FA`) and/or primary `I` (`→I`).",
        "AO/OA edges are colored/labeled by pin group (A / B / C / D).",
        "Layer order is pin-aware + barycentric (fewer crossings). Dashed crimson **↩** arcs are back-edges.",
        "",
        "| Net | d from success | nodes behind | flops | leaves | figure |",
        "|-----|---------------:|-------------:|------:|-------:|--------|",
    ]
    ordered = sorted(depth2.keys(), key=lambda n: (depth2[n], n))
    for n in ordered:
        b = behind_map[n]
        stem = f"d{depth2[n]}_{_stem(n)}_depth4"
        out = per_dir / f"{stem}.png"
        title = (
            f"Fan-in from {short(n)}  ·  depth ≤ 4"
            f"  (appears at d={depth2[n]} on success overview)"
        )
        render_one(n, drivers, stubs, 4, out, with_behind=True, fa_ends=fa_ends, title=title)
        index.append(
            f"| `{short(n)}` | {depth2[n]} | {b['nodes']} | {b['flops']} | {b['leaves']} | "
            f"[`{stem}.png`]({stem}.png) |"
        )
    index.append("")
    (per_dir / "README.md").write_text("\n".join(index), encoding="utf-8")
    print(f"wrote {per_dir / 'README.md'}")
    print(f"bundle done: overview + {len(ordered)} depth-4 maps")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=2, help="max gate hops back from root")
    ap.add_argument("--root", default="success", help="start net (default: success)")
    ap.add_argument("--behind-counts", action="store_true", help="label full fan-in behind each net")
    ap.add_argument(
        "--bundle",
        action="store_true",
        help="depth-2 success overview + depth-4 map for each visible net",
    )
    ap.add_argument("--out", type=Path, default=None, help="output PNG (SVG alongside)")
    args = ap.parse_args()

    drivers, stubs, meta = parse_structural(STRUCTURAL_V)
    write_provenance(PROVENANCE, meta)
    print(f"structural drivers: {meta}")
    if "success" not in drivers:
        raise SystemExit("success not found in structural drivers — wrong netlist?")

    fa_ends = load_fa_endpoints(drivers)

    if args.bundle:
        run_bundle(drivers, stubs, fa_ends)
        return

    if args.root not in drivers and args.root not in PRIMARY:
        raise SystemExit(f"root net not found in structural drivers: {args.root}")

    out = args.out or (OUT_DIR / f"{_stem(args.root)}_fanin_depth{args.depth}.png")
    if args.root == "success" and args.out is None:
        out = OUT_DIR / f"success_fanin_depth{args.depth}.png"
    render_one(
        args.root,
        drivers,
        stubs,
        args.depth,
        out,
        with_behind=args.behind_counts,
        fa_ends=fa_ends,
    )


if __name__ == "__main__":
    main()
