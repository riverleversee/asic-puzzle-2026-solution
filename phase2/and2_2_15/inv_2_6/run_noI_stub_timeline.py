#!/usr/bin/env python3
"""Timeline: I-independent stubs into a31o_2_11 (and2_2_15 sticky arm).

Watches:
  - inv_2_7__A  = and2b_2_11.Y          → a31o_2_11.A2
  - or2_2_11__A = and2b_2_11.A_N        (collapsed under A2 stub)
  - inv_2_9__A  = and4bb_2_6.X          → a31o_2_11.A1
  - or4_2_4 A/B/C/D                     (and4bb inputs)

Usage (from rework_coded/):
  python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py
"""
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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
from rework_paths import savefig_locked  # noqa: E402

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
PDK = REPO / "netlist" / "structural" / "pdk"
INC = PDK / "include"
BUILD = ROOT / "phase2" / "build"
OUT = HERE / "timelines"
N_CYC = 121
TAG = "and215_noI_stub"

# (csv_label, net, lane_title, color) — stubs first
LANES = [
    (
        "inv7_A",
        "sky130_fd_sc_hd__inv_2_7__A",
        "NO-I  inv_2_7__A  (=and2b.Y → a31o.A2)",
        "#c45911",
    ),
    (
        "inv7_Y",
        "sky130_fd_sc_hd__inv_2_7__Y",
        "NO-I  inv_2_7__Y  (inv of stub A)",
        "#e67e22",
    ),
    (
        "inv9_A",
        "sky130_fd_sc_hd__inv_2_9__A",
        "NO-I  inv_2_9__A  (=and4bb.X → a31o.A1)",
        "#548235",
    ),
    (
        "inv9_Y",
        "sky130_fd_sc_hd__inv_2_9__Y",
        "NO-I  inv_2_9__Y  (inv of stub A)",
        "#70ad47",
    ),
    (
        "and2b_AN",
        "sky130_fd_sc_hd__or2_2_11__A",
        "or2_2_11__A  (and2b.A_N / FA in)",
        "#8d6e63",
    ),
    (
        "or4A",
        "sky130_fd_sc_hd__or4_2_4__A",
        "or4_2_4__A  → and4bb.A_N",
        "#1f4e79",
    ),
    (
        "or4B",
        "sky130_fd_sc_hd__or4_2_4__B",
        "or4_2_4__B  → and4bb.D",
        "#2e75b6",
    ),
    (
        "or4C",
        "sky130_fd_sc_hd__or4_2_4__C",
        "or4_2_4__C  → and4bb.B_N",
        "#5b9bd5",
    ),
    (
        "or4D",
        "sky130_fd_sc_hd__or4_2_4__D",
        "or4_2_4__D  → and4bb.C",
        "#9dc3e6",
    ),
    (
        "a31o_X",
        "sky130_fd_sc_hd__a31o_2_11__X",
        "a31o_2_11__X  (I-reaching observe)",
        "#7030a0",
    ),
]

STUB_LABS = ["inv7_A", "inv7_Y", "inv9_A", "inv9_Y", "and2b_AN", "or4A", "or4B", "or4C", "or4D"]

EXTRA = [
    ("I", "I"),
    ("enable", "enable"),
    ("sticky_Q", "sky130_fd_sc_hd__inv_2_6__A"),
    ("mux_X", "sky130_fd_sc_hd__mux2_1_7__X"),
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


def ones(rows: list[dict], key: str) -> list[int]:
    return [int(r["cyc"]) for r in rows if int(r[key])]


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    probes = list(EXTRA) + [(lab, net) for lab, net, _t, _c in LANES]
    labels = [p[0] for p in probes]
    n = len(probes)

    pats = BUILD / f"pats_{TAG}.txt"
    pats.write_text(("0" * N_CYC) + "\n" + ("1" * N_CYC) + "\n", encoding="utf-8")
    n_pat = 2
    pat_names = ["all0", "all1"]

    dumps = []
    for i, (_lab, net) in enumerate(probes):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / f"probe_{TAG}.csv"
    tb = BUILD / f"tb_{TAG}.v"
    vvp = BUILD / f"tb_{TAG}.vvp"
    tb.write_text(
        f"""`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O; wire success;
  reg [{N_CYC-1}:0] pat [0:{n_pat-1}];
  reg [{n-1}:0] bits;
  integer mode, cyc, fd, i;
  puzzle uut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),
    .O_0(O[0]),.O_1(O[1]),.O_2(O[2]),.O_3(O[3]),
    .O_4(O[4]),.O_5(O[5]),.O_6(O[6]),.O_7(O[7]),.success(success));
  always #5 clk = ~clk;
  initial begin
    $readmemb("{pats.as_posix()}", pat);
    fd = $fopen("{csv_raw.as_posix()}", "w");
    $fwrite(fd, "mode,cyc,{','.join(labels)}\\n");
    for (mode=0; mode<{n_pat}; mode=mode+1) begin
      rst_n=0; enable=0; I=0;
      repeat(3) @(posedge clk);
      rst_n=1; @(posedge clk);
      enable=1;
      for (cyc=0; cyc<{N_CYC}; cyc=cyc+1) begin
        @(negedge clk); I = pat[mode][cyc];
        @(posedge clk); #1;
{chr(10).join(dumps)}
        $fwrite(fd, "%0d,%0d", mode, cyc);
        for (i=0; i<{n}; i=i+1) $fwrite(fd, ",%0d", bits[i]);
        $fwrite(fd, "\\n");
      end
    end
    $fclose(fd); $finish;
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
        raise SystemExit((r.stderr or r.stdout)[-4000:])
    _, vvp_bin = find_iverilog()
    print("simulate all0+all1…", flush=True)
    r2 = subprocess.run([str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=600)
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    all_rows = list(csv.DictReader(csv_raw.open(encoding="utf-8")))
    by_mode = {
        name: [r for r in all_rows if int(r["mode"]) == mi]
        for mi, name in enumerate(pat_names)
    }
    rows0 = by_mode["all0"]
    rows1 = by_mode["all1"]

    stub_labs = list(STUB_LABS)
    out_csv = OUT / "noI_stub_timeline_all0.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["cyc"] + [lab for lab, *_ in LANES] + ["sticky_Q", "mux_X"],
        )
        w.writeheader()
        for r in rows0:
            w.writerow({k: r[k] for k in w.fieldnames})

    lane_ones = {lab: ones(rows0, lab) for lab, *_ in LANES}
    indep = True
    for lab in stub_labs:
        s0 = [int(r[lab]) for r in rows0]
        s1 = [int(r[lab]) for r in rows1]
        if s0 != s1:
            indep = False
            print(f"  WARN {lab} differs all0 vs all1")
    a31_differs = [int(r["a31o_X"]) for r in rows0] != [int(r["a31o_X"]) for r in rows1]
    mux_differs = [int(r["mux_X"]) for r in rows0] != [int(r["mux_X"]) for r in rows1]

    # Focus figure: inv_2_7 / inv_2_9 only (what only-I stubs at a31o)
    stub_focus = [L for L in LANES if L[0] in ("inv7_A", "inv7_Y", "inv9_A", "inv9_Y")]
    fig, axes = plt.subplots(2, 1, figsize=(14, 6.2), dpi=140, gridspec_kw={"height_ratios": [1.1, 1.6]})
    ax0, ax = axes
    for yi, (lab, _net, title, col) in enumerate(reversed(stub_focus)):
        for c in lane_ones[lab]:
            ax0.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
    ax0.set_yticks(range(len(stub_focus)))
    ax0.set_yticklabels([t for _a, _n, t, _c in reversed(stub_focus)], fontsize=8, family="monospace")
    ax0.set_xlim(-0.5, N_CYC - 0.5)
    ax0.set_title(
        "NO-I stubs at a31o · inv_2_7 / inv_2_9 (A + Y) · all0  [identical on all1]",
        fontsize=11,
    )
    ax0.grid(axis="x", color="#eee", lw=0.5)

    for yi, (lab, _net, title, col) in enumerate(reversed(LANES)):
        for c in lane_ones[lab]:
            ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
    ax.set_yticks(range(len(LANES)))
    ax.set_yticklabels([t for _a, _n, t, _c in reversed(LANES)], fontsize=7, family="monospace")
    ax.set_xlim(-0.5, N_CYC - 0.5)
    ax.set_xlabel("cycle (all0 · enable=1 after reset)")
    ax.set_title("Full stub context (or4 / and2b.A_N / a31o.X observe)", fontsize=10)
    ax.grid(axis="x", color="#eee", lw=0.5)
    ax.legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in LANES],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=5,
        frameon=False,
        fontsize=7,
    )
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "noI_stub_timeline.png")

    def fmt(xs: list[int], lim: int = 24) -> str:
        if len(xs) <= lim:
            return str(xs)
        return str(xs[:lim])[:-1] + f", …]  (n={len(xs)})"

    md = [
        "# I-independent stub timelines — `inv_2_7` / `inv_2_9` (a31o A-arm)",
        "",
        "Structural sim · **all0** (checked identical vs **all1** for stub lanes).",
        "",
        "## Primary NO-I nets (required)",
        "",
        "| Net | Role | high cycles (all0) |",
        "|-----|------|--------------------|",
        f"| `inv_2_7__A` | a31o.A2 = and2b_2_11.Y | `{fmt(lane_ones['inv7_A'])}` |",
        f"| `inv_2_7__Y` | inv of stub A | `{fmt(lane_ones['inv7_Y'])}` |",
        f"| `inv_2_9__A` | a31o.A1 = and4bb_2_6.X | `{fmt(lane_ones['inv9_A'])}` |",
        f"| `inv_2_9__Y` | inv of stub A | `{fmt(lane_ones['inv9_Y'])}` |",
        "",
        f"**Stub lanes all0 ≡ all1:** `{indep}`",
        "",
        "```text",
        "a31o_2_11:",
        "  A1 = inv_2_9__A  ← and4bb_2_6.X   # NO-I stub (FA)",
        "  A2 = inv_2_7__A  ← and2b_2_11.Y   # NO-I stub (FA)",
        "  A3 = mux2_1_7__X                 # →I",
        "  B1 = inv_2_6__A                  # sticky Q",
        "```",
        "",
        f"- `a31o_2_11.X` differs all0 vs all1: **{a31_differs}**",
        f"- `mux2_1_7.X` differs all0 vs all1: **{mux_differs}**",
        "",
        "## Context (FA priors / observe)",
        "",
        f"- `or2_2_11__A` (and2b.A_N) high @ `{fmt(lane_ones['and2b_AN'])}`",
        f"- `or4_2_4__A` high @ `{fmt(lane_ones['or4A'])}`",
        f"- `or4_2_4__B` high @ `{fmt(lane_ones['or4B'])}`",
        f"- `or4_2_4__C` high @ `{fmt(lane_ones['or4C'])}`",
        f"- `or4_2_4__D` high @ `{fmt(lane_ones['or4D'])}`",
        f"- `a31o_2_11__X` high @ `{fmt(lane_ones['a31o_X'])}`",
        "",
        f"Figure: [`{png.name}`]({png.name}) — top panel = inv_2_7/9 only",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "I=1 probes (separate): [`I1_probe_timeline.md`](I1_probe_timeline.md)",
        "",
        "Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "noI_stub_timeline.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    print(f"wrote {md_path}")
    print(f"wrote {png}")
    print(f"wrote {out_csv}")
    print(f"I-indep stubs all0==all1: {indep}")
    print(f"a31o_X differs all0/all1: {a31_differs}")
    print(f"mux_X differs all0/all1: {mux_differs}")
    for lab, _n, title, _c in LANES:
        print(f"  {lab}: n={len(lane_ones[lab])}  {title}")


if __name__ == "__main__":
    main()
