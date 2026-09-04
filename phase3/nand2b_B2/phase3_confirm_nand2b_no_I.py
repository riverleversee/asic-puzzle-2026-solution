#!/usr/bin/env python3
"""Phase 3 — confirm nand2b_2_23 (→ a32o B2) does not fan-in to I.

Also reports FA-endpoint reachability and enable dependence.

Usage (from rework/):
  python3 tools/phase3_confirm_nand2b_no_I.py
"""
from __future__ import annotations

import json
import sys
from collections import deque
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

from structural_drivers import PRIMARY, is_clk, parse_structural  # noqa: E402
from identify_fa_endpoints import find_fa_pairs, endpoint_sets, fanin_hits  # noqa: E402

OUT_DIR = HERE
OUT_MD = OUT_DIR / "nand2b_no_I.md"
OUT_JSON = OUT_DIR / "nand2b_no_I.json"

# Success-path nand2b: drives a32o_2_4__B2 (second AND of the final a32o)
TARGET_INST = "sky130_fd_sc_hd__nand2b_2_23"
TARGET_OUT = "sky130_fd_sc_hd__a32o_2_4__B2"  # Magic name of nand2b_2_23/Y


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def data_deps(name: str, drivers: dict) -> set[str]:
    info = drivers.get(name)
    if not info:
        return set()
    return {d for d in info["deps"] if not is_clk(d) and d != "rst_n"}


def fanin_leaves(root: str, drivers: dict) -> set[str]:
    leaves: set[str] = set()
    q: deque[str] = deque([root])
    seen = {root}
    while q:
        n = q.popleft()
        if n not in drivers:
            leaves.add(n)
            continue
        for d in data_deps(n, drivers):
            if d not in seen:
                seen.add(d)
                q.append(d)
    return leaves


def main() -> None:
    drivers, _, meta = parse_structural()
    if TARGET_OUT not in drivers:
        raise SystemExit(f"missing target out net {TARGET_OUT}")
    info = drivers[TARGET_OUT]
    if info.get("instance") != TARGET_INST:
        raise SystemExit(
            f"expected driver {TARGET_INST}, got {info.get('instance')} cell={info.get('cell')}"
        )

    leaves = fanin_leaves(TARGET_OUT, drivers)
    prims = sorted(x for x in leaves if x in PRIMARY)
    reaches_i = "I" in leaves
    reaches_en = "enable" in leaves

    pairs = find_fa_pairs(drivers)
    ends = endpoint_sets(pairs)
    fa_hits = fanin_hits(TARGET_OUT, drivers, ends["fa_any"], include_root=True)

    report = {
        "target_instance": short(TARGET_INST),
        "target_out_net": short(TARGET_OUT),
        "cell": info.get("cell"),
        "pins": info.get("in_pins"),
        "rhs": info.get("rhs"),
        "formula": "Y = ¬((¬A_N) ∧ B) = A_N ∨ ¬B   →  Y=1 when A_N=1 or B=0",
        "fanin_primaries": prims,
        "reaches_I": reaches_i,
        "reaches_enable": reaches_en,
        "fa_hit_count": len(fa_hits),
        "fa_hits": [short(x) for x in sorted(fa_hits)],
        "undriven_leaves": sorted(short(x) for x in leaves if x not in PRIMARY),
        "structural": meta,
        "pass_no_I": not reaches_i,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    status = "PASS — does **not** reach `I`" if not reaches_i else "FAIL — reaches `I`"
    md = [
        f"# Phase 3 — nand2b no-`I` check",
        "",
        f"Target: **`{short(TARGET_INST)}`** → out net `{short(TARGET_OUT)}` "
        f"(feeds final `a32o` pin **B2** on the success path).",
        "",
        f"## Result: {status}",
        "",
        f"- Cell: `{info.get('cell')}`",
        f"- Pins: `{info.get('rhs')}`",
        f"- Boolean: `{report['formula']}`",
        f"- Fan-in primaries: {', '.join(f'`{p}`' for p in prims) or '_(none)_'}",
        f"- Reaches `I`: **{reaches_i}**",
        f"- Reaches `enable`: **{reaches_en}**",
        f"- FA endpoints in fan-in: **{len(fa_hits)}** "
        f"({', '.join(f'`{x}`' for x in report['fa_hits'][:8])}{'…' if len(fa_hits) > 8 else ''})",
        "",
        "## Implication for sim watching",
        "",
        "Because this nand2b does **not** depend on serial `I`, its output is a pure "
        "function of FA / enable-side state. Watching `a32o_2_4__B2` (= nand2b Y) going "
        "**high (T/1)** tells us when the FA-side condition is satisfied — independent "
        "of the bit stream.",
        "",
        "Next: `python3 tools/phase3_watch_nand2b.py`",
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {OUT_MD}")
    if reaches_i:
        raise SystemExit("nand2b unexpectedly reaches I")
    print("OK: nand2b does not reach I")


if __name__ == "__main__":
    main()
