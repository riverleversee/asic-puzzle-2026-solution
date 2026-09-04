#!/usr/bin/env python3
"""Expand and4b using and2/and2b type groups as expand-back points.

Sources the strong pin-pattern clusters + remaining strong pairs/outliers from
phase2/figures/and2b_behind_and4b/and2_and2b_similarity.json — NOT the
join0/join1/and4b_D structural banks.

Each type folder expands fan-in behind every member and2/and2b output.

Usage (from rework/):
  python3 tools/expand_and4b_main_groups.py
  python3 tools/expand_and4b_main_groups.py --depth 5
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
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
from render_success_logic_depth import count_behind, load_fa_endpoints, render_one  # noqa: E402

SIM_JSON = ROOT / "phase2" / "and4b" / "behind" / "and2_and2b_similarity.json"
OUT_DIR = HERE  # phase2/and4b/groups/


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def stem(s: str) -> str:
    return re.sub(r"[^\w.\-]+", "_", s)


def i_tag(reaches_i: bool) -> str:
    """Folder/README tag: hasI = fan-in reaches primary I; noI = input-independent."""
    return "hasI" if reaches_i else "noI"


def members_reach_i(details: list[dict]) -> bool:
    return any("I" in (fp.get("primaries") or []) for fp in details)


def slug_label(label: str, idx: int, size: int, reaches_i: bool) -> str:
    s = label.lower()
    s = s.replace("×", "x").replace("~", "")
    s = re.sub(r"[^\w]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    # Drop redundant "size_N" from remainder labels — size lives in _nN_
    s = re.sub(rf"_?size_{size}_?", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return f"t{idx:02d}_n{size}_{i_tag(reaches_i)}_{s[:50]}"


def resolve_net(fp: dict, drivers: dict) -> str:
    net = fp.get("out_full") or ("sky130_fd_sc_hd__" + fp["out_net"])
    if net in drivers:
        return net
    cands = [n for n in drivers if short(n) == fp["out_net"]]
    if not cands:
        raise SystemExit(f"out net not in drivers: {fp['out_net']}")
    return cands[0]


def pin_pattern_key(fp: dict) -> str:
    return json.dumps(fp.get("pin_pattern") or {}, sort_keys=True)


def build_types(report: dict, by_inst: dict) -> list[dict]:
    """Pin-pattern clusters first, then leftover strong pairs, then outliers."""
    covered: set[str] = set()
    types: list[dict] = []

    for cl in report.get("strong_pin_pattern_clusters") or []:
        members = list(cl["members"])
        covered |= set(members)
        types.append(
            {
                "kind": "pin_pattern",
                "label": cl["label"],
                "mean_class_jaccard": cl.get("mean_class_jaccard"),
                "members": members,
            }
        )

    # Strong groups whose members aren't already covered (g4/g5 pairs, etc.)
    for gi, g in enumerate(report.get("strong_groups") or [], 1):
        leftover = [m for m in g["members"] if m not in covered]
        if not leftover:
            continue
        fams = "+".join(g.get("families") or [])
        types.append(
            {
                "kind": "strong_group_remainder",
                "label": f"strong g{gi} remainder ({fams}, size {len(leftover)})",
                "mean_class_jaccard": g.get("mean_class_jaccard"),
                "strong_group": gi,
                "members": leftover,
            }
        )
        covered |= set(leftover)

    # Singleton pin-pattern leftovers still in a strong group (e.g. and2b_2_3)
    # already handled by strong_group_remainder if any members left.

    outliers = [
        fp["instance"]
        for fp in report.get("fingerprints") or []
        if fp["instance"] not in covered
    ]
    if outliers:
        types.append(
            {
                "kind": "outlier",
                "label": "outliers (not in strong type clusters)",
                "mean_class_jaccard": None,
                "members": outliers,
            }
        )

    # Attach fingerprints
    for t in types:
        details = []
        for m in t["members"]:
            fp = by_inst.get(m)
            if not fp:
                raise SystemExit(f"missing fingerprint for {m}")
            details.append(fp)
        details.sort(key=lambda f: (f["family"], f["instance"]))
        t["member_details"] = details
        t["reaches_I"] = members_reach_i(details)
        # representative = median nodes
        details_by_n = sorted(details, key=lambda f: (f["nodes"], f["instance"]))
        t["representative"] = details_by_n[len(details_by_n) // 2]["instance"]
    return types


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=5)
    ap.add_argument(
        "--reps-only",
        action="store_true",
        help="only expand the representative of each type",
    )
    args = ap.parse_args()

    if not SIM_JSON.exists():
        raise SystemExit(f"missing {SIM_JSON} — run compare_and2b_behind_and4b.py first")

    report = json.loads(SIM_JSON.read_text(encoding="utf-8"))
    by_inst = {fp["instance"]: fp for fp in report.get("fingerprints") or []}
    types = build_types(report, by_inst)

    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    fa_ends = load_fa_endpoints(drivers)

    # Replace prior type-group figure folders; keep generators / run scripts
    keep = {".py", ".md"}  # never wipe whole OUT_DIR (scripts live here)
    if OUT_DIR.exists():
        for child in list(OUT_DIR.iterdir()):
            if child.name.startswith("t") and child.is_dir():
                shutil.rmtree(child)
            elif child.name in ("summary.json", "README.md"):
                try:
                    child.unlink()
                except FileNotFoundError:
                    pass
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    index_rows = []
    summary_types = []

    for ti, t in enumerate(types, 1):
        n = len(t["members"])
        reaches = bool(t.get("reaches_I"))
        tag = i_tag(reaches)
        folder = slug_label(t["label"], ti, n, reaches)
        tdir = OUT_DIR / folder
        tdir.mkdir(parents=True)
        rep_name = t["representative"]
        rep_fp = by_inst[rep_name]
        print(f"\n[{folder}] {t['label']}  n={n}  {tag}  rep={rep_name}")

        member_rows = []
        for fp in t["member_details"]:
            if args.reps_only and fp["instance"] != rep_name:
                continue
            net = resolve_net(fp, drivers)
            behind = count_behind(net, drivers, stubs)
            out = tdir / (
                f"{stem(fp['instance'])}_out_{stem(fp['out_net'])}_d{args.depth}.png"
            )
            is_rep = fp["instance"] == rep_name
            title = (
                f"and4b type {ti} ({n}× · {tag}) `{t['label']}`"
                f"  ·  `{fp['instance']}` → `{fp['out_net']}`"
                + ("  (REP)" if is_rep else "")
                + f"  ·  depth ≤ {args.depth}"
            )
            print(f"  expand {fp['instance']} → {fp['out_net']}")
            render_one(
                net,
                drivers,
                stubs,
                args.depth,
                out,
                with_behind=True,
                fa_ends=fa_ends,
                title=title,
            )
            if is_rep:
                for suf in (".png", ".svg", ".md"):
                    src = out.with_suffix(suf)
                    if src.exists():
                        shutil.copy2(
                            src,
                            tdir / f"REP_{stem(fp['instance'])}_fanin_depth{args.depth}{suf}",
                        )
            member_rows.append(
                {
                    "instance": fp["instance"],
                    "family": fp["family"],
                    "out_net": fp["out_net"],
                    "pin_pattern": fp.get("pin_pattern"),
                    "nodes": fp["nodes"],
                    "flops": fp["flops"],
                    "is_rep": is_rep,
                    "figure": out.name,
                    "nodes_behind_full": behind.get("nodes", 0),
                    "primaries": list(behind.get("primary_names") or []),
                }
            )

        # per-type README
        i_note = (
            "fan-in reaches primary **`I`**"
            if reaches
            else "input-independent (no primary **`I`** in fan-in)"
        )
        glines = [
            f"# Type {ti} ({n}× · {tag}): {t['label']}",
            "",
            f"- Kind: `{t['kind']}`",
            f"- Size: **{n}**",
            f"- I: **{tag}** — {i_note}",
            f"- Mean class-Jaccard: **{t.get('mean_class_jaccard')}**",
            f"- Representative expand-back: `{rep_name}` → `{rep_fp['out_net']}`",
            "",
            "Expand-back points are the **and2 / and2b outputs** in this type "
            "(not join0/join1 banks).",
            "",
            "## Members",
            "",
            "| Instance | Family | Out net | pin pattern | nodes | ff | figure |",
            "|----------|--------|---------|-------------|------:|---:|--------|",
        ]
        for r in member_rows:
            pat = json.dumps(r["pin_pattern"] or {}, sort_keys=True)
            mark = " **REP**" if r["is_rep"] else ""
            glines.append(
                f"| `{r['instance']}`{mark} | `{r['family']}` | `{r['out_net']}` | "
                f"`{pat}` | {r['nodes']} | {r['flops']} | [`{r['figure']}`]({r['figure']}) |"
            )
        glines.append("")
        (tdir / "README.md").write_text("\n".join(glines), encoding="utf-8")

        j = t.get("mean_class_jaccard")
        j_s = f"{j}" if j is not None else "—"
        index_rows.append(
            f"| {ti} | {n} | {tag} | {t['kind']} | {j_s} | `{t['label']}` | "
            f"`{rep_name}` | [`{folder}/`]({folder}/) |"
        )
        summary_types.append(
            {
                "index": ti,
                "folder": folder,
                "size": n,
                "reaches_I": reaches,
                "i_tag": tag,
                "label": t["label"],
                "kind": t["kind"],
                "mean_class_jaccard": t.get("mean_class_jaccard"),
                "representative": rep_name,
                "members": member_rows,
            }
        )

    summary = {
        "source": str(SIM_JSON.relative_to(ROOT)).replace("\\", "/"),
        "depth": args.depth,
        "note": "Expand-back roots = and2/and2b type members from similarity analysis",
        "types": summary_types,
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# and4b expand-backs by and2 / and2b type",
        "",
        "Expand points are the **and2 + and2b instances** grouped earlier in "
        "[`../behind/`](../behind/) — strong pin-pattern "
        "clusters, then remaining strong-group pairs / outliers.",
        "",
        "Not the structural `join0` / `join1` / `and4b_D` banks.",
        "",
        f"Depth ≤ **{args.depth}** · source "
        f"[`and2_and2b_similarity.json`](../behind/and2_and2b_similarity.json)",
        "",
        "`hasI` = fan-in reaches primary `I`; `noI` = input-independent.",
        "",
        "| # | Size | I | Kind | Mean J | Type | Rep | Folder |",
        "|--:|-----:|---|------|-------:|------|-----|--------|",
        *index_rows,
        "",
        "Regenerate:",
        "```bash",
        "python3 tools/expand_and4b_main_groups.py",
        "```",
        "",
    ]
    (OUT_DIR / "README.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {OUT_DIR / 'README.md'}")
    print(f"types={len(types)}")


if __name__ == "__main__":
    main()
