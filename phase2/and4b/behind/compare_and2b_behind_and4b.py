#!/usr/bin/env python3
"""Compare and2 + and2b instances in the and4b fan-in cone.

Magic names nets after a load pin, so an and2b *output* may be named
`and4_2_1__A` while the instance is `and2b_2_3`. This script keys on instance.

Usage (from rework/):
  python3 tools/compare_and2b_behind_and4b.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict, deque
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

from structural_drivers import is_clk, parse_structural  # noqa: E402
from render_success_logic_depth import load_fa_endpoints, render_one  # noqa: E402

OUT_DIR = HERE  # phase2/and4b/behind/
AND4B = "sky130_fd_sc_hd__and4b_2_3__X"
# Visible at depth-cut of and4b map as pin net and2b_2_3__B
EXPAND_INST = "sky130_fd_sc_hd__and2b_2_3"

# Families at this level: plain and2 and inverted-A and2b
TARGET_FAMILIES = ("and2", "and2b")


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def cell_family(cell: str) -> str:
    return re.sub(r"_\d+$", "", cell or "")


def is_target_cell(cell: str) -> bool:
    fam = cell_family(cell)
    return fam in TARGET_FAMILIES


def data_deps(name: str, drivers: dict) -> set[str]:
    info = drivers.get(name)
    if not info:
        return set()
    return {d for d in info["deps"] if not is_clk(d) and d != "rst_n"}


def target_instances_in_cone(root: str, drivers: dict) -> dict[str, str]:
    """instance → output net for every and2/and2b reachable in fan-in of root."""
    q: deque[str] = deque([root])
    seen = {root}
    insts: dict[str, str] = {}
    while q:
        n = q.popleft()
        info = drivers.get(n)
        if not info:
            continue
        if is_target_cell(str(info.get("cell", ""))):
            insts[info["instance"]] = n
        for d in data_deps(n, drivers):
            if d not in seen:
                seen.add(d)
                q.append(d)
    return insts


def fingerprint(root: str, drivers: dict, max_depth: int = 8) -> dict:
    depth = {root: 0}
    q: deque[str] = deque([root])
    nodes: set[str] = set()
    while q:
        n = q.popleft()
        d = depth[n]
        if d >= max_depth:
            continue
        for dep in data_deps(n, drivers):
            if dep not in depth:
                depth[dep] = d + 1
                if dep in drivers:
                    nodes.add(dep)
                    q.append(dep)

    classes: Counter = Counter()
    cells: Counter = Counter()
    flops = 0
    primaries: list[str] = []
    for n in depth:
        if n == root:
            continue
        if n in drivers:
            info = drivers[n]
            classes[info.get("class", "?")] += 1
            fam = cell_family(info.get("cell", "?"))
            cells[fam] += 1
            if info.get("kind") == "flop":
                flops += 1
        elif n in ("I", "enable", "rst_n", "clk", "success"):
            primaries.append(n)
            classes["primary"] += 1
        else:
            classes["leaf"] += 1

    info = drivers.get(root, {})
    pins = info.get("in_pins") or {}
    pin_recipe = {
        p: short(v) for p, v in sorted(pins.items()) if not is_clk(v) and v != "rst_n"
    }

    def abstract(net: str) -> str:
        return re.sub(r"_\d+", "_N", short(net))

    pin_pattern = {p: abstract(v) for p, v in pin_recipe.items()}
    fam = cell_family(info.get("cell", ""))

    return {
        "family": fam,
        "instance": short(info.get("instance", "")),
        "out_net": short(root),
        "out_full": root,
        "cell": info.get("cell"),
        "pin_recipe": pin_recipe,
        "pin_pattern": pin_pattern,
        "nodes": len(nodes),
        "flops": flops,
        "primaries": sorted(set(primaries)),
        "class_hist": dict(classes),
        "cell_hist": dict(cells.most_common(12)),
    }


def jaccard(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    inter = sum(min(a[k], b[k]) for k in keys)
    union = sum(max(a[k], b[k]) for k in keys)
    return inter / union if union else 1.0


def similarity(fa: dict, fb: dict) -> dict:
    return {
        "class_jaccard": round(jaccard(Counter(fa["class_hist"]), Counter(fb["class_hist"])), 3),
        "cell_jaccard": round(jaccard(Counter(fa["cell_hist"]), Counter(fb["cell_hist"])), 3),
        "node_ratio": round(min(fa["nodes"], fb["nodes"]) / max(fa["nodes"], fb["nodes"], 1), 3),
        "same_pin_pattern": fa["pin_pattern"] == fb["pin_pattern"],
        "same_family": fa["family"] == fb["family"],
        "same_primaries": fa["primaries"] == fb["primaries"],
    }


STRONG_JACCARD = 0.90
STRONG_NODE_RATIO = 0.85
STRONG_MIN_SIZE = 2


def cluster_key(fp: dict) -> str:
    """Group by family + abstracted wiring template + size band."""
    fam = fp["family"]
    pat = fp["pin_pattern"]
    band = "deep(~110n)" if fp["nodes"] >= 80 else (
        "mid(~40n)" if fp["nodes"] >= 30 else "shallow(~27n)"
    )

    a_n, b = pat.get("A_N", ""), pat.get("B", "")
    a, b2 = pat.get("A", ""), pat.get("B", "")

    if fam == "and2b":
        if a_n.startswith("nand4") and "o21a" in b:
            return f"and2b: nand4_C × o21a_A1  [{band}]"
        if a_n.startswith("nand4") and b.endswith("__B"):
            return f"and2b: nand4_C × flop_B  [{band}]"
        if b == "enable" or "enable" in b:
            return f"and2b: * × enable  [{band}]"
        return f"and2b: {json.dumps(pat, sort_keys=True)}"

    if fam == "and2":
        if a.startswith("or4") and b2.startswith("or4"):
            return f"and2: or4_A × or4_B  [{band}]"
        if a.startswith("nand4") and "o21a" in b2:
            return f"and2: nand4_C × o21a_A1  [{band}]"
        if "o21a" in a or "o21a" in b2:
            return f"and2: involves o21a  [{band}]"
        if "nand4" in a or "nand4" in b2:
            return f"and2: involves nand4  [{band}]"
        return f"and2: {json.dumps(pat, sort_keys=True)}"

    return f"{fam}: {json.dumps(pat, sort_keys=True)}"


def cluster_by_pattern(fps: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for fp in fps:
        groups[cluster_key(fp)].append(fp)
    return dict(groups)


def mean_within(members: list[dict]) -> float | None:
    if len(members) < 2:
        return None
    sims = [
        similarity(a, b)["class_jaccard"]
        for i, a in enumerate(members)
        for b in members[i + 1 :]
    ]
    return sum(sims) / len(sims) if sims else None


def strong_similarity_groups(
    fps: list[dict],
    *,
    jaccard_min: float = STRONG_JACCARD,
    node_ratio_min: float = STRONG_NODE_RATIO,
) -> list[dict]:
    """Union-find clusters of instances with strong pairwise fan-in similarity."""
    n = len(fps)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    for i in range(n):
        for j in range(i + 1, n):
            s = similarity(fps[i], fps[j])
            if s["class_jaccard"] >= jaccard_min and s["node_ratio"] >= node_ratio_min:
                union(i, j)

    buckets: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        buckets[find(i)].append(i)

    groups: list[dict] = []
    for idxs in buckets.values():
        if len(idxs) < STRONG_MIN_SIZE:
            continue
        members = [fps[i] for i in idxs]
        sims = [
            similarity(a, b)
            for i, a in enumerate(members)
            for b in members[i + 1 :]
        ]
        mean_c = sum(s["class_jaccard"] for s in sims) / len(sims)
        mean_cell = sum(s["cell_jaccard"] for s in sims) / len(sims)
        mean_nr = sum(s["node_ratio"] for s in sims) / len(sims)
        families = sorted({m["family"] for m in members})
        groups.append(
            {
                "size": len(members),
                "families": families,
                "members": [m["instance"] for m in sorted(members, key=lambda x: x["instance"])],
                "member_details": [
                    {
                        "instance": m["instance"],
                        "family": m["family"],
                        "out_net": m["out_net"],
                        "nodes": m["nodes"],
                        "flops": m["flops"],
                    }
                    for m in sorted(members, key=lambda x: x["instance"])
                ],
                "mean_class_jaccard": round(mean_c, 3),
                "mean_cell_jaccard": round(mean_cell, 3),
                "mean_node_ratio": round(mean_nr, 3),
                "pin_patterns": sorted(
                    {json.dumps(m["pin_pattern"], sort_keys=True) for m in members}
                ),
            }
        )
    groups.sort(key=lambda g: (-g["size"], -g["mean_class_jaccard"]))
    return groups


def pin_cols(fp: dict) -> tuple[str, str]:
    pr = fp["pin_recipe"]
    if fp["family"] == "and2b":
        return pr.get("A_N", ""), pr.get("B", "")
    return pr.get("A", ""), pr.get("B", "")


def main() -> None:
    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    if AND4B not in drivers:
        raise SystemExit(f"missing {AND4B}")

    insts = target_instances_in_cone(AND4B, drivers)
    fps = [fingerprint(out, drivers) for out in insts.values()]
    fps.sort(key=lambda f: (f["family"], f["instance"]))

    n_and2 = sum(1 for f in fps if f["family"] == "and2")
    n_and2b = sum(1 for f in fps if f["family"] == "and2b")
    print(f"in fan-in of {short(AND4B)}: and2={n_and2}  and2b={n_and2b}  total={len(fps)}")
    for fp in fps:
        p0, p1 = pin_cols(fp)
        print(
            f"  [{fp['family']:5}] {fp['instance']:12} out={fp['out_net']:16} "
            f"pins=({p0}, {p1})  nodes={fp['nodes']} ff={fp['flops']}"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fa_ends = load_fa_endpoints(drivers)

    expand_out = insts.get(EXPAND_INST) or next(iter(insts.values()))
    expand_fp = next(f for f in fps if f["out_full"] == expand_out)
    out_png = OUT_DIR / f"{expand_fp['instance']}_out_{expand_fp['out_net']}_fanin_depth5.png"
    print(f"\nExpanding {expand_fp['instance']} (out {expand_fp['out_net']}) → {out_png.name}")
    render_one(
        expand_out,
        drivers,
        stubs,
        5,
        out_png,
        with_behind=True,
        fa_ends=fa_ends,
        title=(
            f"Fan-in from {expand_fp['family']} {expand_fp['instance']} → {expand_fp['out_net']}"
            f"  ·  depth ≤ 5  (behind {short(AND4B)})"
        ),
    )

    groups = cluster_by_pattern(fps)
    strong = strong_similarity_groups(fps)
    pairwise = []
    for i in range(len(fps)):
        for j in range(i + 1, len(fps)):
            pairwise.append(
                {
                    "a": fps[i]["instance"],
                    "b": fps[j]["instance"],
                    "a_family": fps[i]["family"],
                    "b_family": fps[j]["family"],
                    **similarity(fps[i], fps[j]),
                }
            )

    same_pat = [p for p in pairwise if p["same_pin_pattern"]]
    cross_fam = [p for p in pairwise if not p["same_family"]]
    mean_same = (
        sum(p["class_jaccard"] for p in same_pat) / len(same_pat) if same_pat else None
    )
    mean_all = sum(p["class_jaccard"] for p in pairwise) / len(pairwise) if pairwise else 0
    mean_cross = (
        sum(p["class_jaccard"] for p in cross_fam) / len(cross_fam) if cross_fam else None
    )

    and2_fps = [f for f in fps if f["family"] == "and2"]
    and2b_fps = [f for f in fps if f["family"] == "and2b"]
    cross_template = []
    for a in and2_fps:
        for b in and2b_fps:
            cross_template.append(
                {
                    "a": a["instance"],
                    "b": b["instance"],
                    **similarity(a, b),
                    "a_nodes": a["nodes"],
                    "b_nodes": b["nodes"],
                }
            )
    best_cross = sorted(cross_template, key=lambda p: -p["class_jaccard"])[:8]

    # Pattern clusters that are themselves strong (size≥2 and mean Jaccard ≥ threshold)
    strong_pattern = []
    for key, members in groups.items():
        if len(members) < STRONG_MIN_SIZE:
            continue
        mw = mean_within(members)
        if mw is not None and mw >= STRONG_JACCARD:
            strong_pattern.append(
                {
                    "label": key,
                    "size": len(members),
                    "mean_class_jaccard": round(mw, 3),
                    "members": [m["instance"] for m in members],
                }
            )
    strong_pattern.sort(key=lambda g: (-g["size"], -g["mean_class_jaccard"]))

    n_strong = len(strong)
    n_in_strong = sum(g["size"] for g in strong)

    # Console: lead with strong-group count
    print()
    print("=" * 60)
    print(
        f"STRONG SIMILARITY GROUPS: {n_strong}  "
        f"(threshold class-Jaccard≥{STRONG_JACCARD}, node-ratio≥{STRONG_NODE_RATIO})"
    )
    print(f"  instances in strong groups: {n_in_strong}/{len(fps)}")
    print(f"  strong pin-pattern clusters: {len(strong_pattern)}")
    print("=" * 60)
    for gi, g in enumerate(strong, 1):
        print(
            f"  [{gi}] size={g['size']}  meanJ={g['mean_class_jaccard']:.3f}  "
            f"families={'+'.join(g['families'])}"
        )
        print(f"      {', '.join(g['members'])}")
    print()

    report = {
        "and4b": short(AND4B),
        "and2_count": n_and2,
        "and2b_count": n_and2b,
        "total": len(fps),
        "strong_group_count": n_strong,
        "strong_group_threshold": {
            "class_jaccard": STRONG_JACCARD,
            "node_ratio": STRONG_NODE_RATIO,
            "min_size": STRONG_MIN_SIZE,
        },
        "instances_in_strong_groups": n_in_strong,
        "strong_groups": strong,
        "strong_pin_pattern_cluster_count": len(strong_pattern),
        "strong_pin_pattern_clusters": strong_pattern,
        "expanded_instance": expand_fp["instance"],
        "expanded_out_net": expand_fp["out_net"],
        "figure": str(out_png.relative_to(ROOT)),
        "fingerprints": fps,
        "pairwise": pairwise,
        "mean_class_jaccard_all": round(mean_all, 3),
        "mean_class_jaccard_same_pin_pattern": (
            round(mean_same, 3) if mean_same is not None else None
        ),
        "mean_class_jaccard_and2_vs_and2b": (
            round(mean_cross, 3) if mean_cross is not None else None
        ),
        "best_and2_vs_and2b": best_cross,
    }
    json_path = OUT_DIR / "and2_and2b_similarity.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT_DIR / "and2b_similarity.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    md = [
        f"# and2 + and2b behind `{short(AND4B)}`",
        "",
        f"**{n_and2}** `and2` + **{n_and2b}** `and2b` = **{len(fps)}** instances.",
        f"Expanded: **`{expand_fp['instance']}`** → `{expand_fp['out_net']}` "
        f"([figure]({out_png.name})).",
        "",
        "## Strong similarity groups",
        "",
        f"**Number of strong groups: {n_strong}**",
        "",
        f"Criterion: pairwise class-Jaccard ≥ `{STRONG_JACCARD}` and node-ratio ≥ `{STRONG_NODE_RATIO}` "
        f"(union-find; min size {STRONG_MIN_SIZE}).",
        f"Covered: **{n_in_strong}/{len(fps)}** instances.",
        "",
    ]
    if not strong:
        md.append("_No strong groups found._")
        md.append("")
    else:
        by_inst = {f["instance"]: f for f in fps}
        md += [
            "| # | Size | I | Families | Mean class J | Mean cell J | Members |",
            "|--:|-----:|---|----------|-------------:|------------:|---------|",
        ]
        for gi, g in enumerate(strong, 1):
            mem = ", ".join(f"`{m}`" for m in g["members"])
            reaches = any(
                "I" in (by_inst[m].get("primaries") or [])
                for m in g["members"]
                if m in by_inst
            )
            tag = "hasI" if reaches else "noI"
            md.append(
                f"| {gi} | {g['size']} | {tag} | {'+'.join(g['families'])} | "
                f"{g['mean_class_jaccard']} | {g['mean_cell_jaccard']} | {mem} |"
            )
        md.append("")
        md.append(
            "`hasI` = fan-in reaches primary `I`; `noI` = input-independent."
        )
        md.append("")
        for gi, g in enumerate(strong, 1):
            reaches = any(
                "I" in (by_inst[m].get("primaries") or [])
                for m in g["members"]
                if m in by_inst
            )
            tag = "hasI" if reaches else "noI"
            md.append(f"### Strong group {gi} ({g['size']}× · {tag})")
            md.append("")
            for d in g["member_details"]:
                md.append(
                    f"- `{d['instance']}` ({d['family']}) → `{d['out_net']}` "
                    f"· {d['nodes']}n · {d['flops']}ff"
                )
            md.append("")

    md += [
        f"## Strong pin-pattern clusters ({len(strong_pattern)})",
        "",
        "Pin-template clusters whose *within* mean class-Jaccard also clears the strong threshold:",
        "",
    ]
    if not strong_pattern:
        md.append("_None (pin pattern alone is not enough — see the weak or4×or4 and2 mix)._")
        md.append("")
    else:
        md += [
            "| # | Size | Mean J | Label | Members |",
            "|--:|-----:|-------:|-------|---------|",
        ]
        for gi, g in enumerate(strong_pattern, 1):
            md.append(
                f"| {gi} | {g['size']} | {g['mean_class_jaccard']} | `{g['label']}` | "
                f"{', '.join(f'`{m}`' for m in g['members'])} |"
            )
        md.append("")

    md += [
        "## All instances",
        "",
        "| Family | Instance | Out net | pin0 | pin1 | nodes | ff |",
        "|--------|----------|---------|------|------|------:|---:|",
    ]
    for fp in fps:
        p0, p1 = pin_cols(fp)
        md.append(
            f"| `{fp['family']}` | `{fp['instance']}` | `{fp['out_net']}` | `{p0}` | "
            f"`{p1}` | {fp['nodes']} | {fp['flops']} |"
        )

    md += ["", "## All pin-pattern clusters (incl. weak)", ""]
    for gi, (key, members) in enumerate(sorted(groups.items(), key=lambda x: -len(x[1])), 1):
        mw = mean_within(members)
        flag = ""
        if mw is not None and mw >= STRONG_JACCARD and len(members) >= STRONG_MIN_SIZE:
            flag = " **STRONG**"
        elif len(members) >= STRONG_MIN_SIZE and mw is not None:
            flag = f" _(weak meanJ={mw:.3f})_"
        md.append(f"### {gi}. {len(members)}× `{key}`{flag}")
        md.append("")
        md.append(", ".join(f"`{m['instance']}`" for m in members))
        md.append("")

    md += [
        "## and2 vs and2b (best cross-family)",
        "",
        "| and2 | and2b | class Jaccard | cell Jaccard | node ratio |",
        "|------|-------|-------------:|-------------:|-----------:|",
    ]
    for p in best_cross:
        md.append(
            f"| `{p['a']}` | `{p['b']}` | {p['class_jaccard']} | {p['cell_jaccard']} | "
            f"{p['node_ratio']} |"
        )

    md += [
        "",
        "## Summary counts",
        "",
        f"- **Strong similarity groups: {n_strong}**",
        f"- Strong pin-pattern clusters: **{len(strong_pattern)}**",
        f"- Instances in strong groups: **{n_in_strong}/{len(fps)}**",
        f"- Mean class-Jaccard (all pairs): **{mean_all:.3f}**",
    ]
    if mean_cross is not None:
        md.append(f"- Mean class-Jaccard (and2 ↔ and2b): **{mean_cross:.3f}**")
    md.append("")

    (OUT_DIR / "README.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {OUT_DIR / 'README.md'}")
    print(f"\n>>> strong_group_count = {n_strong}")
    print(f">>> strong_pin_pattern_cluster_count = {len(strong_pattern)}")
    print("\n".join(md[:80]))  # don't dump entire md twice; head is enough
    if len(md) > 80:
        print(f"... ({len(md) - 80} more lines in README)")

if __name__ == "__main__":
    main()
