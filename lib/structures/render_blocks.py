#!/usr/bin/env python3
"""Render fan-in with greedy structure matches collapsed to block nodes."""
from __future__ import annotations

import os
from collections import deque
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

from structures.graph import Match, data_deps, short  # noqa: E402
from structural_drivers import PRIMARY, is_clk  # noqa: E402


def _block_id(m: Match) -> str:
    return f"BLK_{m.pattern_id}_{short(m.anchor)}"


def build_block_graph(
    root: str,
    drivers: dict,
    cover: list[Match],
    max_depth: int = 8,
) -> tuple[dict[str, int], list[tuple[str, str, str]], dict[str, Match]]:
    """BFS with member nets collapsed into block supernodes.

    Returns (depth, edges as (src, dst, label), block_by_id).
    """
    member_to_block: dict[str, Match] = {}
    for m in cover:
        for n in m.members:
            # prefer first (greedy already ordered)
            member_to_block.setdefault(n, m)

    blocks = {_block_id(m): m for m in cover}

    def node_for(net: str) -> str:
        if net in member_to_block:
            return _block_id(member_to_block[net])
        return net

    root_n = node_for(root)
    depth: dict[str, int] = {root_n: 0}
    edges: list[tuple[str, str, str]] = []
    seen_e: set[tuple[str, str, str]] = set()
    q: deque[str] = deque([root_n])

    # For each block, external ports are nets not in members (or named ports)
    def expand_ports(nid: str) -> list[tuple[str, str]]:
        """Return (port_label, predecessor_net_or_block) to expand behind nid."""
        if nid in blocks:
            m = blocks[nid]
            out = []
            for pname, pnet in m.ports.items():
                if not pnet or pnet in m.members:
                    continue
                if pname in ("Y", "Q", "mux_X", "feedback_pin") and pnet == m.anchor:
                    continue
                # don't expand through own Q if Q is member
                out.append((pname, pnet))
            return out
        # primitive: data deps
        return [("", d) for d in sorted(data_deps(nid, drivers))]

    while q:
        n = q.popleft()
        d = depth[n]
        if d >= max_depth:
            continue
        for label, pred_net in expand_ports(n):
            if is_clk(pred_net) or pred_net == "rst_n":
                continue
            pred = node_for(pred_net)
            if pred == n:
                continue
            e = (pred, n, label)
            if e not in seen_e:
                seen_e.add(e)
                edges.append(e)
            nd = d + 1
            if pred not in depth or nd < depth[pred]:
                depth[pred] = nd
                if nd < max_depth and (pred in blocks or pred in drivers or pred in PRIMARY):
                    q.append(pred)

    return depth, edges, blocks


def render_block_fanin(
    root: str,
    drivers: dict,
    cover: list[Match],
    out_png: Path,
    *,
    title: str = "",
    max_depth: int = 8,
) -> Path:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    from rework_paths import savefig_locked

    depth, edges, blocks = build_block_graph(root, drivers, cover, max_depth=max_depth)
    if not depth:
        depth = {root: 0}

    # layout: x = depth, y = index within depth
    by_d: dict[int, list[str]] = {}
    for n, d in depth.items():
        by_d.setdefault(d, []).append(n)
    for d in by_d:
        by_d[d].sort()

    pos: dict[str, tuple[float, float]] = {}
    for d, nodes in by_d.items():
        for i, n in enumerate(nodes):
            y = i - (len(nodes) - 1) / 2
            pos[n] = (float(d), float(y))

    max_d = max(depth.values()) if depth else 0
    n_rows = max((len(v) for v in by_d.values()), default=1)
    fig_w = max(8, 1.6 * (max_d + 1) + 2)
    fig_h = max(4, 0.7 * n_rows + 1.5)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=140)
    ax.set_xlim(-0.8, max_d + 1.2)
    ax.set_ylim(-n_rows / 2 - 1, n_rows / 2 + 1)
    ax.axis("off")
    ax.set_title(title or f"block fan-in · {short(root)}", fontsize=11)

    for src, dst, label in edges:
        if src not in pos or dst not in pos:
            continue
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        ax.annotate(
            "",
            xy=(x1 - 0.35, y1),
            xytext=(x0 + 0.35, y0),
            arrowprops=dict(arrowstyle="->", lw=0.7, color="#555"),
        )
        if label:
            ax.text(
                (x0 + x1) / 2,
                (y0 + y1) / 2 + 0.12,
                label,
                fontsize=5,
                color="#666",
                ha="center",
            )

    for n, (x, y) in pos.items():
        if n in blocks:
            m = blocks[n]
            face = "#ddebf7"
            edge = "#1f4e79"
            txt = f"BLOCK\n{m.pattern_id}\n{short(m.anchor)}"
            if m.extra.get("n_stages"):
                txt += f"\nn={m.extra['n_stages']}"
            w, h = 0.9, 0.55
        elif n in PRIMARY:
            face = "#fce4d6"
            edge = "#c00000"
            txt = n
            w, h = 0.5, 0.35
        else:
            info = drivers.get(n) or {}
            face = "#f2f2f2"
            edge = "#666"
            inst = short(info.get("instance") or "")
            txt = f"{inst}\n{short(n)}" if inst else short(n)
            w, h = 0.7, 0.4
        ax.add_patch(
            FancyBboxPatch(
                (x - w / 2, y - h / 2),
                w,
                h,
                boxstyle="round,pad=0.02,rounding_size=0.05",
                facecolor=face,
                edgecolor=edge,
                lw=1.2 if n in blocks else 0.7,
            )
        )
        ax.text(x, y, txt, ha="center", va="center", fontsize=6, family="monospace")

    fig.tight_layout()
    out_png = Path(out_png)
    return savefig_locked(fig, out_png)


def write_block_md(
    result: dict,
    out_md: Path,
    *,
    png_name: str,
    arm_title: str,
) -> None:
    cov = result["greedy_coverage"]
    lines = [
        f"# Block structures — {arm_title}",
        "",
        f"Root: `{result['root']}` · cone **{result['cone_size']}** nets",
        "",
        f"Greedy coverage: **{cov['covered_nets']}** / **{cov['cone_nets']}** "
        f"({cov['frac']:.1%})",
        "",
        f"Figure: [`{png_name}`]({png_name})",
        "",
        "## Greedy cover",
        "",
        "| pattern | anchor | members | ports |",
        "|---------|--------|--------:|-------|",
    ]
    for m in result["greedy_cover"]:
        ports = ", ".join(f"{k}={v}" for k, v in (m.get("ports") or {}).items() if v)[:80]
        lines.append(
            f"| `{m['pattern_id']}` | `{m['anchor']}` | {len(m.get('members') or [])} | {ports} |"
        )
    lines += [
        "",
        f"Raw matches: **{len(result['raw_matches'])}** "
        f"(coverage {result['raw_coverage']['frac']:.1%})",
        "",
        "Uncovered (sample): "
        + (", ".join(f"`{x}`" for x in cov.get("uncovered", [])[:30]) or "—"),
        "",
        "JSON: [`recognized.json`](recognized.json)",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
