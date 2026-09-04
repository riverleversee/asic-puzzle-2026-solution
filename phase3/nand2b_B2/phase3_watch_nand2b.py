#!/usr/bin/env python3
"""Phase 3 — Icarus watch: when is nand2b_2_23 / a32o_2_4__B2 high?

Structural sim (rework netlist + repo PDK). Patterns: all0, all1, cpsat ones.

Because this nand2b does not fan-in to I, Y=1 is an FA/enable-side event —
use it as a timing pin while searching I.

Usage (from rework/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 tools/phase3_watch_nand2b.py
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
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
REPO = ROOT.parent

from run_sim import find_iverilog  # noqa: E402

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
PDK = REPO / "netlist" / "structural" / "pdk"
INC = PDK / "include"
OUT_DIR = HERE
BUILD = ROOT / "phase3" / "build"
CPSAT = REPO / "sim" / "cpsat_exact.json"

N_CYC = 121
# Magic net name for nand2b_2_23/Y
WATCH_Y = "sky130_fd_sc_hd__a32o_2_4__B2"
WATCH_A_N = "sky130_fd_sc_hd__or2_2_11__B"
WATCH_B = "sky130_fd_sc_hd__or2_2_11__A"
# Context pins
WATCH_ENABLE_SIDE = "enable"
WATCH_SUCCESS = "success"
WATCH_A32O = "sky130_fd_sc_hd__a32o_2_4__X"

# FA-ish context from earlier B2 fan-in (optional extras)
EXTRA = [
    ("or4A", "sky130_fd_sc_hd__or4_2_4__A"),
    ("or4B", "sky130_fd_sc_hd__or4_2_4__B"),
    ("or4C", "sky130_fd_sc_hd__or4_2_4__C"),
    ("or4D", "sky130_fd_sc_hd__or4_2_4__D"),
    ("inv7", "sky130_fd_sc_hd__inv_2_7__A"),
    ("xor7A", "sky130_fd_sc_hd__xor2_2_7__A"),
]


def family(cell: str) -> str:
    return re.sub(r"_\d+$", "", cell.replace("sky130_fd_sc_hd__", ""))


def cells_used() -> set[str]:
    text = STRUCT.read_text(encoding="utf-8", errors="replace")
    return {
        c
        for c in re.findall(r"sky130_fd_sc_hd__\w+", text)
        if re.match(r"sky130_fd_sc_hd__\w+_\d+$", c)
    }


def iverilog_cmd(vvp: Path, sources: list[Path]) -> list[str]:
    iv, _ = find_iverilog()
    cmd = [
        str(iv),
        "-g2012",
        "-DFUNCTIONAL",
        "-DUNIT_DELAY=#1",
        "-I",
        str(INC),
        "-o",
        str(vvp),
    ]
    for c in sorted(cells_used()):
        p = PDK / "cells" / family(c) / f"{c}.v"
        if p.exists():
            cmd.append(str(p))
    cmd += [str(s) for s in sources]
    return cmd


def build_patterns() -> list[tuple[str, str]]:
    """Return [(label, bitstring), ...] length N_CYC each."""
    pats = [
        ("all0", "0" * N_CYC),
        ("all1", "1" * N_CYC),
    ]
    if CPSAT.exists():
        ones = set(json.loads(CPSAT.read_text(encoding="utf-8"))["I_ones"])
        val = sum(1 << c for c in ones if 0 <= c < N_CYC)
        pats.append(("cpsat", format(val, f"0{N_CYC}b")))
    return pats


def main() -> None:
    if not STRUCT.exists():
        raise SystemExit(f"missing {STRUCT}")
    if not INC.exists():
        raise SystemExit(f"missing PDK include dir {INC}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    pats = build_patterns()
    pats_path = BUILD / "pats_nand2b_watch.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")

    probes = [
        ("I", "I"),
        ("enable", "enable"),
        ("nand2b_Y", WATCH_Y),
        ("nand2b_A_N", WATCH_A_N),
        ("nand2b_B", WATCH_B),
        ("a32o_X", WATCH_A32O),
        ("success", WATCH_SUCCESS),
    ] + list(EXTRA)
    labels = [p[0] for p in probes]
    n = len(probes)

    dumps = []
    for i, (lab, net) in enumerate(probes):
        if net in ("I", "enable", "success"):
            # ports / top nets
            if net == "I":
                dumps.append(f"        bits[{i}] = I;")
            elif net == "enable":
                dumps.append(f"        bits[{i}] = enable;")
            else:
                dumps.append(f"        bits[{i}] = uut.success;")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_out = BUILD / "probe_nand2b_watch.csv"
    tb = BUILD / "tb_nand2b_watch.v"
    vvp = BUILD / "tb_nand2b_watch.vvp"
    n_pat = len(pats)

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
    fd = $fopen("{csv_out.as_posix()}", "w");
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

    print("compile…", flush=True)
    r = subprocess.run(
        iverilog_cmd(vvp, [STRUCT, tb]), capture_output=True, text=True, timeout=600
    )
    if r.returncode:
        raise SystemExit((r.stderr or r.stdout)[-5000:])
    _, vvp_bin = find_iverilog()
    print("simulate…", flush=True)
    r2 = subprocess.run(
        [str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=600
    )
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    # Post-process: add labels, find Y=1 windows
    rows = list(csv.DictReader(csv_out.open(encoding="utf-8")))
    mode_labels = [p[0] for p in pats]
    for row in rows:
        row["label"] = mode_labels[int(row["mode"])]

    out_csv = OUT_DIR / "watch_nand2b_B2.csv"
    fieldnames = ["label", "mode", "cyc"] + labels
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})

    summary = {
        "watch_net": "a32o_2_4__B2",
        "instance": "nand2b_2_23",
        "formula": "Y = A_N ∨ ¬B",
        "patterns": [],
    }
    md = [
        "# Phase 3 — watch `nand2b_2_23` / `a32o_2_4__B2`",
        "",
        "Pin: **`uut.sky130_fd_sc_hd__a32o_2_4__B2`** (= `nand2b_2_23` Y).",
        "Confirmed independent of `I` (see `nand2b_no_I.md`).",
        "",
        f"CSV: [`watch_nand2b_B2.csv`](watch_nand2b_B2.csv)  ·  cycles 0..{N_CYC-1}",
        "",
    ]

    for mi, (lab, _) in enumerate(pats):
        high = [int(r["cyc"]) for r in rows if int(r["mode"]) == mi and r["nand2b_Y"] == "1"]
        # collapse to runs
        runs = []
        if high:
            s = e = high[0]
            for c in high[1:]:
                if c == e + 1:
                    e = c
                else:
                    runs.append((s, e))
                    s = e = c
            runs.append((s, e))
        # Check independence: all0 vs all1 Y timelines should match if truly I-free
        summary["patterns"].append(
            {
                "label": lab,
                "high_cycles": high,
                "high_count": len(high),
                "runs": [{"start": a, "end": b, "len": b - a + 1} for a, b in runs],
            }
        )
        md.append(f"## Pattern `{lab}`")
        md.append("")
        md.append(f"- Cycles with Y=1: **{len(high)}** / {N_CYC}")
        if runs:
            md.append("- Runs: " + ", ".join(f"`{a}–{b}`" for a, b in runs))
        else:
            md.append("- Runs: _(never high)_")
        md.append("")
        # sample table around first rising edge
        if high:
            c0 = high[0]
            md.append(f"First rise at cyc **{c0}** (context ±2):")
            md.append("")
            md.append("| cyc | I | Y | A_N | B | a32o_X | success | or4 |")
            md.append("|----:|--:|--:|----:|--:|------:|--------:|-----|")
            for r in rows:
                if int(r["mode"]) != mi:
                    continue
                c = int(r["cyc"])
                if abs(c - c0) <= 2:
                    or4 = "".join(r[b] for b in ("or4A", "or4B", "or4C", "or4D"))
                    md.append(
                        f"| {c} | {r['I']} | {r['nand2b_Y']} | {r['nand2b_A_N']} | "
                        f"{r['nand2b_B']} | {r['a32o_X']} | {r['success']} | `{or4}` |"
                    )
            md.append("")

    # Independence check all0 vs all1
    y0 = [r["nand2b_Y"] for r in rows if int(r["mode"]) == 0]
    y1 = [r["nand2b_Y"] for r in rows if int(r["mode"]) == 1]
    indep = y0 == y1
    summary["Y_identical_all0_vs_all1"] = indep
    md += [
        "## I-independence check (sim)",
        "",
        f"all0 vs all1 `nand2b_Y` timelines identical: **{indep}** "
        + ("(expected — no `I` in fan-in)" if indep else "(unexpected — investigate)"),
        "",
    ]

    (OUT_DIR / "watch_nand2b_B2.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT_DIR / "watch_nand2b_B2.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {OUT_DIR / 'watch_nand2b_B2.md'}")
    print(f"I-independence all0==all1 Y: {indep}")
    for p in summary["patterns"]:
        print(f"  {p['label']}: Y=1 on {p['high_count']} cycles  runs={p['runs']}")


if __name__ == "__main__":
    main()
