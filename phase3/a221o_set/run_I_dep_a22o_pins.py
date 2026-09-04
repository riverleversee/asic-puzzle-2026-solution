#!/usr/bin/env python3
"""I-dependence of a22o_2_2 pins A2 / B2 — single 1 and two ones.

Stimulus:
  - all0 baseline
  - k1: I=1 on exactly one cycle (starts 0..10)
  - k2: I=1 on two consecutive cycles (starts 0..10)

Watches a22o.A2 / B2 and a22o.X vs all0.

Usage (from rework_coded/):
  python3 phase3/a221o_set/run_I_dep_a22o_pins.py
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
BUILD = ROOT / "phase3" / "build"
OUT = HERE / "I_dep"
N_CYC = 121
STARTS = list(range(0, 11))
# Drop final cycle from ≠all0 scoring — end-of-window diffs (e.g. @120) are not informative.
COMPARE_CYC = N_CYC - 1  # score cycles 0 .. COMPARE_CYC-1

PROBES = [
    ("I", "I"),
    ("enable", "enable"),
    ("A2", "sky130_fd_sc_hd__a22o_2_2__A2"),
    ("B2", "sky130_fd_sc_hd__a22o_2_2__B2"),
    ("a22o", "sky130_fd_sc_hd__a22o_2_2__X"),
    # flop D muxes + shared S
    ("D_A2", "sky130_fd_sc_hd__mux2_1_13__X"),
    ("D_B2", "sky130_fd_sc_hd__mux2_1_11__X"),
    ("S_and2b", "sky130_fd_sc_hd__inv_2_7__A"),
]
WATCH = ("A2", "B2", "a22o")


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


def bits_from_ones(ones: set[int]) -> str:
    # $readmemb left char = MSB = pat[N_CYC-1]; pat[cyc] needs bit cyc set.
    val = sum(1 << c for c in ones if 0 <= c < N_CYC)
    return format(val, f"0{N_CYC}b")


def series(rows: list[dict], key: str) -> list[int]:
    return [int(r[key]) for r in rows]


def diff_cycles(base: list[int], other: list[int]) -> list[int]:
    return [
        i
        for i, (a, b) in enumerate(zip(base, other))
        if a != b and i < COMPARE_CYC
    ]


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    pats: list[tuple[str, str]] = [("all0", "0" * N_CYC)]
    for s in STARTS:
        pats.append((f"k1_s{s}", bits_from_ones({s})))
    for s in STARTS:
        pats.append((f"k2_s{s}", bits_from_ones({s, s + 1})))

    pats_path = BUILD / "pats_I_dep_a22o.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")

    labels = [p[0] for p in PROBES]
    n = len(PROBES)
    n_pat = len(pats)
    dumps = []
    for i, (_lab, net) in enumerate(PROBES):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_I_dep_a22o.csv"
    tb = BUILD / "tb_I_dep_a22o.v"
    vvp = BUILD / "tb_I_dep_a22o.vvp"
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
    $readmemb("{pats_path.as_posix()}", pat);
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

    print(f"compile… ({n_pat} patterns)", flush=True)
    r = subprocess.run(
        iverilog_cmd(vvp, [STRUCT, tb]), capture_output=True, text=True, timeout=600
    )
    if r.returncode:
        raise SystemExit((r.stderr or r.stdout)[-4000:])
    _, vvp_bin = find_iverilog()
    print("simulate…", flush=True)
    r2 = subprocess.run([str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=600)
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    raw = list(csv.DictReader(csv_raw.open(encoding="utf-8")))
    mode_labels = [p[0] for p in pats]
    by_mode: dict[str, list[dict]] = {lab: [] for lab, _ in pats}
    for row in raw:
        by_mode[mode_labels[int(row["mode"])]].append(row)

    base = by_mode["all0"]
    base_s = {k: series(base, k) for k in (*WATCH, "D_A2", "D_B2", "S_and2b")}

    rows_out = []
    for lab, _bits in pats:
        if lab == "all0":
            continue
        rows = by_mode[lab]
        entry: dict = {"pattern": lab}
        for k in WATCH:
            dcy = diff_cycles(base_s[k], series(rows, k))
            entry[f"{k}_ndiff"] = len(dcy)
            entry[f"{k}_first"] = dcy[0] if dcy else None
            entry[f"{k}_diffs"] = dcy[:24]
        for k in ("D_A2", "D_B2"):
            dcy = diff_cycles(base_s[k], series(rows, k))
            entry[f"{k}_ndiff"] = len(dcy)
            entry[f"{k}_first"] = dcy[0] if dcy else None
        rows_out.append(entry)

    def block(prefix: str) -> list[dict]:
        return [e for e in rows_out if e["pattern"].startswith(prefix)]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=140)
    pins = list(WATCH)
    for ax, prefix, title in (
        (axes[0], "k1_s", "k=1 — pin ≠ all0"),
        (axes[1], "k2_s", "k=2 — pin ≠ all0"),
    ):
        mat = []
        ylabs = []
        for s in STARTS:
            e = next(x for x in rows_out if x["pattern"] == f"{prefix}{s}")
            mat.append([1 if e[f"{p}_ndiff"] else 0 for p in pins])
            ylabs.append(f"s={s}")
        ax.imshow(mat, aspect="auto", cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(len(pins)))
        ax.set_xticklabels(pins)
        ax.set_yticks(range(len(ylabs)))
        ax.set_yticklabels(ylabs, fontsize=8)
        ax.set_title(title, fontsize=10)
        for i, row in enumerate(mat):
            for j, v in enumerate(row):
                if v:
                    e = next(x for x in rows_out if x["pattern"] == f"{prefix}{STARTS[i]}")
                    ax.text(
                        j,
                        i,
                        str(e[f"{pins[j]}_ndiff"]),
                        ha="center",
                        va="center",
                        fontsize=7,
                        color="white",
                    )
    fig.suptitle(
        "I-dependence of a22o_2_2 A2/B2 · #cycles ≠ all0",
        fontsize=11,
    )
    fig.tight_layout()
    heat = savefig_locked(fig, OUT / "I_dep_a22o_k1_k2_heatmap.png")

    def fmt_diffs(e: dict, pin: str) -> str:
        n = e[f"{pin}_ndiff"]
        if not n:
            return "—"
        first = e[f"{pin}_first"]
        sample = e[f"{pin}_diffs"]
        more = "" if n <= len(sample) else "…"
        return f"n={n} first@{first} {sample}{more}"

    md = [
        "# I-dependence — a22o_2_2 A2 / B2",
        "",
        "Structural sim. Baseline **all0**; then **k=1** (single `I=1`) and **k=2**",
        "(two consecutive ones), start cycle `s=0..10`.",
        "",
        f"Diff scoring uses cycles `0..{COMPARE_CYC - 1}` only (drops final cycle "
        f"`{COMPARE_CYC}` — end-of-window noise).",
        "",
        "```text",
        "a22o_2_2.A2 ← a22o_2_2__A2 = dfrtp_2_41.Q ← mux2_1_13.X  (A1=I when S=1)",
        "a22o_2_2.B2 ← a22o_2_2__B2 = dfrtp_2_38.Q ← mux2_1_11.X",
        "a22o_2_2.A1/B1 = or4_2_4__X / buf_2_0__X   # stubs (no I)",
        "a22o_2_2.X  = (A1∧A2) ∨ (B1∧B2)",
        "```",
        "",
        "## Figures",
        "",
        f"- [`{heat.name}`]({heat.name})",
        "- Per-pin response stacks: "
        "[`timelines/I_dep_response_timelines.md`](timelines/I_dep_response_timelines.md)",
        "",
        "## k=1 vs all0 (diff cycle counts)",
        "",
        "| start | A2 | B2 | a22o.X | D_A2 (mux13) | D_B2 (mux11) |",
        "|------:|---:|---:|-------:|-------------:|-------------:|",
    ]
    for e in block("k1_s"):
        s = e["pattern"].split("s")[1]
        md.append(
            f"| {s} | {e['A2_ndiff']} | {e['B2_ndiff']} | {e['a22o_ndiff']} | "
            f"{e['D_A2_ndiff']} | {e['D_B2_ndiff']} |"
        )

    md += [
        "",
        "## k=2 vs all0 (diff cycle counts)",
        "",
        "| start | A2 | B2 | a22o.X | D_A2 (mux13) | D_B2 (mux11) |",
        "|------:|---:|---:|-------:|-------------:|-------------:|",
    ]
    for e in block("k2_s"):
        s = e["pattern"].split("s")[1]
        md.append(
            f"| {s} | {e['A2_ndiff']} | {e['B2_ndiff']} | {e['a22o_ndiff']} | "
            f"{e['D_A2_ndiff']} | {e['D_B2_ndiff']} |"
        )

    md += ["", "## Detail — k1_s0 / k2_s0", ""]
    for lab in ("k1_s0", "k2_s0"):
        e = next(x for x in rows_out if x["pattern"] == lab)
        md.append(f"### `{lab}`")
        md.append("")
        for pin in WATCH:
            md.append(f"- `{pin}`: {fmt_diffs(e, pin)}")
        md.append(
            f"- `D_A2` diffs: n={e['D_A2_ndiff']} first@{e['D_A2_first']}"
        )
        md.append(
            f"- `D_B2` diffs: n={e['D_B2_ndiff']} first@{e['D_B2_first']}"
        )
        md.append("")

    sand = sum(base_s["S_and2b"])
    md += [
        "## Notes",
        "",
        f"- On all0, mux S `inv_2_7__A` is high **{sand}/{N_CYC}** cycles → "
        "`mux2_1_13` passes **I** onto A2’s flop D.",
        "- `D_A2` / `D_B2` columns show the mux outputs feeding the A2/B2 flops "
        "(combinational I effect before the Q sample).",
        "",
        "See also: [`I_comparisons.md`](I_comparisons.md) · "
        "[`I_dep_a221o_pins.md`](I_dep_a221o_pins.md).",
        "",
        "Regenerate:",
        "```bash",
        "python3 phase3/a221o_set/run_I_dep_a22o_pins.py",
        "python3 phase3/a221o_set/run_I_dep_response_timelines.py",
        "python3 phase3/a221o_set/trace_I_comparisons.py",
        "```",
        "",
    ]
    (OUT / "I_dep_a22o_pins.md").write_text("\n".join(md), encoding="utf-8")

    with (OUT / "I_dep_a22o_summary.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "pattern",
            "A2_ndiff",
            "B2_ndiff",
            "a22o_ndiff",
            "D_A2_ndiff",
            "D_B2_ndiff",
            "A2_first",
            "B2_first",
            "a22o_first",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for e in rows_out:
            w.writerow({k: e.get(k) for k in fields})

    print(f"wrote {OUT / 'I_dep_a22o_pins.md'}")
    print(f"wrote {heat}")
    for e in rows_out:
        if e["pattern"] in ("k1_s0", "k2_s0", "k1_s1", "k2_s1"):
            print(
                e["pattern"],
                {p: e[f"{p}_ndiff"] for p in (*WATCH, "D_A2", "D_B2")},
            )


if __name__ == "__main__":
    main()
