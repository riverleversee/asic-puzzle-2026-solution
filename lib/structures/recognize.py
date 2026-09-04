#!/usr/bin/env python3
"""Run catalog matchers; filter to cone; greedy non-overlapping cover."""
from __future__ import annotations

from structures.catalog import PATTERNS, match_fa_prior_stub_driver
from structures.graph import Match, fanin_cone, short

# Prefer larger / composed patterns first when greedily covering.
GREEDY_PRIORITY = {
    "enabled_mux_shift_register": 100,
    "sticky_ao_latch": 90,
    "andN_flopped_inputs": 80,
    "mux_hold_flop_stage": 50,
    "and2b_enable_gate": 40,
    "inv_on_flop_Q": 35,
    "nand2_I_gate": 30,
    "fa_prior_stub_driver": 20,
}


def all_matches(drivers: dict, stubs: set[str] | None = None) -> list[Match]:
    stubs = stubs or set()
    out: list[Match] = []
    for _name, fn in PATTERNS:
        out.extend(fn(drivers))
    out.extend(match_fa_prior_stub_driver(drivers, stubs))
    return out


def filter_to_cone(matches: list[Match], cone: set[str]) -> list[Match]:
    return [m for m in matches if m.members & cone or m.anchor in cone]


def coverage(matches: list[Match], cone: set[str]) -> dict:
    covered: set[str] = set()
    for m in matches:
        covered |= m.members & cone
    return {
        "cone_nets": len(cone),
        "covered_nets": len(covered),
        "frac": (len(covered) / len(cone)) if cone else 0.0,
        "uncovered": sorted(short(n) for n in (cone - covered))[:80],
    }


def greedy_cover(matches: list[Match], cone: set[str]) -> list[Match]:
    """Non-overlapping cover preferring higher priority then larger member∩cone."""
    cands = [m for m in matches if m.ok and (m.members & cone)]
    cands.sort(
        key=lambda m: (
            GREEDY_PRIORITY.get(m.pattern_id, 0),
            len(m.members & cone),
            -len(m.pattern_id),
        ),
        reverse=True,
    )
    used: set[str] = set()
    chosen: list[Match] = []
    for m in cands:
        inter = m.members & cone
        if not inter:
            continue
        if inter & used:
            continue
        chosen.append(m)
        used |= inter
    return chosen


def recognize_cone(
    drivers: dict,
    root: str,
    stubs: set[str] | None = None,
) -> dict:
    stubs = stubs or set()
    cone = fanin_cone(root, drivers)
    raw = filter_to_cone(all_matches(drivers, stubs), cone)
    cover = greedy_cover(raw, cone)
    return {
        "root": short(root),
        "root_full": root,
        "cone_size": len(cone),
        "raw_matches": [m.to_json() for m in raw],
        "greedy_cover": [m.to_json() for m in cover],
        "raw_coverage": coverage(raw, cone),
        "greedy_coverage": coverage(cover, cone),
        "_cone": cone,
        "_cover_matches": cover,
        "_raw_matches": raw,
    }
