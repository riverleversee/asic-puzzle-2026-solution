#!/usr/bin/env python3
"""Expand SET-path logic behind inv_2_23 (only-I protocol).

One flat folder — three fan-in figures + pin tables (no per-pin figure clutter):
  inv_2_23__A_fanin_depth4.*
  a31o_2_12__X_fanin_depth5.*
  a221o_2_1__X_fanin_depth5.*

Usage (from rework_coded/):
  python3 phase2/a221o_behind_inv23/run.py
"""
from __future__ import annotations

import argparse
import json
import shutil
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

INV23_A = "sky130_fd_sc_hd__inv_2_23__A"
A31O = "sky130_fd_sc_hd__a31o_2_12__X"
A221O = "sky130_fd_sc_hd__a221o_2_1__X"
INV11_A = "sky130_fd_sc_hd__inv_2_11__A"

A31O_PINS = {
    "A1": "I",
    "A2": "sky130_fd_sc_hd__inv_2_7__A",
    "A3": A221O,
    "B1": INV11_A,
}
A31O_ROLES = {
    "A1": "serial I",
    "A2": "and2b_2_11.Y (FA path) — stub",
    "A3": "a221o fold",
    "B1": "sticky feedback (flop Q)",
}

A221O_PINS = {
    "A1": "sky130_fd_sc_hd__or4bb_2_0__X",
    "A2": "sky130_fd_sc_hd__mux2_1_12__A1",
    "B1": "sky130_fd_sc_hd__conb_1_2__HI",
    "B2": "sky130_fd_sc_hd__mux2_1_12__A0",
    "C1": "sky130_fd_sc_hd__a22o_2_2__X",
}
A221O_ROLES = {
    "A1": "or4bb — stub (no I)",
    "A2": "mux A1 flop",
    "B1": "tied HI",
    "B2": "mux A0 flop",
    "C1": "a22o",
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


def wipe_legacy() -> None:
    """Remove old pins/ + a31o/ layout left from earlier expands."""
    for rel in ("pins", "a31o"):
        p = OUT / rel
        if p.is_dir():
            shutil.rmtree(p)
            print(f"  removed legacy {rel}/")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=5, help="fan-in depth for a31o/a221o")
    ap.add_argument("--context-depth", type=int, default=4, help="inv_2_23 context depth")
    args = ap.parse_args()

    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    print("protocol: only_i — stub non-I cones; no per-pin figures")
    fa_ends = load_fa_endpoints(drivers)
    OUT.mkdir(parents=True, exist_ok=True)
    wipe_legacy()

    # 1) context
    inv_png = OUT / f"inv_2_23__A_fanin_depth{args.context_depth}.png"
    print(f"render {inv_png.name}")
    render_one(
        INV23_A,
        drivers,
        stubs,
        args.context_depth,
        inv_png,
        with_behind=True,
        fa_ends=fa_ends,
        only_i=ONLY_I,
        title="inv_2_23.A · only-I · a31o @ d=2 · a221o @ d=3",
    )

    # 2) a31o
    a31_png = OUT / f"a31o_2_12__X_fanin_depth{args.depth}.png"
    print(f"render {a31_png.name}")
    render_one(
        A31O,
        drivers,
        stubs,
        args.depth,
        a31_png,
        with_behind=True,
        fa_ends=fa_ends,
        only_i=ONLY_I,
        title=f"a31o_2_12 · only-I · depth {args.depth}",
    )
    a31_pins = pin_rows(A31O_PINS, drivers, stubs)

    # 3) a221o
    a221_png = OUT / f"a221o_2_1__X_fanin_depth{args.depth}.png"
    print(f"render {a221_png.name}")
    render_one(
        A221O,
        drivers,
        stubs,
        args.depth,
        a221_png,
        with_behind=True,
        fa_ends=fa_ends,
        only_i=ONLY_I,
        title=f"a221o_2_1 · only-I · depth {args.depth}",
    )
    a221_pins = pin_rows(A221O_PINS, drivers, stubs)

    inv_b = count_behind(INV23_A, drivers, stubs)
    a31_b = count_behind(A31O, drivers, stubs)
    a221_b = count_behind(A221O, drivers, stubs)

    meta_out = {
        "protocol": "only_i",
        "protocol_note": (
            "Expand only along fan-in that reaches primary I; "
            "non-I branches shown once as stubs. No per-pin figures."
        ),
        "chain": [
            "a32o_2_4.A1 = inv_2_23.A",
            "inv_2_23.A ← inv_2_11.Y",
            "inv_2_11.A ← dfrtp_2_37.Q (net inv_2_11__A)",
            "dfrtp_2_37.D ← a31o_2_12.X",
            "a31o_2_12 = (I ∧ inv_2_7.A ∧ a221o_2_1.X) ∨ inv_2_11.A",
            "a221o_2_1.X = (A1∧A2) ∨ (B1∧B2) ∨ C1",
        ],
        "aliases": {
            "inv_2_7__A": "and2b_2_11.Y",
            "or2_2_11__A": "and2b_2_11.A_N / dfrtp_2_47.Q",
            "buf_2_0__X": "buffer of or4_2_4__X → a22o.B1",
        },
        "a31o": {
            "instance": "a31o_2_12",
            "out_net": short(A31O),
            "formula": "Y = (A1 ∧ A2 ∧ A3) ∨ B1",
            "pins": a31_pins,
            "nodes_behind": a31_b.get("nodes", 0),
            "flops": a31_b.get("flops", 0),
            "primaries": list(a31_b.get("primary_names") or []),
        },
        "a221o": {
            "instance": "a221o_2_1",
            "out_net": short(A221O),
            "formula": "Y = (A1∧A2) ∨ (B1∧B2) ∨ C1",
            "pins": a221_pins,
            "nodes_behind": a221_b.get("nodes", 0),
            "flops": a221_b.get("flops", 0),
            "primaries": list(a221_b.get("primary_names") or []),
        },
        "inv_2_23__A": {
            "nodes_behind": inv_b.get("nodes", 0),
            "flops": inv_b.get("flops", 0),
            "primaries": list(inv_b.get("primary_names") or []),
        },
        "depths": {"gates": args.depth, "context": args.context_depth},
        "figures": [inv_png.name, a31_png.name, a221_png.name],
    }
    (OUT / "summary.json").write_text(json.dumps(meta_out, indent=2) + "\n", encoding="utf-8")

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

    md = [
        "# SET path behind `inv_2_23` — visuals (phase 2)",
        "",
        "Fan-in / only-I expands of the sticky SET arm for interpreting the netlist.",
        "**Testing and rules live in phase 3:** "
        "[`../../phase3/a221o_set/`](../../phase3/a221o_set/).",
        "",
        "## Protocol (only-I)",
        "",
        "Deepen only branches that reach primary `I`. Non-I cones stay as **stubs** "
        "(dashed gray · `⋯ no I`).",
        "",
        "## Chain",
        "",
        "```text",
        "a32o_2_4.A1  =  inv_2_23.A",
        "inv_2_23.A   ←  inv_2_11.Y",
        "inv_2_11.A   ←  dfrtp_2_37.Q          # net inv_2_11__A",
        "dfrtp_2_37.D ←  a31o_2_12.X",
        "",
        "a31o_2_12.X  =  (A1 ∧ A2 ∧ A3) ∨ B1",
        "  A1 = I",
        "  A2 = inv_2_7__A = and2b_2_11.Y     # stub; A_N=or2_2_11__A",
        "  A3 = a221o_2_1.X",
        "  B1 = inv_2_11__A                   # sticky Q",
        "",
        "a221o_2_1.X  =  (A1 ∧ A2) ∨ (B1 ∧ B2) ∨ C1",
        "```",
        "",
        "## Name aliases",
        "",
        "| Canonical net | Also |",
        "|---------------|------|",
        "| `inv_2_7__A` | `and2b_2_11.Y` |",
        "| `or2_2_11__A` | `and2b_2_11.A_N`, `dfrtp_2_47.Q` (collapsed under and2b stub) |",
        "| `or4_2_4__X` | `a22o.A1`, `buf_2_0.A` |",
        "| `buf_2_0__X` | `a22o.B1` (= `or4_2_4__X`) |",
        "",
        "## Figures",
        "",
        f"1. Context: [`{inv_png.name}`]({inv_png.name})",
        f"2. **a31o**: [`{a31_png.name}`]({a31_png.name})",
        f"3. **a221o**: [`{a221_png.name}`]({a221_png.name})",
        "4. Stub timeline (all0 FA-prior nets): "
        "[`timelines/noI_stub_timeline.md`](timelines/noI_stub_timeline.md)",
        "",
        "## Phase 3 tests",
        "",
        "- I-dep / shift-chain / spaced-I: "
        "[`../../phase3/a221o_set/`](../../phase3/a221o_set/)",
        "- Sticky SET spacing rule: "
        "[`../../phase3/a221o_set/rules/a31o_sticky_set_spacing.txt`]"
        "(../../phase3/a221o_set/rules/a31o_sticky_set_spacing.txt)",
        "",
        "## a31o_2_12 pins",
        "",
        *pin_table(a31_pins, A31O_ROLES),
        "",
        "## a221o_2_1 pins",
        "",
        *pin_table(a221_pins, A221O_ROLES),
        "",
        "## Cone size (full fan-in)",
        "",
        f"- `inv_2_23.A`: **{inv_b.get('nodes', 0)}** n / **{inv_b.get('flops', 0)}** ff · "
        f"`{', '.join(inv_b.get('primary_names') or [])}`",
        f"- `a31o_2_12.X`: **{a31_b.get('nodes', 0)}** n / **{a31_b.get('flops', 0)}** ff · "
        f"`{', '.join(a31_b.get('primary_names') or [])}`",
        f"- `a221o_2_1.X`: **{a221_b.get('nodes', 0)}** n / **{a221_b.get('flops', 0)}** ff · "
        f"`{', '.join(a221_b.get('primary_names') or [])}`",
        "",
        "Regenerate (visuals only):",
        "```bash",
        "python3 phase2/a221o_behind_inv23/run.py",
        "python3 phase2/a221o_behind_inv23/run_noI_stub_timeline.py",
        "```",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT / 'README.md'}")
    print(f"wrote {OUT / 'summary.json'}")


if __name__ == "__main__":
    main()
