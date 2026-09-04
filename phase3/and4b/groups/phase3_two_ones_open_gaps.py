#!/usr/bin/env python3
"""Phase 3 — do open-window gaps between the two I=1s matter? (t03/t04)

For each sticky_or and2 leaf in groups 3 and 4, place exactly two ones:
  I=1 on opens[0] and opens[1+g]  for g = 0..gap_max
  (g = number of open windows skipped between the two ones)

Ask: does Y still stick (PASS) when the second 1 is delayed across one or
more open windows?

Usage (from rework_coded/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 phase3/and4b/groups/run_two_ones_gaps.py
  python3 phase3/and4b/groups/run_two_ones_gaps.py --gap-max 4
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
REPO = ROOT.parent

from run_sim import find_iverilog  # noqa: E402
from structural_drivers import parse_structural  # noqa: E402

# Reuse member/open helpers from k-ones tool
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


def bits_from_ones(ones: set[int]) -> str:
    return _kones.bits_from_ones(ones)


def short(n: str) -> str:
    return _kones.short(n)


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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--groups", type=int, nargs="+", default=list(DEFAULT_GROUPS))
    ap.add_argument(
        "--gap-max",
        type=int,
        default=DEFAULT_GAP_MAX,
        help="max open-windows skipped between the two ones (default 4)",
    )
    args = ap.parse_args()
    if args.gap_max < 0:
        raise SystemExit("--gap-max must be >= 0")
    group_idx = set(args.groups)
    gaps = list(range(0, args.gap_max + 1))

    drivers, _stubs, meta = parse_structural()
    print("structural:", meta)
    leaf_meta = _kones.load_leaf_opens()
    members = _kones.build_members(drivers, leaf_meta, group_idx)
    print(f"members: {len(members)}  groups={sorted(group_idx)}  gaps={gaps}")

    BUILD.mkdir(parents=True, exist_ok=True)

    probes: list[tuple[str, str]] = [("I", "I"), ("enable", "enable")]
    for m in members:
        probes += [
            (f"A_{m['slug']}", m["AN"]),
            (f"B_{m['slug']}", m["B"]),
            (f"Y_{m['slug']}", m["Y"]),
        ]

    # Patterns: one mode per (member, gap)
    pats: list[tuple[str, str, dict]] = []
    for m in members:
        opens = m["opens"]
        for g in gaps:
            j = 1 + g
            if j >= len(opens):
                continue
            c0, c1 = opens[0], opens[j]
            ones = {c0, c1}
            lab = f"t{m['group']:02d}_{m['slug']}_g{g}"
            pats.append(
                (
                    lab,
                    bits_from_ones(ones),
                    {
                        "member": m,
                        "gap": g,
                        "c0": c0,
                        "c1": c1,
                        "delta_cyc": c1 - c0,
                        "opens_skipped": opens[1:j],
                    },
                )
            )

    pats_path = BUILD / "pats_two_ones_gaps.txt"
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

    csv_raw = BUILD / "probe_two_ones_gaps.csv"
    tb = BUILD / "tb_two_ones_gaps.v"
    vvp = BUILD / "tb_two_ones_gaps.vvp"
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
        lab = mode_labels[int(row["mode"])]
        by_mode[lab].append(row)

    # Collect outcomes
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
                "group": m["group"],
                "folder": m["folder"],
                "leaf": m["leaf"],
                "instance": m["instance"],
                "open_lab": m["open_lab"],
                "opens": m["opens"],
                "opens_head": m["opens"][:6],
                "gap": meta_p["gap"],
                "c0": meta_p["c0"],
                "c1": meta_p["c1"],
                "delta_cyc": meta_p["delta_cyc"],
                "opens_skipped": meta_p["opens_skipped"],
                "A_final": a_s[-1],
                "B_final": b_s[-1],
                **out,
            }
        )

    # Per-group MD + CSV + PNG; also section summary
    for gi in sorted(group_idx):
        mems = [m for m in members if m["group"] == gi]
        if not mems:
            continue
        folder = mems[0]["folder"]
        gdir = GROUPS / folder
        gdir.mkdir(parents=True, exist_ok=True)
        sub = [r for r in results if r["group"] == gi]

        md = [
            f"# Two-ones open-gap sweep — t{gi:02d}",
            "",
            f"Group: `{mems[0]['label']}`",
            "",
            "Exactly **two** `I=1` pulses on FA opens: `opens[0]` and `opens[1+g]`.",
            f"`g` = number of open windows skipped between them (g=0..{args.gap_max}).",
            "",
            "Question: does a gap (or multiple gaps) between the first and second "
            "1 prevent Y from sticking?",
            "",
            f"Figure: [`two_ones_gaps_timeline.png`](two_ones_gaps_timeline.png)",
            "",
        ]
        any_stick_g0 = False
        any_die_gap = False
        for m in mems:
            leaf_rows = [r for r in sub if r["leaf"] == m["leaf"]]
            md += [
                f"## `{m['leaf']}` (`{m['instance']}`)",
                "",
                f"- open: `{m['open_lab']}`",
                f"- opens: `{m['opens']}`",
                "",
                "| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |",
                "|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|",
            ]
            for r in sorted(leaf_rows, key=lambda x: x["gap"]):
                if r["gap"] == 0 and r["sticks"]:
                    any_stick_g0 = True
                if r["gap"] > 0 and not r["sticks"]:
                    any_die_gap = False  # track opposite
                sk = r["opens_skipped"]
                sk_s = "`—`" if not sk else f"`{sk}`"
                md.append(
                    f"| {r['gap']} | `{{{r['c0']},{r['c1']}}}` | {r['delta_cyc']} | "
                    f"{sk_s} | {r['y_first']} | {r['y_last']} | "
                    f"{r['A_final']}/{r['B_final']} | {r['y_high']} | "
                    f"{'YES' if r['sticks'] else 'no'} |"
                )
            # leaf verdict
            stick_gaps = [r["gap"] for r in leaf_rows if r["sticks"]]
            die_gaps = [r["gap"] for r in leaf_rows if not r["sticks"]]
            if stick_gaps and not die_gaps:
                verd = f"Y sticks for **all** tested gaps g∈{stick_gaps} — gaps do **not** matter."
            elif not stick_gaps:
                verd = "Y never sticks for any tested gap."
            else:
                verd = (
                    f"Y sticks only for g∈{stick_gaps}; dies for g∈{die_gaps} — "
                    f"**gaps matter**."
                )
            md += ["", f"**Verdict:** {verd}", ""]

        # group-level answer
        by_leaf_matter = []
        for m in mems:
            leaf_rows = [r for r in sub if r["leaf"] == m["leaf"]]
            stick_gaps = [r["gap"] for r in leaf_rows if r["sticks"]]
            die_gaps = [r["gap"] for r in leaf_rows if not r["sticks"]]
            matters = bool(stick_gaps) and bool(die_gaps)
            by_leaf_matter.append((m["leaf"], matters, stick_gaps, die_gaps))
        if all(not x[1] for x in by_leaf_matter) and all(x[2] for x in by_leaf_matter):
            group_ans = (
                "**No — gaps do not matter.** Every leaf sticks for every tested g "
                "(including multi-open gaps between the two ones)."
            )
        elif all(not x[1] for x in by_leaf_matter) and all(not x[2] for x in by_leaf_matter):
            group_ans = "**Inconclusive / never sticks** for these two-ones placements."
        else:
            group_ans = (
                "**Yes — gaps can matter** for at least one leaf "
                f"({', '.join(L for L, mat, *_ in by_leaf_matter if mat)})."
            )
        md = md[:8] + [group_ans, ""] + md[8:]

        (gdir / "two_ones_gaps.md").write_text("\n".join(md), encoding="utf-8")
        out_csv = gdir / "two_ones_gaps.csv"
        fields = [
            "group",
            "leaf",
            "instance",
            "gap",
            "c0",
            "c1",
            "delta_cyc",
            "opens_skipped",
            "y_first",
            "y_last",
            "y_high",
            "y_final",
            "A_final",
            "B_final",
            "sticks",
        ]
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in sorted(sub, key=lambda x: (x["leaf"], x["gap"])):
                row = dict(r)
                row["opens_skipped"] = json.dumps(r["opens_skipped"])
                w.writerow(row)

        png = gdir / "two_ones_gaps_timeline.png"

        def variant_fn(m: dict) -> list[tuple[str, str, set[int]]]:
            out: list[tuple[str, str, set[int]]] = []
            for g in gaps:
                j = 1 + g
                if j >= len(m["opens"]):
                    continue
                mode = f"t{gi:02d}_{m['slug']}_g{g}"
                ones = {m["opens"][0], m["opens"][j]}
                out.append((mode, f"g={g}", ones))
            return out

        _kones.plot_ab_y_lane_variants(
            mems,
            by_mode,
            variant_fn,
            png,
            f"t{gi:02d} — A / B + Y · two I=1s on opens[0] & opens[1+g] (g=0..{args.gap_max})",
        )
        dest = GROUPS / f"t{gi:02d}_two_ones_gaps_timeline.png"
        dest.write_bytes(png.read_bytes())
        print(f"copied {dest}")
        print(f"t{gi:02d}: {group_ans}")

    # Combined section note
    idx = GROUPS / "README.md"
    text = idx.read_text(encoding="utf-8") if idx.exists() else ""
    blurb_lines = [
        "## Two-ones open-gap sweep (t03/t04)\n",
        "Exactly two `I=1` on `opens[0]` and `opens[1+g]`; ask if skipped open "
        "windows between them block PASS.\n",
        "```bash",
        "python3 phase3/and4b/groups/run_two_ones_gaps.py --gap-max 4",
        "```\n",
    ]
    for gi in sorted(group_idx):
        mems = [m for m in members if m["group"] == gi]
        if not mems:
            continue
        folder = mems[0]["folder"]
        blurb_lines.append(
            f"- t{gi:02d}: [`{folder}/two_ones_gaps.md`]({folder}/two_ones_gaps.md) · "
            f"[`{folder}/two_ones_gaps_timeline.png`]({folder}/two_ones_gaps_timeline.png)"
        )
    blurb = "\n".join(blurb_lines) + "\n"
    marker = "## Two-ones open-gap sweep"
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
