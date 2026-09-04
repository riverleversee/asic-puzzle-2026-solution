#!/usr/bin/env python3
"""Sim all0: watch FA-side input or2_2_11__A (into and2b→nand2.B), not the output."""
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt

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
from run_sim import find_iverilog
from rework_paths import savefig_locked

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
PDK = REPO / "netlist" / "structural" / "pdk"
INC = PDK / "include"
BUILD = ROOT / "phase3" / "build"
OUT = HERE
N_CYC = 121


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
    cmd = [str(iv), "-g2012", "-DFUNCTIONAL", "-DUNIT_DELAY=#1", "-I", str(INC), "-o", str(vvp)]
    for c in sorted(cells_used()):
        p = PDK / "cells" / family(c) / f"{c}.v"
        if p.exists():
            cmd.append(str(p))
    cmd += [str(s) for s in sources]
    return cmd


probes = [
    ("I", "I"),
    ("enable", "enable"),
    # nand2.B = inv_2_7__A = and2b_2_11 Y  (predictable under all0)
    ("nand_B", "sky130_fd_sc_hd__inv_2_7__A"),
    # FA-side INPUT into that and2b (A_N)
    ("fa_A_N", "sky130_fd_sc_hd__or2_2_11__A"),
    # FA phase decode that feeds the flop D behind or2_2_11__A
    ("fa_phase", "sky130_fd_sc_hd__inv_2_9__A"),  # and4bb of or4_2_4
    ("or4A", "sky130_fd_sc_hd__or4_2_4__A"),
    ("or4B", "sky130_fd_sc_hd__or4_2_4__B"),
    ("or4C", "sky130_fd_sc_hd__or4_2_4__C"),
    ("or4D", "sky130_fd_sc_hd__or4_2_4__D"),
]

BUILD.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
pats = BUILD / "pats_fa_nand_in.txt"
pats.write_text("0" * N_CYC + "\n", encoding="utf-8")
labels = [p[0] for p in probes]
n = len(probes)
dumps = []
for i, (_l, net) in enumerate(probes):
    dumps.append(f"        bits[{i}] = {net if net in ('I','enable') else 'uut.'+net};")

csv_raw = BUILD / "probe_fa_nand_in.csv"
tb = BUILD / "tb_fa_nand_in.v"
vvp = BUILD / "tb_fa_nand_in.vvp"
tb.write_text(
    f"""`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O; wire success;
  reg [{N_CYC-1}:0] pat [0:0];
  reg [{n-1}:0] bits;
  integer mode, cyc, fd, i;
  puzzle uut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),
    .O_0(O[0]),.O_1(O[1]),.O_2(O[2]),.O_3(O[3]),
    .O_4(O[4]),.O_5(O[5]),.O_6(O[6]),.O_7(O[7]),.success(success));
  always #5 clk = ~clk;
  initial begin
    $readmemb("{pats.as_posix()}", pat);
    fd = $fopen("{csv_raw.as_posix()}", "w");
    $fwrite(fd, "cyc,{','.join(labels)}\\n");
    rst_n=0; enable=0; I=0;
    repeat(3) @(posedge clk);
    rst_n=1; @(posedge clk);
    enable=1;
    for (cyc=0; cyc<{N_CYC}; cyc=cyc+1) begin
      @(negedge clk); I = pat[0][cyc];
      @(posedge clk); #1;
{chr(10).join(dumps)}
      $fwrite(fd, "%0d", cyc);
      for (i=0; i<{n}; i=i+1) $fwrite(fd, ",%0d", bits[i]);
      $fwrite(fd, "\\n");
    end
    $fclose(fd); $finish;
  end
endmodule
""",
    encoding="utf-8",
)

print("compile…", flush=True)
r = subprocess.run(iverilog_cmd(vvp, [STRUCT, tb]), capture_output=True, text=True, timeout=600)
if r.returncode:
    raise SystemExit((r.stderr or r.stdout)[-4000:])
_, vvp_bin = find_iverilog()
print("simulate…", flush=True)
r2 = subprocess.run([str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=600)
if r2.returncode:
    raise SystemExit((r2.stdout + r2.stderr)[-4000:])

rows = list(csv.DictReader(csv_raw.open(encoding="utf-8")))


def ones(key: str) -> list[int]:
    return [int(r["cyc"]) for r in rows if int(r[key])]


fa_an = ones("fa_A_N")
nand_b = ones("nand_B")
fa_ph = ones("fa_phase")
md = [
    "# FA input into nand2(I, ·) — not the nand B output",
    "",
    "The nand2 that drives each sticky_or `or4.D` is:",
    "",
    "```text",
    "nand2.Y = ~( nand2.A  ∧  nand2.B )",
    "        = ~( I        ∧  inv_2_7__A )",
    "```",
    "",
    "`inv_2_7__A` is **not** a raw FA bit — it is `and2b_2_11` output:",
    "",
    "```text",
    "inv_2_7__A = enable ∧ ¬or2_2_11__A",
    "```",
    "",
    "**FA-side input** (the one that can kill the nand B arm) = `or2_2_11__A`",
    "(flop `dfrtp_2_47` Q). Its D fan-in reaches FA phase `or4_2_4` via `inv_2_9__A`",
    "(`and4bb_2_6` of `or4_2_4`).",
    "",
    "Stimulus: **all0**.",
    "",
    f"- `or2_2_11__A` (FA input) high @ `{fa_an}`  (n={len(fa_an)})",
    f"- `inv_2_7__A` (nand B, enable∧¬FA_in) high n={len(nand_b)}",
    f"- `inv_2_9__A` (FA phase and4bb) high @ `{fa_ph}`  (n={len(fa_ph)})",
    "",
    "Figure: [`fa_input_to_nand2_timeline.png`](fa_input_to_nand2_timeline.png)",
    "",
]
(OUT / "fa_input_to_nand2.md").write_text("\n".join(md), encoding="utf-8")

# timeline
fig, ax = plt.subplots(figsize=(14, 3.2), dpi=140)
lanes = [
    ("or2_2_11__A  (FA input / and2b A_N)", fa_an, "#1b5e20"),
    ("inv_2_7__A   (nand2.B = en ∧ ¬A_N)", nand_b, "#757575"),
    ("inv_2_9__A   (and4bb or4_2_4)", fa_ph, "#0d47a1"),
]
for yi, (lab, cycs, col) in enumerate(reversed(lanes)):
    for c in cycs:
        ax.barh(yi, 1.0, left=c - 0.5, height=0.7, color=col, edgecolor="none")
ax.set_yticks(range(len(lanes)))
ax.set_yticklabels([l[0] for l in reversed(lanes)], fontsize=8, family="monospace")
ax.set_xlim(-0.5, N_CYC - 0.5)
ax.set_xlabel("cycle (all0)")
ax.set_title("FA input into nand2 path vs predictable nand B")
ax.grid(axis="x", color="#eee", lw=0.5)
fig.tight_layout()
png = OUT / "fa_input_to_nand2_timeline.png"
png = savefig_locked(fig, png)
print(f"wrote {OUT / 'fa_input_to_nand2.md'}")
print(f"wrote {png}")
print("fa_A_N ones:", fa_an)
print("nand_B n:", len(nand_b))
print("fa_phase ones:", fa_ph)
