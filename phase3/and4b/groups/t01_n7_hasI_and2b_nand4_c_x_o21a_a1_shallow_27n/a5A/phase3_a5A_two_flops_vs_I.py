#!/usr/bin/env python3
"""Show dfrtp_2_80 (A_N) and dfrtp_2_66 (B) D/Q vs I on a5.A opens (k2/k3)."""
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
BUILD = ROOT / "phase3" / "build"
OUT = HERE / "a5A_two_flops_vs_I.md"
N = 55
OPENS = [5, 16, 27, 38, 49]

PROBES = [
    ("I", "I"),
    ("openD", "sky130_fd_sc_hd__nand4_2_9__D"),
    ("AN_D", "sky130_fd_sc_hd__o21a_2_21__X"),  # dfrtp_2_80.D
    ("AN_Q", "sky130_fd_sc_hd__nand4_2_9__C"),  # dfrtp_2_80.Q = A_N
    ("B_D", "sky130_fd_sc_hd__dfrtp_2_66__D"),  # dfrtp_2_66.D
    ("B_Q", "sky130_fd_sc_hd__o21a_2_21__A1"),  # dfrtp_2_66.Q = B
    ("Y", "sky130_fd_sc_hd__and4_2_5__A"),
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


def bits(ones: set[int]) -> str:
    val = sum(1 << c for c in ones if 0 <= c < N)
    return format(val, f"0{N}b")


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pats = [
        ("k2", bits({5, 16})),
        ("k3", bits({5, 16, 27})),
        ("k4", bits({5, 16, 27, 38})),
    ]
    pats_path = BUILD / "pats_ff2.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")
    n_pat = len(pats)

    labs = [p[0] for p in PROBES]
    n = len(PROBES)
    dumps = []
    for i, (_lab, net) in enumerate(PROBES):
        src = "I" if net == "I" else f"uut.{net}"
        dumps.append(f"        bits[{i}] = {src};")

    raw = BUILD / "probe_ff2.csv"
    tb = BUILD / "tb_ff2.v"
    vvp = BUILD / "tb_ff2.vvp"
    tb.write_text(
        f"""`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O; wire success;
  reg [{N-1}:0] pat [0:{n_pat-1}];
  reg [{n-1}:0] bits;
  integer mode, cyc, fd, i;
  puzzle uut(
    .clk(clk), .rst_n(rst_n), .enable(enable), .I(I),
    .O_0(O[0]), .O_1(O[1]), .O_2(O[2]), .O_3(O[3]),
    .O_4(O[4]), .O_5(O[5]), .O_6(O[6]), .O_7(O[7]), .success(success)
  );
  always #5 clk = ~clk;
  initial begin
    $readmemb("{pats_path.as_posix()}", pat);
    fd = $fopen("{raw.as_posix()}", "w");
    $fwrite(fd, "mode,cyc,{','.join(labs)}\\n");
    for (mode=0; mode<{n_pat}; mode=mode+1) begin
      rst_n=0; enable=0; I=0;
      repeat(3) @(posedge clk);
      rst_n=1; @(posedge clk);
      enable=1;
      for (cyc=0; cyc<{N}; cyc=cyc+1) begin
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

    iv, vvp_bin = find_iverilog()
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
    cmd += [str(STRUCT), str(tb)]
    print("compile…", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise SystemExit((r.stderr or r.stdout)[-4000:])
    print("simulate…", flush=True)
    r2 = subprocess.run(
        [str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=600
    )
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    rows = list(csv.DictReader(raw.open(encoding="utf-8")))
    for row in rows:
        row["lab"] = pats[int(row["mode"])][0]

    lines = [
        "# Two and2b input flops vs I",
        "",
        "Labels match the depth-5 figure "
        "`and4b_main_groups/t01_…/and2b_2_25_out_and4_2_5__A_d5.png`.",
        "",
        "## Map: figure node → and2b_2_25 pin",
        "",
        "| Figure label (d) | Role | Cell | and2b pin? |",
        "|---------------|------|------|:----------:|",
        "| `nand4_2_9__C` (d=1, flop) | Q of `dfrtp_2_80` | flop | **yes — A_N** |",
        "| `o21a_2_21__A1` (d=1, flop) | Q of `dfrtp_2_66` | flop | **yes — B** |",
        "| `and4_2_5__A` (d=0) | out of `and2b_2_25` | **and2b** | **yes — X / Y** |",
        "| `o21a_2_21__X` (d=2) | D into `dfrtp_2_80` | o21a | no (AN.D) |",
        "| `dfrtp_2_66__D` / nand2b (d=2) | D into `dfrtp_2_66` | nand2b | no (B.D) |",
        "| `nand4_2_9__D` (d=4) | a5.A open decode | and4bb | no |",
        "",
        "```text",
        "and2b_2_25:",
        "  A_N ← nand4_2_9__C     (figure flop @ d=1)",
        "  B   ← o21a_2_21__A1    (figure flop @ d=1)",
        "  X/Y → and4_2_5__A      (figure and2b @ d=0)",
        "  Y = (¬A_N) ∧ B",
        "```",
        "",
        "a5.A opens ★ @ `5,16,27,38,…`. Sampled after each posedge.",
        "",
    ]
    pat_ones = {"k2": {5, 16}, "k3": {5, 16, 27}, "k4": {5, 16, 27, 38}}
    open_marks = {5, 16, 27, 38}
    for lab, ones in pat_ones.items():
        lines += [
            f"## `{lab}` — I=1 @ {sorted(ones)}",
            "",
            "| cyc | I | `nand4_2_9__D` | →D `o21a_2_21__X` | "
            "**`nand4_2_9__C` = and2b.A_N** | →D `dfrtp_2_66__D` | "
            "**`o21a_2_21__A1` = and2b.B** | **`and4_2_5__A` = and2b.Y** |",
            "|----:|--:|---------------:|-----------------:|"
            "-------------------------------:|------------------:|"
            "-------------------------------:|---------------------------------:|",
        ]
        for r in rows:
            if r["lab"] != lab:
                continue
            c = int(r["cyc"])
            if c > 45:
                continue
            star = " ★" if c in open_marks else ""
            lines.append(
                f"| {c}{star} | {r['I']} | {r['openD']} | {r['AN_D']} | "
                f"**{r['AN_Q']}** | {r['B_D']} | **{r['B_Q']}** | **{r['Y']}** |"
            )
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    print("\nfigure labels → and2b pins:")
    print("  nand4_2_9__C  = and2b.A_N  (flop dfrtp_2_80)")
    print("  o21a_2_21__A1 = and2b.B    (flop dfrtp_2_66)")
    print("  and4_2_5__A   = and2b.Y/X  (and2b_2_25 comb out)")
    print("\ncyc  k2:I A_N B Y   k3:I A_N B Y   k4:I A_N B Y")
    for c in range(4, 45):
        a = next(r for r in rows if r["lab"] == "k2" and int(r["cyc"]) == c)
        b = next(r for r in rows if r["lab"] == "k3" and int(r["cyc"]) == c)
        d = next(r for r in rows if r["lab"] == "k4" and int(r["cyc"]) == c)
        m = "★" if c in open_marks else " "
        print(
            f"{c:>3}{m}  {a['I']} {a['AN_Q']} {a['B_Q']} {a['Y']}    "
            f"{b['I']} {b['AN_Q']} {b['B_Q']} {b['Y']}    "
            f"{d['I']} {d['AN_Q']} {d['B_Q']} {d['Y']}"
        )


if __name__ == "__main__":
    main()
