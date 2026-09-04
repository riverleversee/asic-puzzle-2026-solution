#!/usr/bin/env python3
"""I-dep response timelines — per-pin stacks + multi-lane boards.

For each watched pin, stack rows = I placement (k=1 or k=2, s=0..10).
Each row marks where I=1 and paints cycles where that pin ≠ all0.

Also writes multi-lane boards (I + all pins) for representative starts.

Usage (from rework_coded/):
  python3 phase3/a221o_set/run_I_dep_response_timelines.py
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
BUILD = ROOT / "phase3" / "build"
OUT = HERE / "I_dep" / "timelines"
N_CYC = 121
STARTS = list(range(0, 11))
COMPARE_CYC = N_CYC - 1  # score 0..119
# Zoom for stacks — responses for s≤10 land early; full width is unreadable.
XMAX = 48

# (csv_key, net, display title, color)
PROBES = [
    ("I", "I", "I", "#c00000"),
    ("enable", "enable", "enable", "#888888"),
    ("a221o_A2", "sky130_fd_sc_hd__mux2_1_12__A1", "a221o.A2 ← mux2_1_12__A1", "#c45911"),
    ("a221o_B2", "sky130_fd_sc_hd__mux2_1_12__A0", "a221o.B2 ← mux2_1_12__A0", "#2e75b6"),
    ("a221o_C1", "sky130_fd_sc_hd__a22o_2_2__X", "a221o.C1 ← a22o_2_2__X", "#548235"),
    ("a221o_X", "sky130_fd_sc_hd__a221o_2_1__X", "a221o.X", "#7030a0"),
    ("a22o_A2", "sky130_fd_sc_hd__a22o_2_2__A2", "a22o.A2 (flop Q)", "#ed7d31"),
    ("a22o_B2", "sky130_fd_sc_hd__a22o_2_2__B2", "a22o.B2 (flop Q)", "#5b9bd5"),
    ("D_A2", "sky130_fd_sc_hd__mux2_1_13__X", "mux2_1_13.X → a22o.A2.D", "#a9d08e"),
    ("D_B2", "sky130_fd_sc_hd__mux2_1_11__X", "mux2_1_11.X → a22o.B2.D", "#9dc3e6"),
    ("S", "sky130_fd_sc_hd__inv_2_7__A", "inv_2_7__A (mux S)", "#833c0c"),
]

# Pins that get their own stack figures
STACK_PINS = [
    "a221o_A2",
    "a221o_B2",
    "a221o_C1",
    "a221o_X",
    "a22o_A2",
    "a22o_B2",
    "D_A2",
    "D_B2",
]

# Multi-lane board (response overview) — exclude enable
BOARD_KEYS = [
    "I",
    "a221o_A2",
    "a221o_B2",
    "a221o_C1",
    "a221o_X",
    "a22o_A2",
    "a22o_B2",
    "D_A2",
    "D_B2",
    "S",
]

BOARD_PATS = ["k1_s2", "k1_s3", "k2_s1", "k2_s2"]


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


def probe_meta(key: str) -> tuple[str, str]:
    for k, _n, title, col in PROBES:
        if k == key:
            return title, col
    raise KeyError(key)


def plot_pin_stack(
    pin: str,
    prefix: str,
    by_mode: dict[str, list[dict]],
    base_s: dict[str, list[int]],
    out_png: Path,
) -> Path:
    """Rows = s=0..10; red = I=1; colored bars = pin ≠ all0."""
    title, col = probe_meta(pin)
    fig, ax = plt.subplots(figsize=(13, 5.2), dpi=140)
    for yi, s in enumerate(reversed(STARTS)):
        lab = f"{prefix}{s}"
        rows = by_mode[lab]
        i_ones = [int(r["cyc"]) for r in rows if int(r["I"])]
        diffs = diff_cycles(base_s[pin], series(rows, pin))
        for c in i_ones:
            if c <= XMAX:
                ax.barh(
                    yi,
                    1.0,
                    left=c - 0.5,
                    height=0.92,
                    color="#f4cccc",
                    edgecolor="none",
                    zorder=1,
                )
                ax.plot(
                    [c, c],
                    [yi - 0.42, yi + 0.42],
                    color="#c00000",
                    lw=1.6,
                    zorder=3,
                )
        for c in diffs:
            if c <= XMAX:
                ax.barh(
                    yi,
                    1.0,
                    left=c - 0.5,
                    height=0.62,
                    color=col,
                    edgecolor="none",
                    zorder=2,
                )
    ax.set_yticks(range(len(STARTS)))
    ax.set_yticklabels([f"s={s}" for s in reversed(STARTS)], fontsize=8, family="monospace")
    ax.set_xlim(-0.5, XMAX + 0.5)
    ax.set_xlabel(f"cycle (zoom 0..{XMAX}; score window drops cyc {COMPARE_CYC})")
    klabel = "k=1 (one I=1)" if prefix == "k1_s" else "k=2 (two consecutive I=1)"
    ax.set_title(f"{title}\n{klabel}  ·  red = I=1  ·  bars = pin ≠ all0")
    ax.grid(axis="x", color="#eee", lw=0.5)
    ax.legend(
        handles=[
            Patch(facecolor="#f4cccc", edgecolor="#c00000", label="I=1"),
            Patch(facecolor=col, label=f"{pin} ≠ all0"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
        frameon=False,
        fontsize=8,
    )
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_board(
    lab: str,
    by_mode: dict[str, list[dict]],
    base_s: dict[str, list[int]],
    out_png: Path,
) -> Path:
    """Stub-style stacked lanes: absolute highs + ≠all0 outline + I spans."""
    rows = by_mode[lab]
    i_ones = [int(r["cyc"]) for r in rows if int(r["I"])]
    keys = [k for k in BOARD_KEYS if k != "I"]
    lane_defs = [("I", "I", "#c00000")] + [
        (k, probe_meta(k)[0], probe_meta(k)[1]) for k in keys
    ]

    fig, ax = plt.subplots(figsize=(14, 6.2), dpi=140)
    for yi, (key, title, col) in enumerate(reversed(lane_defs)):
        if key == "I":
            highs = i_ones
            diffs: list[int] = []
        else:
            ys = series(rows, key)
            highs = [c for c, v in enumerate(ys) if v]
            diffs = diff_cycles(base_s[key], ys)
        for c in i_ones:
            if c <= XMAX:
                ax.axvline(c, color="#f4cccc", lw=6, alpha=0.55, zorder=0)
        for c in highs:
            if c <= XMAX:
                ax.barh(
                    yi,
                    1.0,
                    left=c - 0.5,
                    height=0.72,
                    color=col if key == "I" else "#d9d9d9",
                    edgecolor="none",
                    zorder=1,
                )
        for c in diffs:
            if c <= XMAX:
                ax.barh(
                    yi,
                    1.0,
                    left=c - 0.5,
                    height=0.72,
                    color=col,
                    edgecolor="none",
                    zorder=2,
                )
        # I tick on every lane
        for c in i_ones:
            if c <= XMAX:
                ax.plot(
                    [c, c],
                    [yi - 0.4, yi + 0.4],
                    color="#c00000",
                    lw=1.2,
                    zorder=3,
                )

    ax.set_yticks(range(len(lane_defs)))
    ax.set_yticklabels(
        [t for _k, t, _c in reversed(lane_defs)], fontsize=7.5, family="monospace"
    )
    ax.set_xlim(-0.5, XMAX + 0.5)
    ax.set_xlabel(f"cycle (zoom 0..{XMAX})")
    ax.set_title(
        f"Response board · {lab}  ·  I@ {i_ones}\n"
        "gray = high under this pattern · color = ≠ all0 · red tick = I=1"
    )
    ax.grid(axis="x", color="#eee", lw=0.5)
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    pats: list[tuple[str, str]] = [("all0", "0" * N_CYC)]
    for s in STARTS:
        pats.append((f"k1_s{s}", bits_from_ones({s})))
    for s in STARTS:
        pats.append((f"k2_s{s}", bits_from_ones({s, s + 1})))

    pats_path = BUILD / "pats_I_dep_timelines.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")

    labels = [p[0] for p in PROBES]
    n = len(PROBES)
    n_pat = len(pats)
    dumps = []
    for i, (_lab, net, _t, _c) in enumerate(PROBES):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_I_dep_timelines.csv"
    tb = BUILD / "tb_I_dep_timelines.v"
    vvp = BUILD / "tb_I_dep_timelines.vvp"
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
    watch = [k for k, *_ in PROBES if k not in ("I", "enable")]
    base_s = {k: series(base, k) for k in watch}

    written: list[Path] = []
    for pin in STACK_PINS:
        for prefix, tag in (("k1_s", "k1"), ("k2_s", "k2")):
            p = plot_pin_stack(
                pin, prefix, by_mode, base_s, OUT / f"stack_{pin}_{tag}.png"
            )
            written.append(p)
            print(f"  {p.name}")

    for lab in BOARD_PATS:
        p = plot_board(lab, by_mode, base_s, OUT / f"board_{lab}.png")
        written.append(p)
        print(f"  {p.name}")

    # Compact first-diff table for md
    def first_diff(pin: str, lab: str) -> str:
        d = diff_cycles(base_s[pin], series(by_mode[lab], pin))
        return "—" if not d else f"@{d[0]} (n={len(d)})"

    md = [
        "# I-dep response timelines",
        "",
        "Per-pin **stacks**: each row is an I placement (`s=0..10`).",
        "Red tick / pink column = where `I=1`. Colored bars = that pin **≠ all0**.",
        "",
        f"Zoom `0..{XMAX}` (early window). Diff scoring still drops cycle `{COMPARE_CYC}`.",
        "",
        "## Multi-lane boards (all pins together)",
        "",
        "Gray = high under the pattern; color overlay = ≠ all0; red tick = I=1.",
        "",
    ]
    for lab in BOARD_PATS:
        md.append(f"- [`board_{lab}.png`](board_{lab}.png)")
    md += ["", "## Per-pin stacks", ""]
    for pin in STACK_PINS:
        title, _ = probe_meta(pin)
        md.append(f"### `{pin}` — {title}")
        md.append("")
        md.append(f"- k=1: [`stack_{pin}_k1.png`](stack_{pin}_k1.png)")
        md.append(f"- k=2: [`stack_{pin}_k2.png`](stack_{pin}_k2.png)")
        md.append("")
        md.append("| start | k1 first≠ | k2 first≠ |")
        md.append("|------:|----------:|----------:|")
        for s in STARTS:
            md.append(
                f"| {s} | {first_diff(pin, f'k1_s{s}')} | {first_diff(pin, f'k2_s{s}')} |"
            )
        md.append("")

    md += [
        "Regenerate:",
        "```bash",
        "python3 phase3/a221o_set/run_I_dep_response_timelines.py",
        "```",
        "",
    ]
    md_path = OUT / "I_dep_response_timelines.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"{len(written)} figures → {OUT}")


if __name__ == "__main__":
    main()
