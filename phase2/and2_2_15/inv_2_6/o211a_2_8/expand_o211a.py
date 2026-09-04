#!/usr/bin/env python3
"""Expand o211a_2_8 (depth-5 cut under a31o_2_11 / inv_2_6 A-arm).

```text
a22o_2_1.B1  ←  o211a_2_8.X
o211a_2_8.X  =  (A1 ∨ A2) ∧ B1 ∧ C1
```

Usage (from rework_coded/):
  python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run.py
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
O211A = "sky130_fd_sc_hd__o211a_2_8__X"

# From structural:
#   o211a_2_8 (.A1(inv_2_8__A), .A2(mux2_1_7__A0),
#              .B1(or2_2_7__X), .C1(inv_2_7__A), .X(...))
PINS = {
    "A1": "sky130_fd_sc_hd__inv_2_8__A",
    "A2": "sky130_fd_sc_hd__mux2_1_7__A0",
    "B1": "sky130_fd_sc_hd__or2_2_7__X",
    "C1": "sky130_fd_sc_hd__inv_2_7__A",
}
ROLES = {
    "A1": "inv_2_8.A / dfrtp_2_29.Q (= mux2_1_7.S)",
    "A2": "mux2_1_7.A0 = nand2_2_25.Y = ¬(or2_2_7__A ∧ I)",
    "B1": "or2_2_7.X = or2_2_7__A ∨ I (= mux2_1_7.A1)",
    "C1": "inv_2_7.A / and2b_2_11.Y (FA stub)",
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
    args = ap.parse_args()

    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    fa_ends = load_fa_endpoints(drivers)
    OUT.mkdir(parents=True, exist_ok=True)

    png = OUT / f"o211a_2_8__X_fanin_depth{args.depth}.png"
    print(f"render {png.name}")
    render_one(
        O211A,
        drivers,
        stubs,
        args.depth,
        png,
        with_behind=True,
        fa_ends=fa_ends,
        only_i=ONLY_I,
        title=f"o211a_2_8 · under a31o/a22o · only-I · depth {args.depth}",
    )

    rows = pin_rows(PINS, drivers, stubs)
    behind = count_behind(O211A, drivers, stubs)
    summary = {
        "gate": "o211a_2_8",
        "parent": "inv_2_6 / a31o_2_11 → a22o_2_1.B1",
        "out_net": short(O211A),
        "formula": "Y = (A1 ∨ A2) ∧ B1 ∧ C1",
        "sink": "a22o_2_1.B1",
        "pins": rows,
        "nodes_behind": behind.get("nodes", 0),
        "flops": behind.get("flops", 0),
        "primaries": list(behind.get("primary_names") or []),
        "figures": [png.name],
        "protocol": "only_i",
        "depth": args.depth,
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    stub_pins = [p for p in rows if p["kind"] == "stub"]
    md = [
        "# `o211a_2_8` (under A-arm `inv_2_6`)",
        "",
        "Parent: [`../README.md`](../README.md) — depth-5 cut on "
        "`a31o_2_11` fan-in; drives `a22o_2_1.B1`.",
        "",
        "```text",
        "a22o_2_1.B1  ←  o211a_2_8.X",
        "o211a_2_8.X  =  (A1 ∨ A2) ∧ B1 ∧ C1",
        "",
        "A1 = inv_2_8__A          # = mux2_1_7.S",
        "A2 = mux2_1_7__A0        # = ¬(or2_2_7__A ∧ I)",
        "B1 = or2_2_7__X          # = or2_2_7__A ∨ I  (= mux.A1)",
        "C1 = inv_2_7__A          # FA stub (and2b.Y)",
        "```",
        "",
        "Shares the mux / or2 / inv_2_8 neighborhood with the fail-trip "
        "inhibit path (`mux2_1_7` → a31o.A3).",
        "",
        "## Figure",
        "",
        f"- [`{png.name}`]({png.name})",
        "",
        "## Pins",
        "",
        *pin_table(rows, ROLES),
        "",
        f"Cone: **{behind.get('nodes', 0)}** n / **{behind.get('flops', 0)}** ff · "
        f"`{', '.join(behind.get('primary_names') or [])}`",
        "",
        "## Stub pins (no I)",
        "",
    ]
    if stub_pins:
        for p in stub_pins:
            md.append(f"- `{p['pin']}` ← `{p['net']}`")
    else:
        md.append("- (none)")
    md += [
        "",
        "## Related",
        "",
        "- Parent a31o fan-in: [`../a31o_2_11__X_fanin_depth5.png`](../a31o_2_11__X_fanin_depth5.png)",
        "- Mux dependence: [`../mux2_1_7_a31o_dependence.png`](../mux2_1_7_a31o_dependence.png)",
        "- Phase-3 fail-trip rule: "
        "[`../../../../phase3/and2_2_15/rules/a31o_2_11_fail_trip_mux_gate.txt`]"
        "(../../../../phase3/and2_2_15/rules/a31o_2_11_fail_trip_mux_gate.txt)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run.py",
        "```",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT / 'README.md'}")
    print(f"wrote {OUT / 'summary.json'}")


if __name__ == "__main__":
    main()
