#!/usr/bin/env python3
"""Expand or3_2_8.B under nor3_2_2 (and4.D path).

```text
nor3_2_2.C  ←  or3_2_8.X
or3_2_8.B   ←  dfrtp_2_26.Q
dfrtp_2_26.D ←  o21a_2_11.X
```

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run.py
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
AND4 = HERE.parents[1]  # and4_2_3
if str(AND4) not in sys.path:
    sys.path.insert(0, str(AND4))

from structural_drivers import parse_structural  # noqa: E402
from render_success_logic_depth import (  # noqa: E402
    count_behind,
    load_fa_endpoints,
    reaches_I,
    render_one,
)
from pin_i_hop_rule import allowed_watch_nets  # noqa: E402

OUT = HERE
ONLY_I = True
Q_NET = "sky130_fd_sc_hd__or3_2_8__B"  # dfrtp_2_26.Q
ROOT_NET = "sky130_fd_sc_hd__o21a_2_11__X"  # flop D
GATE = "o21a_2_11"
FIGURE = "o21a_2_11__X"

# o21a: X = (A1 ∨ A2) ∧ B1
PINS = {
    "A1": "sky130_fd_sc_hd__and3_2_11__X",
    "A2": "sky130_fd_sc_hd__xnor2_2_11__B",
    "B1": "sky130_fd_sc_hd__and3_2_11__X",  # may differ — filled from structural below
}
ROLES = {
    "A1": "o21a.A1",
    "A2": "o21a.A2",
    "B1": "o21a.B1",
}


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

    # Fill o21a pins from structural
    d = drivers[ROOT_NET]
    pins = {p: n for p, n in (d.get("in_pins") or {}).items() if p not in ("CLK", "RESET_B")}
    roles = {p: f"o21a.{p}" for p in pins}
    # label known
    for p, n in pins.items():
        if short(n) == "and3_2_11__X":
            roles[p] = f"o21a.{p} ← and3_2_11.X"
        elif short(n) == "xnor2_2_11__B":
            roles[p] = f"o21a.{p} ← xnor2_2_11.B"

    png = OUT / f"{FIGURE}_fanin_depth{args.depth}.png"
    print(f"render {png.name}")
    render_one(
        ROOT_NET,
        drivers,
        stubs,
        args.depth,
        png,
        with_behind=True,
        fa_ends=fa_ends,
        only_i=ONLY_I,
        title=f"o21a_2_11 · or3_2_8.B / dfrtp_2_26.D · only-I · depth {args.depth}",
    )

    rows = pin_rows(pins, drivers, stubs)
    behind = count_behind(ROOT_NET, drivers, stubs)
    q_behind = count_behind(Q_NET, drivers, stubs)

    # Pin rule report
    watch_rows = allowed_watch_nets(ROOT_NET, drivers, stubs, reaches_I, max_depth=args.depth)
    allowed = [r for r in watch_rows if r["allowed"]]
    rejected = [r for r in watch_rows if not r["allowed"]]

    summary = {
        "folder": "or3_2_8_B",
        "parent": "nor3_2_2",
        "and4_pin_path": "D ← nor3.C ← or3_2_8.B",
        "flop": "dfrtp_2_26",
        "q_net": short(Q_NET),
        "out_net": short(ROOT_NET),
        "gate": GATE,
        "formula": "Y = (A1 ∨ A2) ∧ B1",
        "sink": "dfrtp_2_26.D → or3_2_8.B → or3_2_8.X → nor3.C",
        "pins": rows,
        "nodes_behind": behind.get("nodes", 0),
        "flops": behind.get("flops", 0),
        "primaries": list(behind.get("primary_names") or []),
        "q_nodes_behind": q_behind.get("nodes", 0),
        "q_flops": q_behind.get("flops", 0),
        "figures": [png.name],
        "protocol": "only_i",
        "depth": args.depth,
        "pin_rule": "1_hop_to_I",
        "allowed_watches": allowed,
        "rejected_watches": rejected,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "pin_rule_watches.json").write_text(
        json.dumps({"allowed": allowed, "rejected": rejected}, indent=2) + "\n",
        encoding="utf-8",
    )

    stub_pins = [p for p in rows if p["kind"] == "stub"]
    md = [
        "# `or3_2_8_B` — under `nor3_2_2` (and4.D)",
        "",
        "Parent: [`../README.md`](../README.md).",
        "",
        "Pin **B** of `or3_2_8` feeds `nor3_2_2.C` (and4.D path).",
        "It is `dfrtp_2_26.Q`; next-state is `o21a_2_11`.",
        "",
        "```text",
        "nor3_2_2.Y  =  ¬(A ∨ B ∨ C)",
        "C           ←  or3_2_8.X",
        "or3_2_8.B   ←  dfrtp_2_26.Q",
        "dfrtp_2_26.D ←  o21a_2_11.X = (A1 ∨ A2) ∧ B1",
        "```",
        "",
        "## Figure",
        "",
        f"- [`{png.name}`]({png.name})",
        "",
        f"## `{GATE}` pins",
        "",
        *pin_table(rows, roles),
        "",
        f"Cone (`{short(ROOT_NET)}`): **{behind.get('nodes', 0)}** n / "
        f"**{behind.get('flops', 0)}** ff · "
        f"`{', '.join(behind.get('primary_names') or [])}`",
        "",
        f"Behind Q/`{short(Q_NET)}`: **{q_behind.get('nodes', 0)}** n / "
        f"**{q_behind.get('flops', 0)}** ff",
        "",
        "## Pin watch rule (1-hop to I)",
        "",
        "No watches more than **1 node back** from something that reaches `I`.",
        "If a net does **not** reach I, it may only be pinned when the gate it",
        "**feeds into** (toward the root) **does** reach I.",
        "",
        f"Shared helper: [`../../pin_i_hop_rule.py`](../../pin_i_hop_rule.py)",
        "",
        f"Allowed watches (**{len(allowed)}**):",
        "",
        "| net | why | parent |",
        "|-----|-----|--------|",
    ]
    for r in allowed:
        md.append(
            f"| `{r['net']}` | {r['why']} | "
            f"{('`'+r['parent']+'`') if r['parent'] else '—'} |"
        )
    md += [
        "",
        f"Rejected (**{len(rejected)}**):",
        "",
    ]
    if rejected:
        md += [
            "| net | why | parent |",
            "|-----|-----|--------|",
        ]
        for r in rejected:
            md.append(
                f"| `{r['net']}` | {r['why']} | "
                f"{('`'+r['parent']+'`') if r['parent'] else '—'} |"
            )
    else:
        md.append("- (none)")
    md += [
        "",
        "## Stub pins (gate pins, no I)",
        "",
    ]
    if stub_pins:
        for p in stub_pins:
            md.append(f"- `{p['pin']}` ← `{p['net']}`")
    else:
        md.append("- (none)")
    md += [
        "",
        "## Timelines",
        "",
        "- [`timelines/`](timelines/) — I tests using **allowed** watches only",
        "",
        "## Related",
        "",
        "- Parent nor3 fan-in: [`../nor3_2_2__Y_fanin_depth5.png`](../nor3_2_2__Y_fanin_depth5.png)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run.py",
        "python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run_i_tests.py",
        "```",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT / 'README.md'}")
    print(f"allowed watches: {len(allowed)}  rejected: {len(rejected)}")


if __name__ == "__main__":
    main()
