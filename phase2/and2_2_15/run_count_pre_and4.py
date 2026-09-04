#!/usr/bin/env python3
"""Size and2_2_15 A-arm vs B-arm (pre/beside and4_2_3).

Writes pre_and4_region.md + .json at phase2/and2_2_15/.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/run_count_pre_and4.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from structural_drivers import PRIMARY, is_clk, parse_structural  # noqa: E402
from render_success_logic_depth import count_behind  # noqa: E402

AND215 = "sky130_fd_sc_hd__and2_2_15__X"
AND4 = "sky130_fd_sc_hd__and4_2_3__X"
INV6_Y = "sky130_fd_sc_hd__inv_2_6__Y"

LARGE_NODES = 20
LARGE_FRAC = 0.25


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def fanin_nets(root: str, drivers: dict, stubs: set[str]) -> set[str]:
    """All nets in full fan-in of root (including root)."""
    behind = count_behind(root, drivers, stubs)
    # count_behind does not return the net set; re-BFS
    from collections import deque

    seen: set[str] = {root}
    q = deque([root])
    while q:
        n = q.popleft()
        info = drivers.get(n)
        if not info:
            continue
        for d in info.get("deps") or []:
            if is_clk(d) or d == "rst_n":
                continue
            if d not in seen:
                seen.add(d)
                if d in drivers:
                    q.append(d)
    return seen


def class_hist(nets: set[str], drivers: dict) -> dict[str, int]:
    c: Counter[str] = Counter()
    for n in nets:
        if n in PRIMARY:
            c["primary"] += 1
        elif n in drivers:
            c[drivers[n].get("class") or "?"] += 1
        else:
            c["undriven"] += 1
    return dict(c.most_common())


def leave_nets(nets: set[str], drivers: dict) -> list[str]:
    leaves = []
    for n in nets:
        if n in PRIMARY or n not in drivers:
            leaves.append(n)
            continue
        deps = {
            d
            for d in (drivers[n].get("deps") or [])
            if not is_clk(d) and d != "rst_n"
        }
        if not deps:
            leaves.append(n)
    return sorted(short(x) for x in leaves)


def main() -> None:
    drivers, stubs, meta = parse_structural()
    full = fanin_nets(AND215, drivers, stubs)
    a = fanin_nets(INV6_Y, drivers, stubs)
    b = fanin_nets(AND4, drivers, stubs)
    a_ex = a - b
    b_ex = b - a
    shared = a & b

    def stats(nets: set[str]) -> dict:
        flops = sum(1 for n in nets if (drivers.get(n) or {}).get("class") == "flop")
        prim = sorted(short(n) for n in nets if n in PRIMARY)
        return {
            "nodes": len(nets),
            "flops": flops,
            "primaries": prim,
            "class_hist": class_hist(nets, drivers),
        }

    full_s, a_s, b_s = stats(full), stats(a), stats(b)
    aex_s, bex_s, sh_s = stats(a_ex), stats(b_ex), stats(shared)

    frac = (aex_s["nodes"] / full_s["nodes"]) if full_s["nodes"] else 0.0
    large = aex_s["nodes"] >= LARGE_NODES or frac >= LARGE_FRAC

    payload = {
        "source": meta,
        "roots": {
            "full": short(AND215),
            "A_arm": short(INV6_Y),
            "B_arm": short(AND4),
        },
        "thresholds": {"LARGE_NODES": LARGE_NODES, "LARGE_FRAC": LARGE_FRAC},
        "LARGE_PRE_AND4": large,
        "A_exclusive_frac_of_full": round(frac, 4),
        "full": full_s,
        "A_arm": a_s,
        "B_arm": b_s,
        "A_exclusive": {**aex_s, "leaves": leave_nets(a_ex, drivers)[:40]},
        "B_exclusive": {**bex_s, "leaves": leave_nets(b_ex, drivers)[:40]},
        "shared": sh_s,
    }
    (HERE / "pre_and4_region.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    def row(name: str, s: dict) -> str:
        prim = ", ".join(f"`{p}`" for p in s.get("primaries") or []) or "—"
        return f"| {name} | **{s['nodes']}** | **{s['flops']}** | {prim} |"

    md = [
        "# Pre-`and4_2_3` region size (`and2_2_15`)",
        "",
        "Fan-in set diffs on structural netlist (no simulation).",
        "",
        f"## Verdict: `LARGE_PRE_AND4={'yes' if large else 'no'}`",
        "",
        f"- A-exclusive nodes: **{aex_s['nodes']}** "
        f"({frac:.1%} of full cone {full_s['nodes']})",
        f"- Thresholds: ≥{LARGE_NODES} nodes **or** ≥{LARGE_FRAC:.0%} of full",
        "",
        "## Counts",
        "",
        "| Region | nodes | flops | primaries |",
        "|--------|------:|------:|-----------|",
        row("Full `and2_2_15.X`", full_s),
        row("A-arm `inv_2_6.Y`", a_s),
        row("B-arm `and4_2_3.X`", b_s),
        row("A exclusive (A−B)", aex_s),
        row("B exclusive (B−A)", bex_s),
        row("Shared (A∩B)", sh_s),
        "",
        "## A-exclusive class histogram",
        "",
        "| class | n |",
        "|-------|--:|",
    ]
    for k, v in (aex_s.get("class_hist") or {}).items():
        md.append(f"| `{k}` | {v} |")
    md += [
        "",
        "## A-exclusive leaves (sample)",
        "",
        ", ".join(f"`{x}`" for x in payload["A_exclusive"]["leaves"]) or "—",
        "",
        "JSON: [`pre_and4_region.json`](pre_and4_region.json)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/run_count_pre_and4.py",
        "```",
        "",
    ]
    (HERE / "pre_and4_region.md").write_text("\n".join(md), encoding="utf-8")
    print(f"LARGE_PRE_AND4={'yes' if large else 'no'}")
    print(f"  full={full_s['nodes']}  A={a_s['nodes']}  B={b_s['nodes']}")
    print(f"  A_ex={aex_s['nodes']} ({frac:.1%})  B_ex={bex_s['nodes']}  shared={sh_s['nodes']}")
    print(f"wrote {HERE / 'pre_and4_region.md'}")


if __name__ == "__main__":
    main()
