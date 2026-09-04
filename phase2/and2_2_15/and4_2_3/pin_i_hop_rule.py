#!/usr/bin/env python3
"""Pin eligibility: only nets within 1 hop of an I-reaching node.

Rule
----
Do **not** watch pins that sit more than one node back from something
that traces to primary ``I``.

Equivalently: if net N itself does **not** reach I, then the cell it
**feeds into** (its fan-out parent toward the expand root) **must**
reach I. So non-I stubs are allowed only as *immediate* inputs of an
I-reaching gate — never deeper.

Usage:
  from pin_i_hop_rule import allowed_watch_nets, classify_net
"""
from __future__ import annotations

from collections import deque


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def is_clkish(n: str) -> bool:
    s = short(n).lower()
    return (
        n in ("clk", "rst_n")
        or s.endswith("__clk")
        or "clkbuf" in s
        or s == "rst_n"
        or "reset" in s
    )


def classify_net(
    net: str,
    parent: str | None,
    drivers: dict,
    stubs: set[str],
    reaches_I,
) -> dict:
    """Return eligibility record for net with optional fan-in parent (toward root)."""
    hit_i = net == "I" or reaches_I(net, drivers, stubs)
    parent_i = False
    if parent is not None:
        parent_i = parent == "I" or reaches_I(parent, drivers, stubs)
    # Allowed: reaches I, OR (does not reach I but feeds an I-reaching parent)
    if hit_i:
        ok = True
        why = "reaches_I"
    elif parent is not None and parent_i:
        ok = True
        why = "feeds_I_parent"  # 1 hop back from I-tracing node
    else:
        ok = False
        why = "deeper_non_I" if parent is not None else "no_I_no_parent"
    return {
        "net": short(net),
        "net_full": net,
        "reaches_I": hit_i,
        "parent": None if parent is None else short(parent),
        "parent_reaches_I": parent_i,
        "allowed": ok,
        "why": why,
    }


def fanin_parents(
    root: str,
    drivers: dict,
    max_depth: int = 5,
) -> dict[str, str | None]:
    """Map net → parent toward root (None for root). BFS fan-in."""
    parent: dict[str, str | None] = {root: None}
    depth = {root: 0}
    q = deque([root])
    while q:
        n = q.popleft()
        d = depth[n]
        if d >= max_depth:
            continue
        info = drivers.get(n)
        if not info:
            continue
        for dep in info.get("deps") or set():
            if is_clkish(dep):
                continue
            # skip constants
            if dep.startswith("1'b"):
                continue
            if dep not in parent:
                parent[dep] = n
                depth[dep] = d + 1
                q.append(dep)
    return parent


def allowed_watch_nets(
    root: str,
    drivers: dict,
    stubs: set[str],
    reaches_I,
    max_depth: int = 5,
) -> list[dict]:
    """List fan-in nets from root that pass the 1-hop-to-I pin rule."""
    parents = fanin_parents(root, drivers, max_depth=max_depth)
    rows = []
    for net, par in parents.items():
        if is_clkish(net):
            continue
        rows.append(classify_net(net, par, drivers, stubs, reaches_I))
    # stable: allowed first, then by name
    rows.sort(key=lambda r: (not r["allowed"], r["net"]))
    return rows
