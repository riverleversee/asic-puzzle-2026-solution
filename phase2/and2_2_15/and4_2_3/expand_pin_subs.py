#!/usr/bin/env python3
"""Expand each and4_2_3 input into its own subfolder (only-I, depth 5).

Same protocol as inv_2_6 → o211a_2_8: one folder per and4 pin / flop,
fan-in rooted at the next-state combo that drives that pin.

```text
and4_2_3.X = A ∧ B ∧ C ∧ D

A ← dfrtp_2_24.Q   D← a32o_2_2.X
B ← dfrtp_2_25.Q   D← and2b_2_10.X  (net dfrtp_2_25__D)
C ← dfrtp_2_20.Q   D← xnor2_2_11.Y
D ← nor3_2_2.Y
```

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/expand_pin_subs.py
  python3 phase2/and2_2_15/and4_2_3/expand_pin_subs.py --only dfrtp_2_24
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

ONLY_I = True

# folder_name → expand config
SUBS: dict[str, dict] = {
    "dfrtp_2_24": {
        "and4_pin": "A",
        "flop": "dfrtp_2_24",
        "q_net": "sky130_fd_sc_hd__and4_2_3__A",
        "root": "sky130_fd_sc_hd__a32o_2_2__X",
        "gate": "a32o_2_2",
        "figure_stem": "a32o_2_2__X",
        "formula": "Y = (A1 ∧ A2 ∧ A3) ∨ (B1 ∧ B2)",
        "sink": "dfrtp_2_24.D → and4_2_3.A",
        "pins": {
            "A1": "I",
            "A2": "sky130_fd_sc_hd__inv_2_7__A",
            "A3": "sky130_fd_sc_hd__and3_2_10__B",
            "B1": "sky130_fd_sc_hd__inv_2_10__Y",
            "B2": "sky130_fd_sc_hd__and4_2_3__A",
        },
        "roles": {
            "A1": "primary I",
            "A2": "inv_2_7.A / and2b_2_11.Y (FA stub)",
            "A3": "and3_2_10.B",
            "B1": "inv_2_10.Y",
            "B2": "sticky Q feedback (and4_2_3.A / dfrtp_2_24.Q)",
        },
        "blurb": [
            "Pin **A** of `and4_2_3` is `dfrtp_2_24.Q`.",
            "Next-state is `a32o_2_2` (AO32 sticky hold with I-gated set term).",
        ],
    },
    "dfrtp_2_25": {
        "and4_pin": "B",
        "flop": "dfrtp_2_25",
        "q_net": "sky130_fd_sc_hd__and4_2_3__B",
        "root": "sky130_fd_sc_hd__dfrtp_2_25__D",
        "gate": "and2b_2_10",
        "figure_stem": "and2b_2_10__X",
        "formula": "Y = ¬A_N ∧ B",
        "sink": "dfrtp_2_25.D → and4_2_3.B",
        "pins": {
            "A_N": "sky130_fd_sc_hd__and3_2_11__X",
            "B": "sky130_fd_sc_hd__a21o_2_10__X",
        },
        "roles": {
            "A_N": "and3_2_11.X (active-low AND input)",
            "B": "a21o_2_10.X",
        },
        "blurb": [
            "Pin **B** of `and4_2_3` is `dfrtp_2_25.Q`.",
            "Next-state net `dfrtp_2_25__D` is driven by `and2b_2_10`.",
        ],
    },
    "dfrtp_2_20": {
        "and4_pin": "C",
        "flop": "dfrtp_2_20",
        "q_net": "sky130_fd_sc_hd__and4_2_3__C",
        "root": "sky130_fd_sc_hd__xnor2_2_11__Y",
        "gate": "xnor2_2_11",
        "figure_stem": "xnor2_2_11__Y",
        "formula": "Y = ¬(A ⊕ B)",
        "sink": "dfrtp_2_20.D → and4_2_3.C",
        "pins": {
            "A": "sky130_fd_sc_hd__and4_2_3__C",
            "B": "sky130_fd_sc_hd__xnor2_2_11__B",
        },
        "roles": {
            "A": "Q feedback (and4_2_3.C / dfrtp_2_20.Q)",
            "B": "xnor2_2_11.B ← nand2_2_24.Y",
        },
        "blurb": [
            "Pin **C** of `and4_2_3` is `dfrtp_2_20.Q`.",
            "Next-state is `xnor2_2_11` (compare / hold vs `nand2` side).",
        ],
    },
    "nor3_2_2": {
        "and4_pin": "D",
        "flop": None,
        "q_net": "sky130_fd_sc_hd__nor3_2_2__Y",
        "root": "sky130_fd_sc_hd__nor3_2_2__Y",
        "gate": "nor3_2_2",
        "figure_stem": "nor3_2_2__Y",
        "formula": "Y = ¬(A ∨ B ∨ C)",
        "sink": "and4_2_3.D",
        "pins": {
            "A": "sky130_fd_sc_hd__nor3_2_2__A",
            "B": "sky130_fd_sc_hd__nor3_2_2__B",
            "C": "sky130_fd_sc_hd__or3_2_8__X",
        },
        "roles": {
            "A": "nor3_2_2.A ← dfrtp_2_21.Q",
            "B": "nor3_2_2.B ← dfrtp_2_19.Q",
            "C": "or3_2_8.X",
        },
        "blurb": [
            "Pin **D** of `and4_2_3` is `nor3_2_2.Y` (combinational; not a single flop).",
            "A/B are themselves flop Qs (`dfrtp_2_21`, `dfrtp_2_19`); C is `or3_2_8`.",
        ],
    },
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


def write_run_py(out_dir: Path, folder: str) -> None:
    text = f'''#!/usr/bin/env python3
"""Expand and4_2_3 pin subfolder `{folder}`.

From rework_coded/:
  python3 phase2/and2_2_15/and4_2_3/{folder}/run.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "expand_pin_subs.py"
sys.argv = [str(TOOL), "--only", "{folder}", *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
'''
    (out_dir / "run.py").write_text(text, encoding="utf-8")


def expand_one(
    folder: str,
    cfg: dict,
    drivers: dict,
    stubs: set[str],
    fa_ends,
    depth: int,
) -> dict:
    out = HERE / folder
    out.mkdir(parents=True, exist_ok=True)
    root = cfg["root"]
    png = out / f"{cfg['figure_stem']}_fanin_depth{depth}.png"
    print(f"render {png.relative_to(HERE)}")
    title = (
        f"{cfg['gate']} · and4.{cfg['and4_pin']}"
        + (f" / {cfg['flop']}" if cfg.get("flop") else "")
        + f" · only-I · depth {depth}"
    )
    render_one(
        root,
        drivers,
        stubs,
        depth,
        png,
        with_behind=True,
        fa_ends=fa_ends,
        only_i=ONLY_I,
        title=title,
    )

    rows = pin_rows(cfg["pins"], drivers, stubs)
    behind = count_behind(root, drivers, stubs)
    q_behind = count_behind(cfg["q_net"], drivers, stubs)
    summary = {
        "folder": folder,
        "and4_pin": cfg["and4_pin"],
        "flop": cfg.get("flop"),
        "parent": "and4_2_3",
        "out_net": short(root),
        "q_net": short(cfg["q_net"]),
        "gate": cfg["gate"],
        "formula": cfg["formula"],
        "sink": cfg["sink"],
        "pins": rows,
        "nodes_behind": behind.get("nodes", 0),
        "flops": behind.get("flops", 0),
        "primaries": list(behind.get("primary_names") or []),
        "q_nodes_behind": q_behind.get("nodes", 0),
        "q_flops": q_behind.get("flops", 0),
        "figures": [png.name],
        "protocol": "only_i",
        "depth": depth,
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    stub_pins = [p for p in rows if p["kind"] == "stub"]
    md = [
        f"# `{folder}` — and4_2_3 pin `{cfg['and4_pin']}`",
        "",
        "Parent: [`../README.md`](../README.md).",
        "",
        *[f"{line}" for line in cfg["blurb"]],
        "",
        "```text",
        f"and4_2_3.{cfg['and4_pin']}  ←  {short(cfg['q_net'])}",
        f"{cfg['gate']}  =  {cfg['formula'][4:] if cfg['formula'].startswith('Y = ') else cfg['formula']}",
        f"sink: {cfg['sink']}",
        "```",
        "",
        "## Figure",
        "",
        f"- [`{png.name}`]({png.name})",
        "",
        f"## `{cfg['gate']}` pins",
        "",
        *pin_table(rows, cfg["roles"]),
        "",
        f"Cone (`{short(root)}`): **{behind.get('nodes', 0)}** n / "
        f"**{behind.get('flops', 0)}** ff · "
        f"`{', '.join(behind.get('primary_names') or [])}`",
        "",
        f"Behind Q/`{short(cfg['q_net'])}`: **{q_behind.get('nodes', 0)}** n / "
        f"**{q_behind.get('flops', 0)}** ff",
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
        f"- Parent and4 fan-in: [`../and4_2_3__X_fanin_depth{depth}.png`]"
        f"(../and4_2_3__X_fanin_depth{depth}.png)",
        "- Sibling pin folders: "
        + ", ".join(f"[`../{k}/`](../{k}/)" for k in SUBS if k != folder),
        "",
        "```bash",
        f"python3 phase2/and2_2_15/and4_2_3/{folder}/run.py",
        "```",
        "",
    ]
    (out / "README.md").write_text("\n".join(md), encoding="utf-8")
    write_run_py(out, folder)
    print(f"wrote {out / 'README.md'}")
    return summary


def rewrite_parent_readme(summaries: dict[str, dict], depth: int) -> None:
    """Refresh and4_2_3/README.md sub-expand section; keep timelines/structures."""
    and4_png = f"and4_2_3__X_fanin_depth{depth}.png"
    # Prefer live summary.json if present
    parent_sum_path = HERE / "summary.json"
    if parent_sum_path.is_file():
        parent_sum = json.loads(parent_sum_path.read_text(encoding="utf-8"))
    else:
        parent_sum = {}

    pin_lines = [
        "| Pin | Net | Role | kind | nodes | primaries | folder |",
        "|-----|-----|------|:----:|------:|-----------|--------|",
    ]
    roles = {
        "A": "dfrtp_2_24.Q",
        "B": "dfrtp_2_25.Q",
        "C": "dfrtp_2_20.Q",
        "D": "nor3_2_2.Y",
    }
    folder_by_pin = {cfg["and4_pin"]: name for name, cfg in SUBS.items()}
    for p in parent_sum.get("pins") or []:
        folder = folder_by_pin.get(p["pin"], "")
        prim = ", ".join(f"`{x}`" for x in (p.get("primaries") or [])) or "—"
        link = f"[`{folder}/`]({folder}/)" if folder else "—"
        pin_lines.append(
            f"| `{p['pin']}` | `{p['net']}` | {roles.get(p['pin'], '')} | "
            f"{p.get('kind','')} | {p.get('nodes_behind',0)} | {prim} | {link} |"
        )

    sub_rows = [
        "| Pin | Folder | Expand root | n / ff |",
        "|-----|--------|-------------|-------:|",
    ]
    for name, cfg in SUBS.items():
        s = summaries.get(name) or {}
        sub_rows.append(
            f"| `{cfg['and4_pin']}` | [`{name}/`]({name}/) | `{cfg['gate']}` | "
            f"{s.get('nodes_behind', '?')} / {s.get('flops', '?')} |"
        )

    md = [
        "# B-arm `and4_2_3` (phase 2)",
        "",
        "Join: [`../README.md`](../README.md) — `and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X`.",
        "",
        "## Figure",
        "",
        f"- [`{and4_png}`]({and4_png})",
        "",
        "## Pins",
        "",
        *pin_lines,
        "",
        f"Cone: **{parent_sum.get('nodes_behind', '?')}** n / "
        f"**{parent_sum.get('flops', '?')}** ff · "
        f"`{', '.join(parent_sum.get('primaries') or [])}`",
        "",
        "## Sub-expand (one folder per and4 input)",
        "",
        "Each input figured separately — same only-I depth-5 expansion as "
        "`inv_2_6/o211a_2_8/`.",
        "",
        *sub_rows,
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
    (HERE / "README.md").write_text("\n".join(md), encoding="utf-8")

    # annotate parent summary
    parent_sum["sub_expands"] = {
        name: {
            "and4_pin": cfg["and4_pin"],
            "gate": cfg["gate"],
            "folder": name,
            "figure": f"{name}/{cfg['figure_stem']}_fanin_depth{depth}.png",
            "nodes_behind": (summaries.get(name) or {}).get("nodes_behind"),
            "flops": (summaries.get(name) or {}).get("flops"),
        }
        for name, cfg in SUBS.items()
    }
    parent_sum_path.write_text(
        json.dumps(parent_sum, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument(
        "--only",
        choices=sorted(SUBS.keys()),
        help="Expand a single pin subfolder",
    )
    args = ap.parse_args()

    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    fa_ends = load_fa_endpoints(drivers)

    targets = [args.only] if args.only else list(SUBS.keys())
    summaries: dict[str, dict] = {}
    for name in targets:
        summaries[name] = expand_one(
            name, SUBS[name], drivers, stubs, fa_ends, args.depth
        )

    # If only one, still load siblings' summaries for parent index if present
    if args.only:
        for name in SUBS:
            if name in summaries:
                continue
            sp = HERE / name / "summary.json"
            if sp.is_file():
                summaries[name] = json.loads(sp.read_text(encoding="utf-8"))

    rewrite_parent_readme(summaries, args.depth)
    print(f"wrote {HERE / 'README.md'}")


if __name__ == "__main__":
    main()
