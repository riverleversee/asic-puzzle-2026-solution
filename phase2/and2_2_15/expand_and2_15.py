#!/usr/bin/env python3
"""Expand and2_2_15 join + per-arm fan-ins (only-I).

Layout:
  and2_2_15__X_fanin_depth4.*     # join (this folder)
  and4_2_3/and4_2_3__X_…          # B-arm
  inv_2_6/a31o_2_11__X_…          # A-arm sticky

Usage (from rework_coded/):
  python3 phase2/and2_2_15/run.py
"""
from __future__ import annotations

import argparse
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
from render_success_logic_depth import (  # noqa: E402
    count_behind,
    load_fa_endpoints,
    reaches_I,
    render_one,
)

OUT = HERE
AND4_DIR = HERE / "and4_2_3"
INV_DIR = HERE / "inv_2_6"

AND215 = "sky130_fd_sc_hd__and2_2_15__X"
AND4 = "sky130_fd_sc_hd__and4_2_3__X"
A31O = "sky130_fd_sc_hd__a31o_2_11__X"
INV6_A = "sky130_fd_sc_hd__inv_2_6__A"
INV6_Y = "sky130_fd_sc_hd__inv_2_6__Y"

AND215_PINS = {"A": INV6_Y, "B": AND4}
AND215_ROLES = {
    "A": "inv_2_6.Y ← sticky a31o_2_11 / dfrtp_2_28",
    "B": "and4_2_3.X",
}
AND4_PINS = {
    "A": "sky130_fd_sc_hd__and4_2_3__A",
    "B": "sky130_fd_sc_hd__and4_2_3__B",
    "C": "sky130_fd_sc_hd__and4_2_3__C",
    "D": "sky130_fd_sc_hd__nor3_2_2__Y",
}
AND4_ROLES = {
    "A": "dfrtp_2_24.Q",
    "B": "dfrtp_2_25.Q",
    "C": "dfrtp_2_20.Q",
    "D": "nor3_2_2.Y",
}
A31O_PINS = {
    "A1": "sky130_fd_sc_hd__inv_2_9__A",
    "A2": "sky130_fd_sc_hd__inv_2_7__A",
    "A3": "sky130_fd_sc_hd__mux2_1_7__X",
    "B1": INV6_A,
}
A31O_ROLES = {
    "A1": "inv_2_9.A (FA-side)",
    "A2": "inv_2_7.A / and2b.Y (FA-side)",
    "A3": "mux2_1_7.X",
    "B1": "sticky feedback (inv_2_6.A / dfrtp_2_28.Q)",
}

ONLY_I = True


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def pin_rows(pins: dict[str, str], drivers: dict, stubs: set[str]) -> list[dict]:
    rows = []
    for pin, net in pins.items():
        behind = count_behind(net, drivers, stubs)
        prim = list(behind.get("primary_names") or [])
        if net == "I" and "I" not in prim:
            prim = ["I"]
        hit_i = net == "I" or reaches_I(net, drivers, stubs)
        tied = net.endswith("__HI") or "conb" in short(net)
        if net == "I":
            kind = "primary"
        elif tied:
            kind = "tied"
        elif hit_i:
            kind = "→I"
        else:
            kind = "stub"
        rows.append(
            {
                "pin": pin,
                "net": "I" if net == "I" else short(net),
                "net_full": net,
                "kind": kind,
                "reaches_I": hit_i,
                "nodes_behind": behind.get("nodes", 0),
                "flops": behind.get("flops", 0),
                "primaries": prim,
            }
        )
    return rows


def pin_table(rows: list[dict], roles: dict[str, str]) -> list[str]:
    lines = [
        "| Pin | Net | Role | kind | nodes | primaries |",
        "|-----|-----|------|:----:|------:|-----------|",
    ]
    for p in rows:
        prim = ", ".join(f"`{x}`" for x in (p["primaries"] or [])) or "—"
        lines.append(
            f"| `{p['pin']}` | `{p['net']}` | {roles.get(p['pin'], '')} | "
            f"{p['kind']} | {p['nodes_behind']} | {prim} |"
        )
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument("--context-depth", type=int, default=4)
    args = ap.parse_args()

    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    fa_ends = load_fa_endpoints(drivers)
    AND4_DIR.mkdir(parents=True, exist_ok=True)
    INV_DIR.mkdir(parents=True, exist_ok=True)

    root_png = OUT / f"and2_2_15__X_fanin_depth{args.context_depth}.png"
    print(f"render {root_png.name}")
    render_one(
        AND215, drivers, stubs, args.context_depth, root_png,
        with_behind=True, fa_ends=fa_ends, only_i=ONLY_I,
        title="and2_2_15.X · join · only-I · A=inv6 Y · B=and4",
    )
    and215_pins = pin_rows(AND215_PINS, drivers, stubs)

    and4_png = AND4_DIR / f"and4_2_3__X_fanin_depth{args.depth}.png"
    print(f"render {and4_png.relative_to(OUT)}")
    render_one(
        AND4, drivers, stubs, args.depth, and4_png,
        with_behind=True, fa_ends=fa_ends, only_i=ONLY_I,
        title=f"and4_2_3 · B-arm · only-I · depth {args.depth}",
    )
    and4_pins = pin_rows(AND4_PINS, drivers, stubs)

    a31_png = INV_DIR / f"a31o_2_11__X_fanin_depth{args.depth}.png"
    print(f"render {a31_png.relative_to(OUT)}")
    render_one(
        A31O, drivers, stubs, args.depth, a31_png,
        with_behind=True, fa_ends=fa_ends, only_i=ONLY_I,
        title=f"a31o_2_11 · A-arm sticky · only-I · depth {args.depth}",
    )
    a31_pins = pin_rows(A31O_PINS, drivers, stubs)

    root_b = count_behind(AND215, drivers, stubs)
    and4_b = count_behind(AND4, drivers, stubs)
    a31_b = count_behind(A31O, drivers, stubs)
    inv6_b = count_behind(INV6_A, drivers, stubs)
    inv6y_b = count_behind(INV6_Y, drivers, stubs)

    # --- and4 arm README / summary ---
    and4_sum = {
        "arm": "and4_2_3",
        "role": "B-arm of and2_2_15",
        "out_net": short(AND4),
        "formula": "Y = A ∧ B ∧ C ∧ D",
        "pins": and4_pins,
        "nodes_behind": and4_b.get("nodes", 0),
        "flops": and4_b.get("flops", 0),
        "primaries": list(and4_b.get("primary_names") or []),
        "figures": [and4_png.name],
    }
    # Keep pin-sub expand index if present (from expand_pin_subs.py)
    prev_and4 = AND4_DIR / "summary.json"
    if prev_and4.is_file():
        try:
            old = json.loads(prev_and4.read_text(encoding="utf-8"))
            if isinstance(old.get("sub_expands"), dict):
                and4_sum["sub_expands"] = old["sub_expands"]
        except json.JSONDecodeError:
            pass
    (AND4_DIR / "summary.json").write_text(
        json.dumps(and4_sum, indent=2) + "\n", encoding="utf-8"
    )
    and4_md = [
        "# B-arm `and4_2_3` (phase 2)",
        "",
        "Join: [`../README.md`](../README.md) — `and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X`.",
        "",
        "## Figure",
        "",
        f"- [`{and4_png.name}`]({and4_png.name})",
        "",
        "## Pins",
        "",
        *pin_table(and4_pins, AND4_ROLES),
        "",
        f"Cone: **{and4_b.get('nodes', 0)}** n / **{and4_b.get('flops', 0)}** ff · "
        f"`{', '.join(and4_b.get('primary_names') or [])}`",
        "",
        "## Sub-expand (one folder per and4 input)",
        "",
        "Run after this expand to refresh pin folders:",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/expand_pin_subs.py",
        "```",
        "",
        "| Pin | Folder | Expand root |",
        "|-----|--------|-------------|",
        "| `A` | [`dfrtp_2_24/`](dfrtp_2_24/) | `a32o_2_2` |",
        "| `B` | [`dfrtp_2_25/`](dfrtp_2_25/) | `and2b_2_10` |",
        "| `C` | [`dfrtp_2_20/`](dfrtp_2_20/) | `xnor2_2_11` |",
        "| `D` | [`nor3_2_2/`](nor3_2_2/) | `nor3_2_2` |",
        "",
        "## Timelines / structures",
        "",
        "- Inputs timeline: [`timelines/and4_inputs.md`](timelines/and4_inputs.md)",
        "- Block structures: [`structures/`](structures/)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/run.py",
        "python3 phase2/and2_2_15/and4_2_3/expand_pin_subs.py",
        "python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py",
        "python3 phase2/and2_2_15/and4_2_3/run_recognize_structures.py",
        "```",
        "",
    ]
    (AND4_DIR / "README.md").write_text("\n".join(and4_md), encoding="utf-8")

    # --- inv / sticky arm README / summary ---
    inv_sum = {
        "arm": "inv_2_6",
        "role": "A-arm of and2_2_15 (sticky a31o_2_11)",
        "a31o": {
            "out_net": short(A31O),
            "formula": "Y = (A1 ∧ A2 ∧ A3) ∨ B1",
            "pins": a31_pins,
            "nodes_behind": a31_b.get("nodes", 0),
            "flops": a31_b.get("flops", 0),
            "primaries": list(a31_b.get("primary_names") or []),
        },
        "inv_2_6__A": {
            "nodes_behind": inv6_b.get("nodes", 0),
            "flops": inv6_b.get("flops", 0),
            "primaries": list(inv6_b.get("primary_names") or []),
        },
        "inv_2_6__Y": {
            "nodes_behind": inv6y_b.get("nodes", 0),
            "flops": inv6y_b.get("flops", 0),
            "primaries": list(inv6y_b.get("primary_names") or []),
        },
        "figures": [a31_png.name],
    }
    (INV_DIR / "summary.json").write_text(
        json.dumps(inv_sum, indent=2) + "\n", encoding="utf-8"
    )
    stub_pins = [p for p in a31_pins if p["kind"] == "stub"]
    inv_md = [
        "# A-arm `inv_2_6` / sticky `a31o_2_11` (phase 2)",
        "",
        "Join: [`../README.md`](../README.md) — `and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X`.",
        "",
        "```text",
        "inv_2_6.A    ←  dfrtp_2_28.Q",
        "dfrtp_2_28.D ←  a31o_2_11.X",
        "a31o_2_11.X  =  (A1 ∧ A2 ∧ A3) ∨ B1",
        "```",
        "",
        "## Figure",
        "",
        f"- [`{a31_png.name}`]({a31_png.name})",
        "",
        "## a31o_2_11 pins",
        "",
        *pin_table(a31_pins, A31O_ROLES),
        "",
        f"- `a31o_2_11.X`: **{a31_b.get('nodes', 0)}** n / **{a31_b.get('flops', 0)}** ff",
        f"- `inv_2_6.A`: **{inv6_b.get('nodes', 0)}** n / **{inv6_b.get('flops', 0)}** ff",
        f"- `inv_2_6.Y`: **{inv6y_b.get('nodes', 0)}** n / **{inv6y_b.get('flops', 0)}** ff",
        "",
        "## Stub pins (no I)",
        "",
    ]
    for p in stub_pins:
        inv_md.append(f"- `{p['pin']}` ← `{p['net']}`")
    inv_md += [
        "",
        "## Timelines / structures",
        "",
        "- I-indep stubs: [`timelines/noI_stub_timeline.md`](timelines/noI_stub_timeline.md)",
        "- I=1 probes: [`timelines/I1_probe_timeline.md`](timelines/I1_probe_timeline.md)",
        "- Block structures: [`structures/`](structures/)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/run.py",
        "python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py",
        "python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py",
        "python3 phase2/and2_2_15/inv_2_6/run_recognize_structures.py",
        "```",
        "",
    ]
    (INV_DIR / "README.md").write_text("\n".join(inv_md), encoding="utf-8")

    # --- top join index ---
    meta_out = {
        "protocol": "only_i",
        "join": "and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X",
        "arms": {
            "A": {"dir": "inv_2_6", "root": short(INV6_Y), "sticky": short(A31O)},
            "B": {"dir": "and4_2_3", "root": short(AND4)},
        },
        "and2_2_15": {
            "pins": and215_pins,
            "nodes_behind": root_b.get("nodes", 0),
            "flops": root_b.get("flops", 0),
            "primaries": list(root_b.get("primary_names") or []),
        },
        "figures": {
            "join": root_png.name,
            "and4_2_3": f"and4_2_3/{and4_png.name}",
            "inv_2_6": f"inv_2_6/{a31_png.name}",
        },
        "pre_and4_region": "pre_and4_region.md",
        "depths": {"gates": args.depth, "context": args.context_depth},
    }
    (OUT / "summary.json").write_text(json.dumps(meta_out, indent=2) + "\n", encoding="utf-8")

    top_md = [
        "# Success entry `and2_2_15` — join (phase 2)",
        "",
        "Thin AND of two mostly independent arms. Detail lives in the arm folders.",
        "",
        "```text",
        "a32o_2_4.A2  =  and2_2_15.X",
        "and2_2_15.X  =  inv_2_6.Y ∧ and4_2_3.X",
        "              └─ A-arm: inv_2_6/ ─┘   └─ B-arm: and4_2_3/ ─┘",
        "```",
        "",
        "**Testing → phase 3 later.**",
        "",
        "## Arms",
        "",
        "| Arm | Folder | Root |",
        "|-----|--------|------|",
        "| A (sticky) | [`inv_2_6/`](inv_2_6/) | `inv_2_6.Y` ← `a31o_2_11` |",
        "| B (and4) | [`and4_2_3/`](and4_2_3/) | `and4_2_3.X` |",
        "",
        "## Join figure",
        "",
        f"- [`{root_png.name}`]({root_png.name})",
        "",
        "## Join pins",
        "",
        *pin_table(and215_pins, AND215_ROLES),
        "",
        f"Full cone: **{root_b.get('nodes', 0)}** n / **{root_b.get('flops', 0)}** ff · "
        f"`{', '.join(root_b.get('primary_names') or [])}`",
        "",
        "## Size check (A vs B)",
        "",
        "- [`pre_and4_region.md`](pre_and4_region.md)",
        "",
        "Sibling: SET path [`../a221o_behind_inv23/`](../a221o_behind_inv23/). "
        "`and4b_2_3` not expanded here.",
        "",
        "```bash",
        "python3 phase2/and2_2_15/run.py",
        "python3 phase2/and2_2_15/run_count_pre_and4.py",
        "python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py",
        "python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py",
        "python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py",
        "python3 phase2/and2_2_15/and4_2_3/run_recognize_structures.py",
        "python3 phase2/and2_2_15/inv_2_6/run_recognize_structures.py",
        "```",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(top_md), encoding="utf-8")
    print(f"wrote {OUT / 'README.md'}")
    print(f"wrote {AND4_DIR / 'README.md'}")
    print(f"wrote {INV_DIR / 'README.md'}")


if __name__ == "__main__":
    main()
