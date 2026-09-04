#!/usr/bin/env python3
"""Phase 3 — more open-gap variants for t03/t04 sticky_or and2.

1) three ones with gaps:
     I=1 on opens[0], opens[step], opens[2*step]  where step=1+g
     (g open windows skipped between consecutive ones)

2) two ones, first not on the first open:
     I=1 on opens[s], opens[s+1+g]  for start s>=1

Usage (from rework_coded/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 phase3/and4b/groups/run_ones_gap_variants.py
  python3 phase3/and4b/groups/run_ones_gap_variants.py --gap-max 4 --start-max 3
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from run_sim import find_iverilog  # noqa: E402
from structural_drivers import parse_structural  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "kones", HERE / "phase3_k_ones_flops_timeline.py"
)
_kones = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_kones)

STRUCT = _kones.STRUCT
BUILD = ROOT / "phase3" / "build"
GROUPS = HERE
N_CYC = _kones.N_CYC
DEFAULT_GROUPS = (3, 4)
DEFAULT_GAP_MAX = 4
DEFAULT_START_MAX = 3


def bits_from_ones(ones: set[int]) -> str:
    return _kones.bits_from_ones(ones)


def iverilog_cmd(vvp: Path, sources: list[Path]) -> list[str]:
    return _kones.iverilog_cmd(vvp, sources)


def y_outcome(ys: list[int]) -> dict:
    first = next((c for c, v in enumerate(ys) if v), None)
    last = max((c for c, v in enumerate(ys) if v), default=None)
    sticks = bool(ys) and ys[-1] == 1 and (last is not None and last >= N_CYC - 1)
    return {
        "y_first": first,
        "y_last": last,
        "y_high": sum(ys),
        "y_final": ys[-1] if ys else 0,
        "sticks": sticks,
    }


def group_verdict(leaf_rows_by_leaf: list[tuple[str, list[dict]]]) -> str:
    """Summarize whether any leaf dies / all stick."""
    all_stick = True
    all_die = True
    mixed = []
    for leaf, rows in leaf_rows_by_leaf:
        sticks = [r for r in rows if r["sticks"]]
        dies = [r for r in rows if not r["sticks"]]
        if sticks and dies:
            mixed.append(leaf)
            all_stick = False
            all_die = False
        elif sticks:
            all_die = False
        else:
            all_stick = False
    if all_stick:
        return "All tested placements **stick**."
    if all_die:
        return "All tested placements **die**."
    if mixed:
        return f"**Mixed** — some stick / some die (mixed leaves: {', '.join(mixed)})."
    return "Mixed across leaves (some always-stick, some always-die)."


def write_three_md(gi: int, mems: list[dict], sub: list[dict], gap_max: int, gdir: Path) -> str:
    md = [
        f"# Three-ones open-gap sweep — t{gi:02d}",
        "",
        f"Group: `{mems[0]['label']}`",
        "",
        "Exactly **three** `I=1` pulses on FA opens:",
        "`opens[0]`, `opens[step]`, `opens[2*step]` with `step=1+g`",
        f"(g = open windows skipped between consecutive ones; g=0..{gap_max}).",
        "",
        "Figure: [`three_ones_gaps_timeline.png`](three_ones_gaps_timeline.png)",
        "",
    ]
    by_leaf = []
    for m in mems:
        leaf_rows = sorted(
            [r for r in sub if r["leaf"] == m["leaf"]], key=lambda r: r["gap"]
        )
        by_leaf.append((m["leaf"], leaf_rows))
        md += [
            f"## `{m['leaf']}` (`{m['instance']}`)",
            "",
            f"- opens: `{m['opens']}`",
            "",
            "| g | step | I@ | Y first↑ | Y last | A/B final | Y high | sticks? |",
            "|--:|-----:|----|---------:|-------:|----------:|-------:|:-------:|",
        ]
        for r in leaf_rows:
            md.append(
                f"| {r['gap']} | {r['step']} | `{r['ones']}` | {r['y_first']} | "
                f"{r['y_last']} | {r['A_final']}/{r['B_final']} | {r['y_high']} | "
                f"{'YES' if r['sticks'] else 'no'} |"
            )
        stick_g = [r["gap"] for r in leaf_rows if r["sticks"]]
        die_g = [r["gap"] for r in leaf_rows if not r["sticks"]]
        if stick_g and not die_g:
            verd = f"sticks for all g∈{stick_g}"
        elif die_g and not stick_g:
            verd = f"dies for all g∈{die_g}"
        else:
            verd = f"sticks g∈{stick_g}; dies g∈{die_g}"
        md += ["", f"**Verdict:** {verd}", ""]
    ans = group_verdict(by_leaf)
    md.insert(8, f"**Group:** {ans}")
    md.insert(9, "")
    (gdir / "three_ones_gaps.md").write_text("\n".join(md), encoding="utf-8")
    return ans


def write_late_md(gi: int, mems: list[dict], sub: list[dict], start_max: int, gap_max: int, gdir: Path) -> str:
    md = [
        f"# Two-ones late-start sweep — t{gi:02d}",
        "",
        f"Group: `{mems[0]['label']}`",
        "",
        "Exactly **two** `I=1` pulses, **not** starting at the first open:",
        f"`opens[s]` and `opens[s+1+g]` for s=1..{start_max}, g=0..{gap_max}.",
        "",
        "Figure: [`two_ones_late_timeline.png`](two_ones_late_timeline.png)",
        "",
    ]
    by_leaf = []
    for m in mems:
        leaf_rows = sorted(
            [r for r in sub if r["leaf"] == m["leaf"]],
            key=lambda r: (r["start"], r["gap"]),
        )
        by_leaf.append((m["leaf"], leaf_rows))
        md += [
            f"## `{m['leaf']}` (`{m['instance']}`)",
            "",
            f"- opens: `{m['opens']}`",
            "",
            "| s | g | I@ | Δcyc | Y first↑ | Y last | A/B final | Y high | sticks? |",
            "|--:|--:|----|-----:|---------:|-------:|----------:|-------:|:-------:|",
        ]
        for r in leaf_rows:
            md.append(
                f"| {r['start']} | {r['gap']} | `{r['ones']}` | {r['delta_cyc']} | "
                f"{r['y_first']} | {r['y_last']} | {r['A_final']}/{r['B_final']} | "
                f"{r['y_high']} | {'YES' if r['sticks'] else 'no'} |"
            )
        stick = [f"s{r['start']}g{r['gap']}" for r in leaf_rows if r["sticks"]]
        die = [f"s{r['start']}g{r['gap']}" for r in leaf_rows if not r["sticks"]]
        if stick and not die:
            verd = "sticks for **all** late starts / gaps tested"
        elif die and not stick:
            verd = "dies for all tested late starts / gaps"
        else:
            verd = f"sticks {stick}; dies {die}"
        md += ["", f"**Verdict:** {verd}", ""]
    ans = group_verdict(by_leaf)
    md.insert(7, f"**Group:** {ans}")
    md.insert(8, "")
    (gdir / "two_ones_late.md").write_text("\n".join(md), encoding="utf-8")
    return ans


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            row = dict(r)
            if isinstance(row.get("ones"), list):
                row["ones"] = json.dumps(row["ones"])
            w.writerow(row)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--groups", type=int, nargs="+", default=list(DEFAULT_GROUPS))
    ap.add_argument("--gap-max", type=int, default=DEFAULT_GAP_MAX)
    ap.add_argument(
        "--start-max",
        type=int,
        default=DEFAULT_START_MAX,
        help="max start open index s for late two-ones (default 3)",
    )
    args = ap.parse_args()
    group_idx = set(args.groups)
    gaps = list(range(0, args.gap_max + 1))
    starts = list(range(1, args.start_max + 1))

    drivers, _stubs, meta = parse_structural()
    print("structural:", meta)
    leaf_meta = _kones.load_leaf_opens()
    members = _kones.build_members(drivers, leaf_meta, group_idx)
    print(
        f"members: {len(members)}  groups={sorted(group_idx)}  "
        f"three:g={gaps}  late:s={starts},g={gaps}"
    )

    BUILD.mkdir(parents=True, exist_ok=True)
    probes: list[tuple[str, str]] = [("I", "I"), ("enable", "enable")]
    for m in members:
        probes += [
            (f"A_{m['slug']}", m["AN"]),
            (f"B_{m['slug']}", m["B"]),
            (f"Y_{m['slug']}", m["Y"]),
        ]

    pats: list[tuple[str, str, dict]] = []

    # --- three ones with uniform open-gaps ---
    for m in members:
        opens = m["opens"]
        for g in gaps:
            step = 1 + g
            idxs = [0, step, 2 * step]
            if idxs[-1] >= len(opens):
                continue
            ones_list = [opens[i] for i in idxs]
            lab = f"t{m['group']:02d}_{m['slug']}_3g{g}"
            pats.append(
                (
                    lab,
                    bits_from_ones(set(ones_list)),
                    {
                        "kind": "three",
                        "member": m,
                        "gap": g,
                        "step": step,
                        "ones": ones_list,
                        "start": 0,
                        "delta_cyc": ones_list[-1] - ones_list[0],
                    },
                )
            )

    # --- two ones, late start ---
    for m in members:
        opens = m["opens"]
        for s in starts:
            for g in gaps:
                j = s + 1 + g
                if j >= len(opens):
                    continue
                ones_list = [opens[s], opens[j]]
                lab = f"t{m['group']:02d}_{m['slug']}_s{s}g{g}"
                pats.append(
                    (
                        lab,
                        bits_from_ones(set(ones_list)),
                        {
                            "kind": "late2",
                            "member": m,
                            "gap": g,
                            "step": 1 + g,
                            "ones": ones_list,
                            "start": s,
                            "delta_cyc": ones_list[1] - ones_list[0],
                        },
                    )
                )

    pats_path = BUILD / "pats_ones_gap_variants.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")
    labels = [p[0] for p in probes]
    n = len(probes)
    n_pat = len(pats)
    dumps = []
    for i, (_lab, net) in enumerate(probes):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_ones_gap_variants.csv"
    tb = BUILD / "tb_ones_gap_variants.v"
    vvp = BUILD / "tb_ones_gap_variants.vvp"
    tb.write_text(
        f"""`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O;
  wire success;
  reg [{N_CYC-1}:0] pat [0:{n_pat-1}];
  reg [{n-1}:0] bits;
  integer mode, cyc, fd, i;

  puzzle uut(
    .clk(clk), .rst_n(rst_n), .enable(enable), .I(I),
    .O_0(O[0]), .O_1(O[1]), .O_2(O[2]), .O_3(O[3]),
    .O_4(O[4]), .O_5(O[5]), .O_6(O[6]), .O_7(O[7]),
    .success(success)
  );
  always #5 clk = ~clk;

  initial begin
    $readmemb("{pats_path.as_posix()}", pat);
    fd = $fopen("{csv_raw.as_posix()}", "w");
    $fwrite(fd, "mode,cyc,{','.join(labels)}\\n");
    for (mode=0; mode<{n_pat}; mode=mode+1) begin
      rst_n=0; enable=0; I=0;
      repeat(3) @(posedge clk);
      rst_n=1; @(posedge clk);
      enable=1;
      for (cyc=0; cyc<{N_CYC}; cyc=cyc+1) begin
        @(negedge clk);
        I = pat[mode][cyc];
        @(posedge clk);
        #1;
{chr(10).join(dumps)}
        $fwrite(fd, "%0d,%0d", mode, cyc);
        for (i=0; i<{n}; i=i+1) $fwrite(fd, ",%0d", bits[i]);
        $fwrite(fd, "\\n");
      end
    end
    $fclose(fd);
    $finish;
  end
endmodule
""",
        encoding="utf-8",
    )

    print(f"compile… ({n_pat} patterns, {n} probes)", flush=True)
    r = subprocess.run(
        iverilog_cmd(vvp, [STRUCT, tb]), capture_output=True, text=True, timeout=900
    )
    if r.returncode:
        raise SystemExit((r.stderr or r.stdout)[-6000:])
    _, vvp_bin = find_iverilog()
    print("simulate…", flush=True)
    r2 = subprocess.run(
        [str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=900
    )
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    raw_rows = list(csv.DictReader(csv_raw.open(encoding="utf-8")))
    mode_labels = [p[0] for p in pats]
    by_mode: dict[str, list[dict]] = {lab: [] for lab in mode_labels}
    for row in raw_rows:
        by_mode[mode_labels[int(row["mode"])]].append(row)

    results: list[dict] = []
    for lab, _bits, meta_p in pats:
        m = meta_p["member"]
        rows = by_mode[lab]
        ys = [int(r[f"Y_{m['slug']}"]) for r in rows]
        a_s = [int(r[f"A_{m['slug']}"]) for r in rows]
        b_s = [int(r[f"B_{m['slug']}"]) for r in rows]
        out = y_outcome(ys)
        results.append(
            {
                "kind": meta_p["kind"],
                "group": m["group"],
                "folder": m["folder"],
                "leaf": m["leaf"],
                "instance": m["instance"],
                "opens": m["opens"],
                "gap": meta_p["gap"],
                "step": meta_p["step"],
                "start": meta_p["start"],
                "ones": meta_p["ones"],
                "delta_cyc": meta_p["delta_cyc"],
                "A_final": a_s[-1],
                "B_final": b_s[-1],
                **out,
            }
        )

    for gi in sorted(group_idx):
        mems = [m for m in members if m["group"] == gi]
        if not mems:
            continue
        folder = mems[0]["folder"]
        gdir = GROUPS / folder
        gdir.mkdir(parents=True, exist_ok=True)

        three = [r for r in results if r["group"] == gi and r["kind"] == "three"]
        late = [r for r in results if r["group"] == gi and r["kind"] == "late2"]

        ans3 = write_three_md(gi, mems, three, args.gap_max, gdir)
        ansl = write_late_md(gi, mems, late, args.start_max, args.gap_max, gdir)
        write_csv(
            gdir / "three_ones_gaps.csv",
            sorted(three, key=lambda r: (r["leaf"], r["gap"])),
            [
                "group",
                "leaf",
                "instance",
                "gap",
                "step",
                "ones",
                "y_first",
                "y_last",
                "y_high",
                "y_final",
                "A_final",
                "B_final",
                "sticks",
            ],
        )
        write_csv(
            gdir / "two_ones_late.csv",
            sorted(late, key=lambda r: (r["leaf"], r["start"], r["gap"])),
            [
                "group",
                "leaf",
                "instance",
                "start",
                "gap",
                "ones",
                "delta_cyc",
                "y_first",
                "y_last",
                "y_high",
                "y_final",
                "A_final",
                "B_final",
                "sticks",
            ],
        )

        png3 = gdir / "three_ones_gaps_timeline.png"

        def three_variants(m: dict) -> list[tuple[str, str, set[int]]]:
            out: list[tuple[str, str, set[int]]] = []
            for g in gaps:
                step = 1 + g
                idxs = [0, step, 2 * step]
                if idxs[-1] >= len(m["opens"]):
                    continue
                mode = f"t{gi:02d}_{m['slug']}_3g{g}"
                ones = {m["opens"][i] for i in idxs}
                out.append((mode, f"g={g}", ones))
            return out

        _kones.plot_ab_y_lane_variants(
            mems,
            by_mode,
            three_variants,
            png3,
            f"t{gi:02d} — A / B + Y · three I=1s · step=1+g between opens",
        )
        (GROUPS / f"t{gi:02d}_three_ones_gaps_timeline.png").write_bytes(png3.read_bytes())

        pngl = gdir / "two_ones_late_timeline.png"

        def late_variants(m: dict) -> list[tuple[str, str, set[int]]]:
            out: list[tuple[str, str, set[int]]] = []
            for s in starts:
                for g in gaps:
                    j = s + 1 + g
                    if j >= len(m["opens"]):
                        continue
                    mode = f"t{gi:02d}_{m['slug']}_s{s}g{g}"
                    ones = {m["opens"][s], m["opens"][j]}
                    out.append((mode, f"s={s} g={g}", ones))
            return out

        _kones.plot_ab_y_lane_variants(
            mems,
            by_mode,
            late_variants,
            pngl,
            f"t{gi:02d} — A / B + Y · two I=1s on opens[s] & opens[s+1+g] (s≥1)",
        )
        (GROUPS / f"t{gi:02d}_two_ones_late_timeline.png").write_bytes(pngl.read_bytes())

        print(f"t{gi:02d} three: {ans3}")
        print(f"t{gi:02d} late2: {ansl}")

    # README blurb
    idx = GROUPS / "README.md"
    text = idx.read_text(encoding="utf-8") if idx.exists() else ""
    blurb = "\n".join(
        [
            "## Three-ones gaps + late two-ones (t03/t04)\n",
            "- **three**: `opens[0], opens[step], opens[2*step]`, `step=1+g`",
            "- **late two**: `opens[s], opens[s+1+g]` with `s≥1`\n",
            "```bash",
            "python3 phase3/and4b/groups/run_ones_gap_variants.py --gap-max 4 --start-max 3",
            "```\n",
        ]
        + [
            f"- t{gi:02d}: "
            f"[`{(m:=[x for x in members if x['group']==gi])[0]['folder']}/three_ones_gaps.md`]"
            f"({m[0]['folder']}/three_ones_gaps.md) · "
            f"[`{m[0]['folder']}/two_ones_late.md`]({m[0]['folder']}/two_ones_late.md)"
            for gi in sorted(group_idx)
            if any(x["group"] == gi for x in members)
        ]
    ) + "\n"
    marker = "## Three-ones gaps + late two-ones"
    if marker in text:
        pre, _, rest = text.partition(marker)
        nxt = rest.find("\n## ")
        after = rest[nxt + 1 :] if nxt >= 0 else ""
        text = pre.rstrip() + "\n\n" + blurb + ("\n" + after if after else "\n")
    else:
        text = text.rstrip() + "\n\n" + blurb + "\n"
    idx.write_text(text, encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
