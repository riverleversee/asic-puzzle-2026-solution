#!/usr/bin/env python3
"""Trace I-vs-I comparison sites along a221o and a22o I-reaching pins.

A comparison site is a gate that combines ≥2 data operands that each reach
primary I. Counted kinds:
  - mux2: both A0 and A1 reach I  (select between two I-traced values)
  - xor / xnor: both data inputs reach I

Paths:
  a221o.A2 / B2 / C1
  a22o_2_2.A2 / B2   (I-reaching arms; A1/B1 are enable stubs)

Usage (from rework_coded/):
  python3 phase3/a221o_set/trace_I_comparisons.py
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
ROOT = _p
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from structural_drivers import is_clk, parse_structural  # noqa: E402
from render_success_logic_depth import reaches_I  # noqa: E402

OUT = HERE / "I_dep"

# label → net
A221O_PATHS = {
    "a221o.A2": "sky130_fd_sc_hd__mux2_1_12__A1",
    "a221o.B2": "sky130_fd_sc_hd__mux2_1_12__A0",
    "a221o.C1": "sky130_fd_sc_hd__a22o_2_2__X",
}
A22O_PATHS = {
    "a22o.A2": "sky130_fd_sc_hd__a22o_2_2__A2",
    "a22o.B2": "sky130_fd_sc_hd__a22o_2_2__B2",
}


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def data_deps(name: str, drivers: dict) -> set[str]:
    info = drivers.get(name)
    if not info:
        return set()
    return {d for d in info["deps"] if not is_clk(d) and d != "rst_n"}


def fanin_cone(root: str, drivers: dict) -> tuple[set[str], dict[str, int]]:
    depth: dict[str, int] = {root: 0}
    q: deque[str] = deque([root])
    while q:
        n = q.popleft()
        for dep in data_deps(n, drivers):
            nd = depth[n] + 1
            if dep not in depth or nd < depth[dep]:
                depth[dep] = nd
                q.append(dep)
    return set(depth), depth


def pin_map(info: dict) -> dict[str, str]:
    return dict(info.get("in_pins") or {})


def find_comparisons(root: str, drivers: dict, stubs: set[str]) -> dict:
    nodes, depth = fanin_cone(root, drivers)
    i_memo: dict[str, bool] = {}

    def ri(n: str) -> bool:
        if n not in i_memo:
            i_memo[n] = n == "I" or reaches_I(n, drivers, stubs)
        return i_memo[n]

    mux_hits: list[dict] = []
    xor_hits: list[dict] = []

    for n in sorted(nodes):
        info = drivers.get(n)
        if not info:
            continue
        cls = info.get("class")
        pins = pin_map(info)
        if cls == "mux":
            a0, a1 = pins.get("A0"), pins.get("A1")
            s = pins.get("S")
            if a0 and a1 and ri(a0) and ri(a1):
                mux_hits.append(
                    {
                        "net": short(n),
                        "instance": short(info.get("instance") or n),
                        "depth": depth.get(n, -1),
                        "A0": short(a0),
                        "A1": short(a1),
                        "S": short(s) if s else None,
                        "S_reaches_I": bool(s and ri(s)),
                        "kind": "mux2 A0∧A1 →I",
                    }
                )
        elif cls in ("xor", "xnor"):
            deps = sorted(data_deps(n, drivers))
            if len(deps) >= 2 and all(ri(x) for x in deps):
                xor_hits.append(
                    {
                        "net": short(n),
                        "instance": short(info.get("instance") or n),
                        "cell": info.get("cell"),
                        "depth": depth.get(n, -1),
                        "deps": [short(x) for x in deps],
                        "kind": "xor/xnor both →I",
                    }
                )

    mux_hits.sort(key=lambda r: (r["depth"], r["net"]))
    xor_hits.sort(key=lambda r: (r["depth"], r["net"]))
    return {
        "root": short(root),
        "cone_nodes": len(nodes),
        "mux_I_vs_I": mux_hits,
        "xor_I_vs_I": xor_hits,
        "count_mux": len(mux_hits),
        "count_xor": len(xor_hits),
        "count_total": len(mux_hits) + len(xor_hits),
    }


def path_section(label: str, r: dict) -> list[str]:
    lines = [
        f"## Path `{label}` ← `{r['root']}`",
        "",
        f"Total I-vs-I sites: **{r['count_total']}** "
        f"({r['count_mux']} mux + {r['count_xor']} xor).",
        "",
    ]
    if r["mux_I_vs_I"]:
        lines += [
            "### mux2 (A0 & A1 both → I)",
            "",
            "| depth | instance | net | A0 | A1 | S | S→I? |",
            "|------:|----------|-----|----|----|---|:----:|",
        ]
        for h in r["mux_I_vs_I"]:
            lines.append(
                f"| {h['depth']} | `{h['instance']}` | `{h['net']}` | "
                f"`{h['A0']}` | `{h['A1']}` | "
                f"`{h['S'] or '—'}` | {'yes' if h['S_reaches_I'] else ''} |"
            )
        lines.append("")
    else:
        lines += ["_(no mux I-vs-I sites)_", ""]
    if r["xor_I_vs_I"]:
        lines += [
            "### xor/xnor (both deps → I)",
            "",
            "| depth | instance | net | deps |",
            "|------:|----------|-----|------|",
        ]
        for h in r["xor_I_vs_I"]:
            deps = ", ".join(f"`{x}`" for x in h["deps"])
            lines.append(
                f"| {h['depth']} | `{h['instance']}` | `{h['net']}` | {deps} |"
            )
        lines.append("")
    else:
        lines += ["_(no xor/xnor I-vs-I sites)_", ""]
    return lines


def main() -> None:
    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    OUT.mkdir(parents=True, exist_ok=True)

    all_paths = {**A221O_PATHS, **A22O_PATHS}
    reports: dict[str, dict] = {}
    for label, net in all_paths.items():
        rep = find_comparisons(net, drivers, stubs)
        reports[label] = rep
        print(
            f"  {label} ← {rep['root']}: "
            f"mux I-vs-I={rep['count_mux']}  xor I-vs-I={rep['count_xor']}  "
            f"(cone {rep['cone_nodes']})"
        )

    reports["a221o"] = find_comparisons(
        "sky130_fd_sc_hd__a221o_2_1__X", drivers, stubs
    )
    reports["a22o"] = find_comparisons(
        "sky130_fd_sc_hd__a22o_2_2__X", drivers, stubs
    )

    (OUT / "I_comparisons.json").write_text(
        json.dumps(
            {
                "definition": (
                    "I-vs-I comparison = gate with ≥2 data operands that each "
                    "reach primary I. mux2: A0 and A1 both →I. xor/xnor: all "
                    "data deps →I."
                ),
                "paths": reports,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# I-vs-I comparison tracer",
        "",
        "Count gates along each pin’s fan-in that **compare / select between**",
        "two values that both trace to primary `I`.",
        "",
        "**Counted**",
        "",
        "- `mux2` where **both** `A0` and `A1` reach `I` (S may be enable/FA)",
        "- `xor` / `xnor` where **all** data inputs reach `I`",
        "",
        "```text",
        "a221o_2_1.A2 ← mux2_1_12__A1",
        "a221o_2_1.B2 ← mux2_1_12__A0",
        "a221o_2_1.C1 ← a22o_2_2__X",
        "",
        "a22o_2_2.A2  ← a22o_2_2__A2   (flop; D ← mux2_1_13)",
        "a22o_2_2.B2  ← a22o_2_2__B2   (flop; D ← mux2_1_11)",
        "a22o_2_2.A1/B1 = or4.X / buf  (stubs — not traced here)",
        "```",
        "",
        "## Summary",
        "",
        "| Path | cone | mux I-vs-I | xor I-vs-I | total |",
        "|------|-----:|----------:|----------:|------:|",
    ]
    order = [
        "a221o.A2",
        "a221o.B2",
        "a221o.C1",
        "a221o",
        "a22o.A2",
        "a22o.B2",
        "a22o",
    ]
    for pin in order:
        r = reports[pin]
        lines.append(
            f"| `{pin}` ← `{r['root']}` | {r['cone_nodes']} | "
            f"{r['count_mux']} | {r['count_xor']} | {r['count_total']} |"
        )

    lines += ["", "# a221o pins", ""]
    for pin in ("a221o.A2", "a221o.B2", "a221o.C1"):
        lines += path_section(pin, reports[pin])

    lines += ["", "# a22o_2_2 pins (A2 / B2)", ""]
    for pin in ("a22o.A2", "a22o.B2"):
        lines += path_section(pin, reports[pin])

    lines += [
        "## JSON",
        "",
        f"[`I_comparisons.json`](I_comparisons.json)",
        "",
        "Regenerate:",
        "```bash",
        "python3 phase3/a221o_set/trace_I_comparisons.py",
        "```",
        "",
    ]
    md = OUT / "I_comparisons.md"
    md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {md}")
    print(f"wrote {OUT / 'I_comparisons.json'}")


if __name__ == "__main__":
    main()
