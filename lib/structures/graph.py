#!/usr/bin/env python3
"""Graph helpers for structure matching on structural drivers."""
from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any

from structural_drivers import PRIMARY, is_clk


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


@dataclass
class Check:
    rule: str
    ok: bool
    detail: str = ""


@dataclass
class Match:
    pattern_id: str
    anchor: str
    ports: dict[str, str] = field(default_factory=dict)
    members: set[str] = field(default_factory=set)
    checks: list[Check] = field(default_factory=list)
    ok: bool = True
    extra: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict:
        d = {
            "pattern_id": self.pattern_id,
            "anchor": short(self.anchor),
            "anchor_full": self.anchor,
            "ports": {k: short(v) for k, v in self.ports.items()},
            "ports_full": dict(self.ports),
            "members": sorted(short(m) for m in self.members),
            "members_full": sorted(self.members),
            "ok": self.ok,
            "checks": [asdict(c) for c in self.checks],
            "extra": self.extra,
        }
        return d


def data_deps(name: str, drivers: dict) -> set[str]:
    info = drivers.get(name)
    if not info:
        return set()
    return {d for d in info["deps"] if not is_clk(d) and d != "rst_n"}


def fanin_cone(root: str, drivers: dict) -> set[str]:
    seen: set[str] = {root}
    q = deque([root])
    while q:
        n = q.popleft()
        for d in data_deps(n, drivers):
            if d not in seen:
                seen.add(d)
                if d in drivers:
                    q.append(d)
    return seen


def find_flop_driven_by(drivers: dict, d_net: str) -> tuple[str, dict] | None:
    for net, info in drivers.items():
        if info.get("class") != "flop":
            continue
        if info["in_pins"].get("D") == d_net:
            return net, info
    return None


def consumers_of(drivers: dict, net: str) -> list[tuple[str, dict]]:
    out = []
    for n, info in drivers.items():
        if net in (info.get("deps") or set()):
            out.append((n, info))
    return out


def cell_family(info: dict) -> str:
    c = (info.get("cell") or "").lower()
    for fam in (
        "a31o",
        "a32o",
        "a221o",
        "a22o",
        "a21o",
        "and2b",
        "and4bb",
        "and4b",
        "nand4",
        "nand3",
        "nand2",
        "and4",
        "and3",
        "and2",
        "mux2",
        "inv",
        "dfrtp",
        "nor4",
        "nor3",
        "nor2",
        "or4",
        "or3",
        "or2",
    ):
        if fam in c:
            return fam
    return info.get("class") or "?"
