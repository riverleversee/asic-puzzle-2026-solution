#!/usr/bin/env python3
"""Identify full-adder (FA) endpoints in the trusted structural netlist.

Heuristic (same as match_complex_operators FA pairing):
  A full-adder bit is an XOR/XNOR (sum) paired with an AO/OA/maj (carry)
  that shares ≥2 data inputs.

Writes:
  rework/phase2/fa_endpoints.json
  rework/phase2/fa_endpoints.md

Usage (from rework/):
  python3 tools/identify_fa_endpoints.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

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

from structural_drivers import (  # noqa: E402
    STRUCTURAL_V,
    is_clk,
    parse_structural,
)

OUT_JSON = ROOT / "phase2" / "fa_endpoints.json"
OUT_MD = ROOT / "phase2" / "fa_endpoints.md"


def _data_deps(name: str, drivers: dict) -> set[str]:
    info = drivers.get(name)
    if not info:
        return set()
    return {d for d in info["deps"] if not is_clk(d) and d != "rst_n"}


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def find_fa_pairs(drivers: dict) -> list[dict]:
    """Return FA-like {sum, carry, shared, inputs} records (full net names)."""
    xors = [n for n, i in drivers.items() if i.get("class") in ("xor", "xnor")]
    aois = [n for n, i in drivers.items() if i.get("class") == "aoi"]
    pairs: list[dict] = []
    used_aoi: set[str] = set()
    for x in sorted(xors):
        xd = _data_deps(x, drivers)
        best = None
        best_share = 0
        for a in aois:
            if a in used_aoi:
                continue
            share = len(xd & _data_deps(a, drivers))
            if share > best_share:
                best_share = share
                best = a
        if best is not None and best_share >= 2:
            used_aoi.add(best)
            shared = sorted(xd & _data_deps(best, drivers))
            pairs.append(
                {
                    "sum": x,
                    "sum_cell": drivers[x]["cell"],
                    "sum_class": drivers[x]["class"],
                    "carry": best,
                    "carry_cell": drivers[best]["cell"],
                    "shared": best_share,
                    "shared_inputs": shared,
                }
            )
    return pairs


def endpoint_sets(pairs: list[dict]) -> dict[str, set[str]]:
    sums = {p["sum"] for p in pairs}
    carries = {p["carry"] for p in pairs}
    return {
        "fa_sum": sums,
        "fa_carry": carries,
        "fa_any": sums | carries,
        "fa_inputs": {n for p in pairs for n in p["shared_inputs"]},
    }


def fanin_hits(
    root: str,
    drivers: dict,
    targets: set[str],
    *,
    include_root: bool = True,
) -> set[str]:
    """Which targets appear in the fan-in of root (optionally including root)."""
    hit: set[str] = set()
    if include_root and root in targets:
        hit.add(root)
    q = [root]
    seen = {root}
    while q:
        n = q.pop()
        for d in _data_deps(n, drivers):
            if d in targets:
                hit.add(d)
            if d not in seen:
                seen.add(d)
                if d in drivers:
                    q.append(d)
    return hit


def build_report(drivers: dict) -> dict:
    pairs = find_fa_pairs(drivers)
    ends = endpoint_sets(pairs)
    return {
        "source": str(STRUCTURAL_V.relative_to(ROOT)),
        "method": "xor/xnor paired with AO/OA/maj sharing ≥2 data inputs",
        "fa_pair_count": len(pairs),
        "fa_sum_count": len(ends["fa_sum"]),
        "fa_carry_count": len(ends["fa_carry"]),
        "pairs": [
            {
                "sum": short(p["sum"]),
                "sum_full": p["sum"],
                "sum_cell": p["sum_cell"],
                "carry": short(p["carry"]),
                "carry_full": p["carry"],
                "carry_cell": p["carry_cell"],
                "shared": p["shared"],
                "shared_inputs": [short(x) for x in p["shared_inputs"]],
            }
            for p in pairs
        ],
        "endpoints_full": {
            "fa_sum": sorted(ends["fa_sum"]),
            "fa_carry": sorted(ends["fa_carry"]),
            "fa_any": sorted(ends["fa_any"]),
        },
    }


def write_md(report: dict) -> None:
    lines = [
        "# Full-adder endpoints (structural)",
        "",
        f"Source: `{report['source']}`",
        f"Method: {report['method']}",
        "",
        f"- FA-like pairs: **{report['fa_pair_count']}**",
        f"- Sum nets: **{report['fa_sum_count']}**",
        f"- Carry nets: **{report['fa_carry_count']}**",
        "",
        "| # | Sum | Sum cell | Carry | Carry cell | Shared inputs |",
        "|--:|-----|----------|-------|------------|---------------|",
    ]
    for i, p in enumerate(report["pairs"], 1):
        shared = ", ".join(f"`{x}`" for x in p["shared_inputs"][:4])
        if len(p["shared_inputs"]) > 4:
            shared += ", …"
        lines.append(
            f"| {i} | `{p['sum']}` | `{p['sum_cell']}` | `{p['carry']}` | "
            f"`{p['carry_cell']}` | {shared} |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    drivers, _stubs, meta = parse_structural(STRUCTURAL_V)
    report = build_report(drivers)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_md(report)
    print(f"structural: {meta}")
    print(f"FA pairs: {report['fa_pair_count']}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
