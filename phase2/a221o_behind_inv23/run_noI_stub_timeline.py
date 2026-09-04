#!/usr/bin/env python3
"""Timeline: I-independent stubs into a31o / a221o / a22o (all0).

Watches:
  - and2b_2_11.Y = inv_2_7__A          → a31o_2_12.A2
  - or4bb_2_0.X                        → a221o_2_1.A1
  - or4_2_4.X                          → a22o_2_2.A1
  - buf_2_0.X  (= or4_2_4.X buffered)  → a22o_2_2.B1

Usage (from rework_coded/):
  python3 phase2/a221o_behind_inv23/run_noI_stub_timeline.py
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

# (csv_label, net, lane_title, color)
LANES = [
    (
        "and2b_Y",
        "sky130_fd_sc_hd__inv_2_7__A",
        "inv_2_7__A  (and2b_2_11.Y) → a31o.A2",
        "#c45911",
    ),
    (
        "and2b_AN",
        "sky130_fd_sc_hd__or2_2_11__A",
        "or2_2_11__A  (and2b_2_11.A_N / FA in)",
        "#8d6e63",
    ),
    (
        "or4bb",
        "sky130_fd_sc_hd__or4bb_2_0__X",
        "or4bb_2_0__X  → a221o.A1",
        "#548235",
    ),
    (
        "a22o_A1",
        "sky130_fd_sc_hd__or4_2_4__X",
        "or4_2_4__X  → a22o.A1",
        "#1f4e79",
    ),
    (
        "a22o_B1",
        "sky130_fd_sc_hd__buf_2_0__X",
        "buf_2_0__X  → a22o.B1  (=or4.X)",
        "#2e75b6",
    ),
    (
        "a22o_X",
        "sky130_fd_sc_hd__a22o_2_2__X",
        "a22o_2_2__X  → a221o.C1",
        "#7030a0",
    ),
]

EXTRA = [
    ("I", "I"),
    ("enable", "enable"),
    ("or4A", "sky130_fd_sc_hd__or4_2_4__A"),
    ("or4B", "sky130_fd_sc_hd__or4_2_4__B"),
    ("or4C", "sky130_fd_sc_hd__or4_2_4__C"),
    ("or4D", "sky130_fd_sc_hd__or4_2_4__D"),
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

    pats = BUILD / "pats_noI_stub_timeline.txt"
    # all0 + all1 — confirm I-independence of these stubs
    pats.write_text(("0" * N_CYC) + "\n" + ("1" * N_CYC) + "\n", encoding="utf-8")
    n_pat = 2
    pat_names = ["all0", "all1"]

    dumps = []
    for i, (_lab, net) in enumerate(probes):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_noI_stub_timeline.csv"
    tb = BUILD / "tb_noI_stub_timeline.v"
    vvp = BUILD / "tb_noI_stub_timeline.vvp"
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

    # Copy slim CSV of all0 into timelines/
    out_csv = OUT / "noI_stub_timeline_all0.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["cyc"] + [lab for lab, *_ in LANES] + ["or4A", "or4B", "or4C", "or4D"],
        )
        w.writeheader()
        for r in rows0:
            w.writerow({k: r[k] for k in w.fieldnames})

    lane_ones = {lab: ones(rows0, lab) for lab, *_ in LANES}
    stub_labs = ["and2b_Y", "and2b_AN", "or4bb", "a22o_A1", "a22o_B1"]
    indep = True
    for lab in stub_labs:
        s0 = [int(r[lab]) for r in rows0]
        s1 = [int(r[lab]) for r in rows1]
        if s0 != s1:
            indep = False
            print(f"  WARN {lab} differs all0 vs all1")
    a22o_differs = [int(r["a22o_X"]) for r in rows0] != [int(r["a22o_X"]) for r in rows1]

    a1_eq_b1 = [int(r["a22o_A1"]) for r in rows0] == [int(r["a22o_B1"]) for r in rows0]

    # Figure — all0 bar lanes
    fig, ax = plt.subplots(figsize=(14, 4.6), dpi=140)
    for yi, (lab, _net, title, col) in enumerate(reversed(LANES)):
        for c in lane_ones[lab]:
            ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
    ax.set_yticks(range(len(LANES)))
    ax.set_yticklabels([t for _a, _n, t, _c in reversed(LANES)], fontsize=8, family="monospace")
    ax.set_xlim(-0.5, N_CYC - 0.5)
    ax.set_xlabel("cycle (all0 · enable=1 after reset)")
    ax.set_title(
        "I-independent stubs into a31o / a221o / a22o  ·  all0\n"
        "inv_2_7__A / or2_2_11__A (and2b) · or4bb · or4.X / buf"
    )
    ax.grid(axis="x", color="#eee", lw=0.5)
    ax.legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in LANES],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=3,
        frameon=False,
        fontsize=8,
    )
    fig.tight_layout()
    png = savefig_locked(fig, OUT / "noI_stub_timeline.png")

    def fmt(xs: list[int], lim: int = 24) -> str:
        if len(xs) <= lim:
            return str(xs)
        return str(xs[:lim])[:-1] + f", …]  (n={len(xs)})"

    md = [
        "# I-independent stub timelines (a31o / a221o / a22o)",
        "",
        "Structural sim · stimulus **all0** (also checked vs **all1**).",
        "",
        "```text",
        "and2b_2_11:",
        "  A_N = or2_2_11__A   ← dfrtp_2_47.Q  (FA-side flop; I-independent)",
        "  B   = enable",
        "  Y   = inv_2_7__A    → a31o_2_12.A2",
        "",
        "a221o_2_1.A1  ←  or4bb_2_0__X",
        "a22o_2_2.A1   ←  or4_2_4__X",
        "a22o_2_2.B1   ←  buf_2_0__X   (= or4_2_4__X buffered)",
        "a221o_2_1.C1  ←  a22o_2_2__X",
        "```",
        "",
        "Name aliases (same net, different labels elsewhere):",
        "",
        "| Canonical net | Also called |",
        "|---------------|-------------|",
        "| `inv_2_7__A` | `and2b_2_11.Y` |",
        "| `or2_2_11__A` | `and2b_2_11.A_N`, `dfrtp_2_47.Q` |",
        "| `or4_2_4__X` | `a22o_2_2.A1`, `buf_2_0.A` |",
        "| `buf_2_0__X` | `a22o_2_2.B1` (= `or4_2_4__X`) |",
        "",
        "Fan-in figures stub at `inv_2_7__A` (only-I), so `or2_2_11__A` is **not drawn** there —",
        "it is the collapsed `A_N` under that stub (annotated on the box).",
        "",
        f"- stub lanes identical all0 vs all1 (and2b.Y/A_N, or4bb, or4.X, buf): **{indep}**",
        f"- `or4_2_4.X` == `buf_2_0.X` on all0: **{a1_eq_b1}**",
        f"- `a22o_2_2.X` differs all0 vs all1 (I-reaching A2/B2 arms): **{a22o_differs}**",
        "",
        "Note: under all0, `and2b.A_N` stays 0 so `and2b.Y = enable` (high every cycle after enable).",
        "",
        "## Ones (all0)",
        "",
        f"- `inv_2_7__A` (and2b_2_11.Y) high @ `{fmt(lane_ones['and2b_Y'])}`",
        f"- `or2_2_11__A` (and2b_2_11.A_N) high @ `{fmt(lane_ones['and2b_AN'])}`",
        f"- `or4bb_2_0__X` high @ `{fmt(lane_ones['or4bb'])}`",
        f"- `or4_2_4__X` (a22o.A1) high @ `{fmt(lane_ones['a22o_A1'])}`",
        f"- `buf_2_0__X` (a22o.B1) high @ `{fmt(lane_ones['a22o_B1'])}`",
        f"- `a22o_2_2__X` high @ `{fmt(lane_ones['a22o_X'])}`",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "Regenerate:",
        "```bash",
        "python3 phase2/a221o_behind_inv23/run_noI_stub_timeline.py",
        "```",
        "",
    ]
    md_path = OUT / "noI_stub_timeline.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    print(f"wrote {md_path}")
    print(f"wrote {png}")
    print(f"wrote {out_csv}")
    print(f"I-indep stubs all0==all1: {indep}")
    print(f"A1==B1 (or4.X==buf): {a1_eq_b1}")
    print(f"a22o_X differs all0/all1: {a22o_differs}")
    for lab, _n, title, _c in LANES:
        print(f"  {lab}: n={len(lane_ones[lab])}  {title}")


if __name__ == "__main__":
    main()
