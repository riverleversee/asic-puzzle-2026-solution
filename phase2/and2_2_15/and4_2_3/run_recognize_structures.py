#!/usr/bin/env python3
"""Recognize + block-render for and4_2_3 B-arm.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/run_recognize_structures.py
"""
from __future__ import annotations

import json
import sys
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

from structural_drivers import parse_structural  # noqa: E402
from structures import recognize_cone, render_block_fanin, write_block_md  # noqa: E402

ROOT_NET = "sky130_fd_sc_hd__and4_2_3__X"
OUT = HERE / "structures"


def main() -> None:
    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    OUT.mkdir(parents=True, exist_ok=True)
    result = recognize_cone(drivers, ROOT_NET, stubs)
    cover = result.pop("_cover_matches")
    result.pop("_raw_matches", None)
    result.pop("_cone", None)

    png = OUT / "block_fanin.png"
    render_block_fanin(
        ROOT_NET,
        drivers,
        cover,
        png,
        title="and4_2_3 · greedy structure blocks",
        max_depth=8,
    )
    write_block_md(result, OUT / "block_fanin.md", png_name=png.name, arm_title="and4_2_3 B-arm")
    # substitution sketch
    lines = [
        "# Substitution sketch — and4_2_3",
        "",
        f"`and4_2_3.X` covered by **{len(result['greedy_cover'])}** greedy blocks "
        f"({result['greedy_coverage']['frac']:.1%} of cone).",
        "",
    ]
    for m in result["greedy_cover"]:
        lines.append(f"- `{m['pattern_id']}` @ `{m['anchor']}`")
    lines.append("")
    (OUT / "substitution_sketch.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "recognized.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"greedy={len(result['greedy_cover'])} raw={len(result['raw_matches'])}")
    print(f"coverage={result['greedy_coverage']['frac']:.1%}")
    for m in result["greedy_cover"]:
        print(f"  {m['pattern_id']} @ {m['anchor']}")
    print(f"wrote {OUT / 'recognized.json'}")


if __name__ == "__main__":
    main()
