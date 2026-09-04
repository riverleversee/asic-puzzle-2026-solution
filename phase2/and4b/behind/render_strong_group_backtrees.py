#!/usr/bin/env python3
"""Render fan-in back-trees for each strong and2/and2b similarity group.

Reads phase2/figures/and2b_behind_and4b/and2_and2b_similarity.json
and writes one representative tree per strong group, plus every member
under strong_groups/gNN/.

Usage (from rework/):
  python3 tools/render_strong_group_backtrees.py
  python3 tools/render_strong_group_backtrees.py --depth 5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
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

from structural_drivers import parse_structural  # noqa: E402
from render_success_logic_depth import load_fa_endpoints, render_one  # noqa: E402

SIM_JSON = HERE / "and2_and2b_similarity.json"
OUT_ROOT = HERE / "strong_groups"


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def stem(s: str) -> str:
    return re.sub(r"[^\w.\-]+", "_", s)


def i_tag(reaches_i: bool) -> str:
    return "hasI" if reaches_i else "noI"


def group_reaches_i(group: dict, by_inst: dict) -> bool:
    for m in group.get("members") or []:
        fp = by_inst.get(m) or {}
        if "I" in (fp.get("primaries") or []):
            return True
    return False


def pick_representative(group: dict, by_inst: dict) -> dict:
    """Prefer median node-count member; break ties toward and2b then name."""
    details = []
    for m in group["members"]:
        fp = by_inst.get(m)
        if fp:
            details.append(fp)
    if not details:
        raise SystemExit(f"no fingerprints for group {group['members']}")
    details.sort(key=lambda f: (f["nodes"], f["family"] != "and2b", f["instance"]))
    return details[len(details) // 2]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument(
        "--reps-only",
        action="store_true",
        help="only render one representative tree per group",
    )
    args = ap.parse_args()

    if not SIM_JSON.exists():
        raise SystemExit(f"missing {SIM_JSON} — run compare_and2b_behind_and4b.py first")

    report = json.loads(SIM_JSON.read_text(encoding="utf-8"))
    groups = report.get("strong_groups") or []
    by_inst = {fp["instance"]: fp for fp in report.get("fingerprints") or []}
    if not groups:
        raise SystemExit("no strong_groups in similarity JSON")

    drivers, stubs, meta = parse_structural()
    fa_ends = load_fa_endpoints(drivers)
    print(f"structural: {meta}")
    print(f"strong groups: {len(groups)}  depth≤{args.depth}")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    index = [
        f"# Strong-group back-trees (depth ≤ {args.depth})",
        "",
        f"Source: [`../and2_and2b_similarity.json`](../and2_and2b_similarity.json)",
        f"**{len(groups)}** strong groups · fan-in behind each and2/and2b output.",
        "",
        "`hasI` = fan-in reaches primary `I`; `noI` = input-independent.",
        "",
        "| Group | Size | I | Families | Mean J | Representative | Rep figure | All members |",
        "|------:|-----:|---|----------|-------:|----------------|------------|-------------|",
    ]

    for gi, g in enumerate(groups, 1):
        reaches = group_reaches_i(g, by_inst)
        tag = i_tag(reaches)
        gdir = OUT_ROOT / f"g{gi:02d}_n{g['size']}_{tag}"
        gdir.mkdir(parents=True, exist_ok=True)
        rep = pick_representative(g, by_inst)
        fams = "+".join(g.get("families") or [])
        label = (
            f"g{gi:02d} size={g['size']} {tag} "
            f"meanJ={g['mean_class_jaccard']} [{fams}]"
        )

        rep_net = rep.get("out_full") or ("sky130_fd_sc_hd__" + rep["out_net"])
        if rep_net not in drivers:
            cand = [n for n in drivers if short(n) == rep["out_net"]]
            if not cand:
                raise SystemExit(f"out net not in drivers: {rep['out_net']}")
            rep_net = cand[0]

        rep_png = OUT_ROOT / f"g{gi:02d}_rep_{stem(rep['instance'])}_fanin_depth{args.depth}.png"
        title = (
            f"Strong group {gi}/{len(groups)}  ·  size {g['size']}  ·  {tag}"
            f"  ·  meanJ={g['mean_class_jaccard']}"
            f"  ·  rep `{rep['instance']}` → `{short(rep_net)}`"
        )
        print(f"\n[{label}] rep={rep['instance']} → {short(rep_net)}")
        render_one(
            rep_net,
            drivers,
            stubs,
            args.depth,
            rep_png,
            with_behind=True,
            fa_ends=fa_ends,
            title=title,
        )
        # mirror rep into group folder
        import shutil

        for suf in (".png", ".svg", ".md"):
            src = rep_png.with_suffix(suf)
            if src.exists():
                shutil.copy2(src, gdir / f"REP_{stem(rep['instance'])}_fanin_depth{args.depth}{suf}")

        member_figs = []
        if not args.reps_only:
            for m in g["members"]:
                fp = by_inst[m]
                net = fp.get("out_full") or ("sky130_fd_sc_hd__" + fp["out_net"])
                if net not in drivers:
                    cands = [n for n in drivers if short(n) == fp["out_net"]]
                    net = cands[0]
                out = gdir / f"{stem(m)}_out_{stem(fp['out_net'])}_d{args.depth}.png"
                is_rep = m == rep["instance"]
                mtitle = (
                    f"Strong group {gi} member `{m}` → `{fp['out_net']}`"
                    + ("  (REPRESENTATIVE)" if is_rep else "")
                    + f"  ·  depth ≤ {args.depth}"
                )
                print(f"  member {m} → {fp['out_net']}")
                render_one(
                    net,
                    drivers,
                    stubs,
                    args.depth,
                    out,
                    with_behind=True,
                    fa_ends=fa_ends,
                    title=mtitle,
                )
                member_figs.append(f"[`{out.name}`]({gdir.name}/{out.name})")

        # per-group README
        i_note = (
            "fan-in reaches primary **`I`**"
            if reaches
            else "input-independent (no primary **`I`** in fan-in)"
        )
        glines = [
            f"# Strong group {gi} ({g['size']}× · {tag})",
            "",
            f"- Size: **{g['size']}**",
            f"- I: **{tag}** — {i_note}",
            f"- Families: **{fams}**",
            f"- Mean class-Jaccard: **{g['mean_class_jaccard']}**",
            f"- Representative: `{rep['instance']}` → `{rep['out_net']}`",
            f"- Rep figure: [`{rep_png.name}`](../{rep_png.name})",
            "",
            "## Members",
            "",
            "| Instance | Family | Out net | nodes | ff | figure |",
            "|----------|--------|---------|------:|---:|--------|",
        ]
        for d in g.get("member_details") or []:
            fig = f"`{stem(d['instance'])}_out_{stem(d['out_net'])}_d{args.depth}.png`"
            glines.append(
                f"| `{d['instance']}` | `{d['family']}` | `{d['out_net']}` | "
                f"{d['nodes']} | {d['flops']} | {fig} |"
            )
        glines.append("")
        (gdir / "README.md").write_text("\n".join(glines), encoding="utf-8")

        index.append(
            f"| {gi} | {g['size']} | {tag} | {fams} | {g['mean_class_jaccard']} | "
            f"`{rep['instance']}` | [`{rep_png.name}`]({rep_png.name}) | "
            f"[`{gdir.name}/`]({gdir.name}/) |"
        )

    index += ["", f"Generated with `tools/render_strong_group_backtrees.py --depth {args.depth}`.", ""]
    (OUT_ROOT / "README.md").write_text("\n".join(index), encoding="utf-8")
    print(f"\nwrote {OUT_ROOT / 'README.md'}")
    print(f"strong_group_backtrees = {len(groups)} representative trees")


if __name__ == "__main__":
    main()
