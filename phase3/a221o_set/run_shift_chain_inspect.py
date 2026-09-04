#!/usr/bin/env python3
"""Inspect the I→a221o mux/flop chain: Verilog match + time / extra-I tests.

Hypothesis from I-dep timelines: the A2/B2 path is a **shift register**
(mux2 + dfrtp), not FA arithmetic on I. FA-side nets (`or4_2_4`, …) gate
whether a shifted pulse appears on C1 / a221o.X — so those outputs **do**
depend on *which cycle* I enters, even though the shift taps themselves
are pure delays.

What this script does
---------------------
1. Walk structural Verilog from `mux2_1_13` (A1=I) along the A1/S=1 data
   path; record each flop stage and expected delay from I.
2. Simulate with **I@1** as the reference pulse (never cycle 120).
3. Match observed first≠all0 delays to Verilog stage depths.
4. **FA-prior nets**: confirm identical for all0 vs any I placement.
5. **Time entry**: align responses to I; show shift taps are shift-invariant,
   while C1 / a221o.X are gated by FA stubs (shape depends on entry cycle).
6. **Extra I**: close + **wide** gaps (Δ up to 88) and **triple** spaced
   pulses; check response == OR of the corresponding singles.

Outputs → `I_dep/shift_chain/`

Usage (from rework_coded/):
  python3 phase3/a221o_set/run_shift_chain_inspect.py
"""
from __future__ import annotations

import csv
import json
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
from structural_drivers import parse_structural  # noqa: E402

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
PDK = REPO / "netlist" / "structural" / "pdk"
INC = PDK / "include"
BUILD = ROOT / "phase3" / "build"
OUT = HERE / "I_dep" / "shift_chain"

N_CYC = 121
COMPARE_CYC = N_CYC - 1  # score 0..119; never treat cyc 120 as signal
I_REF = 1  # reference pulse cycle (user: not 120)

# Gaps between I ones. Close = within/near the 12-stage chain; wide = well separated
# (incl. multiples of the ~11-cycle or4.X hole period).
CLOSE_GAPS = [1, 2, 3, 5, 6, 10, 11, 12]
WIDE_GAPS = [15, 20, 22, 24, 33, 44, 55, 66, 77, 88]
EXTRA_GAPS = CLOSE_GAPS + WIDE_GAPS
# Three ones: I @ {1, 1+g, 1+2g} with g large enough that pulses don't overlap in the chain
TRIPLE_GAPS = [22, 33, 44]

# Singles needed for OR checks + time-entry near window
_pulse_pos = {I_REF}
for g in EXTRA_GAPS:
    _pulse_pos.add(I_REF + g)
for g in TRIPLE_GAPS:
    _pulse_pos.add(I_REF + g)
    _pulse_pos.add(I_REF + 2 * g)
STARTS = sorted(c for c in _pulse_pos if 0 <= c < COMPARE_CYC)
STARTS_NEAR = [s for s in STARTS if s <= 13]  # readable time-entry stack

XMAX = 40  # near-window figures
XMAX_WIDE = 100  # spaced-I figures

# Named taps we care about (csv_key, full net, title, color, group)
# group: "shift" | "gated" | "fa_prior"
PROBES = [
    ("I", "I", "I", "#c00000", "stim"),
    ("enable", "enable", "enable", "#888888", "stim"),
    ("D_A2", "sky130_fd_sc_hd__mux2_1_13__X", "mux13.X (I entry / A2.D)", "#a9d08e", "shift"),
    ("a22o_A2", "sky130_fd_sc_hd__a22o_2_2__A2", "a22o.A2 flop Q", "#ed7d31", "shift"),
    ("a221o_A2", "sky130_fd_sc_hd__mux2_1_12__A1", "a221o.A2", "#c45911", "shift"),
    ("a221o_B2", "sky130_fd_sc_hd__mux2_1_12__A0", "a221o.B2", "#2e75b6", "shift"),
    ("D_B2", "sky130_fd_sc_hd__mux2_1_11__X", "mux11.X (B2.D)", "#9dc3e6", "shift"),
    ("a22o_B2", "sky130_fd_sc_hd__a22o_2_2__B2", "a22o.B2 flop Q", "#5b9bd5", "shift"),
    ("a22o_X", "sky130_fd_sc_hd__a22o_2_2__X", "a22o.X → a221o.C1", "#548235", "gated"),
    ("a221o_X", "sky130_fd_sc_hd__a221o_2_1__X", "a221o.X", "#7030a0", "gated"),
    # FA-prior / stubs (should ignore I)
    ("or4_X", "sky130_fd_sc_hd__or4_2_4__X", "or4_2_4.X (a22o.A1, FA bus OR)", "#1f4e79", "fa_prior"),
    ("or4_A", "sky130_fd_sc_hd__or4_2_4__A", "or4_2_4.A (FA reg)", "#2e75b6", "fa_prior"),
    ("or4_B", "sky130_fd_sc_hd__or4_2_4__B", "or4_2_4.B (FA reg)", "#5b9bd5", "fa_prior"),
    ("or4_C", "sky130_fd_sc_hd__or4_2_4__C", "or4_2_4.C (FA reg)", "#9dc3e6", "fa_prior"),
    ("or4_D", "sky130_fd_sc_hd__or4_2_4__D", "or4_2_4.D (FA reg)", "#bdd7ee", "fa_prior"),
    ("or4bb", "sky130_fd_sc_hd__or4bb_2_0__X", "or4bb → a221o.A1", "#548235", "fa_prior"),
    ("S", "sky130_fd_sc_hd__inv_2_7__A", "inv_2_7__A (mux S / and2b.Y)", "#833c0c", "fa_prior"),
    ("AN", "sky130_fd_sc_hd__or2_2_11__A", "or2_2_11__A (and2b.A_N)", "#8d6e63", "fa_prior"),
]

MUX_ENTRY = "sky130_fd_sc_hd__mux2_1_13"


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


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
    # $readmemb: left char = MSB = pat[N_CYC-1]
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


def ones_list(xs: list[int]) -> list[int]:
    return [i for i, v in enumerate(xs) if v and i < COMPARE_CYC]


# ---------------------------------------------------------------------------
# 1. Structural walk
# ---------------------------------------------------------------------------


def walk_shift_chain(drivers: dict) -> list[dict]:
    """Follow S=1 data path: mux A1 → X → flop D → Q → next mux A1 …

    Stage 0 is combinational mux13.X (same cycle as I when S=1).
    Each subsequent flop Q is +1 cycle.
    """
    mux = drivers.get(f"{MUX_ENTRY}__X")
    if not mux:
        raise SystemExit(f"missing {MUX_ENTRY}__X in netlist")
    pins = mux["in_pins"]
    if pins.get("A1") != "I":
        raise SystemExit(f"{MUX_ENTRY} A1 is {pins.get('A1')}, expected I")

    stages: list[dict] = []
    # combo entry
    stages.append(
        {
            "stage": 0,
            "kind": "combo_mux",
            "net": f"{MUX_ENTRY}__X",
            "instance": short(mux["instance"]),
            "expected_delay": 0,
            "note": "A1=I → X (when S=1)",
        }
    )

    # net currently carrying the shifted I value (after combo: mux X)
    cur = f"{MUX_ENTRY}__X"
    seen_flops: set[str] = set()

    for stage in range(1, 20):
        # find flop whose D = cur
        flop_q = None
        flop_info = None
        for net, info in drivers.items():
            if info.get("class") != "flop":
                continue
            if info["in_pins"].get("D") == cur and net not in seen_flops:
                flop_q = net
                flop_info = info
                break
        if flop_q is None:
            break
        seen_flops.add(flop_q)
        stages.append(
            {
                "stage": stage,
                "kind": "flop",
                "net": flop_q,
                "instance": short(flop_info["instance"]),
                "expected_delay": stage,
                "note": f"D←{short(cur)}",
            }
        )
        # next mux: S-path with A1 = this Q (shift forward)
        next_mux_x = None
        next_mux = None
        for net, info in drivers.items():
            if info.get("class") != "mux":
                continue
            if info["in_pins"].get("A1") == flop_q:
                next_mux_x = net
                next_mux = info
                break
        if next_mux_x is None:
            # end of A1 chain (a22o.B2 is last flop; its mux uses A1=prev)
            break
        stages.append(
            {
                "stage": stage,  # same cycle as Q (combo mux after flop)
                "kind": "combo_mux",
                "net": next_mux_x,
                "instance": short(next_mux["instance"]),
                "expected_delay": stage,
                "note": f"A1←{short(flop_q)} → X",
            }
        )
        cur = next_mux_x

    return stages


def tap_expected_delay(stages: list[dict], net: str) -> int | None:
    full = net if net.startswith("sky130") or net == "I" else f"sky130_fd_sc_hd__{net}"
    # prefer flop stage if both mux X and Q listed
    hits = [s for s in stages if s["net"] == full or short(s["net"]) == short(full)]
    if not hits:
        # try without prefix mismatch
        hits = [s for s in stages if short(s["net"]) == short(net)]
    if not hits:
        return None
    flops = [s for s in hits if s["kind"] == "flop"]
    return (flops[-1] if flops else hits[-1])["expected_delay"]


# ---------------------------------------------------------------------------
# Sim helpers
# ---------------------------------------------------------------------------


def run_sim(pats: list[tuple[str, str]]) -> dict[str, list[dict]]:
    BUILD.mkdir(parents=True, exist_ok=True)
    pats_path = BUILD / "pats_shift_chain.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")

    labels = [p[0] for p in PROBES]
    n = len(PROBES)
    n_pat = len(pats)
    dumps = []
    for i, (_lab, net, *_rest) in enumerate(PROBES):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_shift_chain.csv"
    tb = BUILD / "tb_shift_chain.v"
    vvp = BUILD / "tb_shift_chain.vvp"
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
    return by_mode


def align_to_i(xs: list[int], i_at: int, ref: int = I_REF) -> list[int]:
    """Shift series so I pulse lines up with ref cycle."""
    delta = i_at - ref
    out = [0] * N_CYC
    for t, v in enumerate(xs):
        t2 = t - delta
        if 0 <= t2 < N_CYC:
            out[t2] = v
    return out


def or_series(a: list[int], b: list[int]) -> list[int]:
    return [1 if (x or y) else 0 for x, y in zip(a, b)]


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------


def plot_chain_match(
    stages: list[dict],
    matches: list[dict],
    out_png: Path,
) -> Path:
    """Horizontal ladder: stage vs expected/observed delay."""
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=140)
    ys = list(range(len(matches)))
    exp = [m["expected"] for m in matches]
    obs = [m["observed"] if m["observed"] is not None else -1 for m in matches]
    ax.scatter(exp, ys, s=80, c="#1f4e79", zorder=3, label="Verilog expected")
    ax.scatter(
        [o if o >= 0 else float("nan") for o in obs],
        ys,
        s=50,
        c="#c45911",
        marker="x",
        zorder=4,
        label="sim first≠ (I@1)",
    )
    for y, e, o, m in zip(ys, exp, obs, matches):
        ok = o == e
        ax.plot([e, o if o >= 0 else e], [y, y], color="#aaa" if ok else "#c00000", lw=1)
        ax.text(max(e, o if o >= 0 else e) + 0.35, y, "OK" if ok else "MISS", va="center", fontsize=7)
    ax.set_yticks(ys)
    ax.set_yticklabels([m["label"] for m in matches], fontsize=8, family="monospace")
    ax.set_xlabel("delay from I (cycles)")
    ax.set_title("Shift-chain match · Verilog stage depth vs sim (reference I@1)")
    ax.set_xlim(-0.5, max(exp + [o for o in obs if o >= 0]) + 3)
    ax.grid(axis="x", color="#eee")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_fa_prior_board(by_mode: dict, base_s: dict, out_png: Path) -> Path:
    """FA-prior nets under all0 and I@1 — should be identical."""
    fa_keys = [p[0] for p in PROBES if p[4] == "fa_prior"]
    fig, axes = plt.subplots(2, 1, figsize=(13, 5.8), dpi=140, sharex=True)
    for ax, lab, title in (
        (axes[0], "all0", "FA-prior nets · all0 (no I)"),
        (axes[1], f"k1_s{I_REF}", f"FA-prior nets · I@{I_REF}"),
    ):
        rows = by_mode[lab]
        for yi, key in enumerate(reversed(fa_keys)):
            title_k = next(p[2] for p in PROBES if p[0] == key)
            col = next(p[3] for p in PROBES if p[0] == key)
            highs = ones_list(series(rows, key))
            for c in highs:
                if c <= XMAX:
                    ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none")
        ax.set_yticks(range(len(fa_keys)))
        ax.set_yticklabels(
            [next(p[2] for p in PROBES if p[0] == k) for k in reversed(fa_keys)],
            fontsize=7,
            family="monospace",
        )
        ax.set_xlim(-0.5, XMAX + 0.5)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="x", color="#eee", lw=0.5)
        if lab != "all0":
            ax.axvline(I_REF, color="#c00000", lw=1.4, alpha=0.8)
    axes[-1].set_xlabel(f"cycle (0..{XMAX})")
    fig.suptitle("FA-prior / stub nets ignore I  ·  bands should match across panels", fontsize=11)
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_time_entry(
    by_mode: dict,
    base_s: dict,
    out_png: Path,
) -> Path:
    """Stack I@near starts for a22o.A2 (shift) vs a22o.X (FA-gated)."""
    starts = STARTS_NEAR
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8), dpi=140, sharey=True)
    for ax, key, title, col in (
        (axes[0], "a22o_A2", "a22o.A2 — pure shift (+1)", "#ed7d31"),
        (axes[1], "a22o_X", "a22o.X (C1) — FA-gated", "#548235"),
    ):
        for yi, s in enumerate(reversed(starts)):
            rows = by_mode[f"k1_s{s}"]
            diffs = diff_cycles(base_s[key], series(rows, key))
            if s <= XMAX:
                ax.barh(yi, 1.0, left=s - 0.5, height=0.9, color="#f4cccc", edgecolor="none", zorder=1)
                ax.plot([s, s], [yi - 0.4, yi + 0.4], color="#c00000", lw=1.4, zorder=3)
            for c in diffs:
                if c <= XMAX:
                    ax.barh(yi, 1.0, left=c - 0.5, height=0.62, color=col, edgecolor="none", zorder=2)
        ax.set_yticks(range(len(starts)))
        ax.set_yticklabels([f"I@{s}" for s in reversed(starts)], fontsize=8, family="monospace")
        ax.set_xlim(-0.5, XMAX + 0.5)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="x", color="#eee", lw=0.5)
        ax.set_xlabel("cycle")
    fig.suptitle(
        "Time entry of I · red = I=1 · color = ≠ all0\n"
        "Left: diagonal = fixed delay. Right: some entry cycles miss (FA stub low).",
        fontsize=11,
    )
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_aligned_overlay(
    by_mode: dict,
    base_s: dict,
    out_png: Path,
) -> Path:
    """After aligning each I@s to I@1: shift taps overlap; C1 may not."""
    keys = ["a22o_A2", "a221o_A2", "a221o_B2", "a22o_B2", "a22o_X", "a221o_X"]
    starts = STARTS_NEAR
    fig, axes = plt.subplots(len(keys), 1, figsize=(13, 8.5), dpi=140, sharex=True)
    ref_rows = by_mode[f"k1_s{I_REF}"]
    for ax, key in zip(axes, keys):
        col = next(p[3] for p in PROBES if p[0] == key)
        title = next(p[2] for p in PROBES if p[0] == key)
        ref_diff = [
            1 if a != b else 0
            for a, b in zip(base_s[key], series(ref_rows, key))
        ]
        for c, v in enumerate(ref_diff):
            if v and c <= XMAX:
                ax.barh(0, 1.0, left=c - 0.5, height=0.35, color=col, alpha=0.9, edgecolor="none")
        mismatches = 0
        for s in starts:
            if s == I_REF:
                continue
            rows = by_mode[f"k1_s{s}"]
            rel = [
                1 if a != b else 0
                for a, b in zip(base_s[key], series(rows, key))
            ]
            aligned = align_to_i(rel, s, I_REF)
            for c, (r, a) in enumerate(zip(ref_diff, aligned)):
                if c > XMAX:
                    break
                if a and not r:
                    ax.barh(0.35, 1.0, left=c - 0.5, height=0.25, color="#c00000", alpha=0.7, edgecolor="none")
                    mismatches += 1
                elif r and not a:
                    ax.barh(-0.35, 1.0, left=c - 0.5, height=0.25, color="#7030a0", alpha=0.5, edgecolor="none")
                    mismatches += 1
        ax.axvline(I_REF, color="#c00000", lw=0.9, alpha=0.7)
        ax.set_yticks([])
        ax.set_ylabel(key, rotation=0, ha="right", va="center", fontsize=8)
        ax.set_xlim(-0.5, XMAX + 0.5)
        ax.set_title(f"{title}  ·  aligned to I@{I_REF}  ·  extra≠ref marks={mismatches}", fontsize=9)
        ax.grid(axis="x", color="#eee", lw=0.5)
    axes[-1].set_xlabel(f"cycle (aligned; I@{I_REF} marked)")
    fig.suptitle(
        "Shift-invariance check · solid = I@1 response · red/purple = other I@s disagree after align",
        fontsize=11,
    )
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_extra_i(
    by_mode: dict,
    base_s: dict,
    gaps: list[int],
    out_png: Path,
    xmax: int,
    title: str,
) -> Path:
    """For each gap: two ones vs OR of singles."""
    fig_h = max(4.5, 0.38 * len(gaps) + 2.2)
    fig, axes = plt.subplots(2, 1, figsize=(14, fig_h), dpi=140, sharex=True)
    for ax, key, subtitle, col in (
        (axes[0], "a22o_A2", "a22o.A2 shift tap — expect linear OR", "#ed7d31"),
        (axes[1], "a22o_X", "a22o.X gated — OR of gated singles", "#548235"),
    ):
        for yi, g in enumerate(reversed(gaps)):
            lab = f"extra_g{g}"
            single_a = [
                1 if a != b else 0
                for a, b in zip(base_s[key], series(by_mode[f"k1_s{I_REF}"], key))
            ]
            single_b = [
                1 if a != b else 0
                for a, b in zip(base_s[key], series(by_mode[f"k1_s{I_REF + g}"], key))
            ]
            pred = or_series(single_a, single_b)
            got = [
                1 if a != b else 0
                for a, b in zip(base_s[key], series(by_mode[lab], key))
            ]
            for c in (I_REF, I_REF + g):
                if c <= xmax:
                    ax.plot([c, c], [yi - 0.4, yi + 0.4], color="#c00000", lw=1.1, zorder=3)
            for c, v in enumerate(got):
                if v and c <= xmax:
                    ax.barh(yi, 1.0, left=c - 0.5, height=0.55, color=col, edgecolor="none", zorder=2)
            for c, (p, g_) in enumerate(zip(pred, got)):
                if p != g_ and c <= xmax:
                    ax.scatter([c], [yi], s=14, c="#c00000", zorder=4, marker="o")
        ax.set_yticks(range(len(gaps)))
        ax.set_yticklabels(
            [f"Δ={g}  I@{{{I_REF},{I_REF + g}}}" for g in reversed(gaps)],
            fontsize=7,
            family="monospace",
        )
        ax.set_xlim(-0.5, xmax + 0.5)
        ax.set_title(subtitle, fontsize=10)
        ax.grid(axis="x", color="#eee", lw=0.5)
    axes[-1].set_xlabel(f"cycle (0..{xmax}) · red ticks = I · red dots = ≠ OR(singles)")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_triple_i(
    by_mode: dict,
    base_s: dict,
    out_png: Path,
) -> Path:
    """Three spaced ones vs OR of three singles."""
    gaps = TRIPLE_GAPS
    fig, axes = plt.subplots(2, 1, figsize=(14, 4.8), dpi=140, sharex=True)
    for ax, key, subtitle, col in (
        (axes[0], "a22o_A2", "a22o.A2 — expect OR of 3 singles", "#ed7d31"),
        (axes[1], "a22o_X", "a22o.X — OR of 3 gated singles", "#548235"),
    ):
        for yi, g in enumerate(reversed(gaps)):
            ones = (I_REF, I_REF + g, I_REF + 2 * g)
            lab = f"triple_g{g}"
            pred = [0] * N_CYC
            for s in ones:
                rel = [
                    1 if a != b else 0
                    for a, b in zip(base_s[key], series(by_mode[f"k1_s{s}"], key))
                ]
                pred = or_series(pred, rel)
            got = [
                1 if a != b else 0
                for a, b in zip(base_s[key], series(by_mode[lab], key))
            ]
            for c in ones:
                if c <= XMAX_WIDE:
                    ax.plot([c, c], [yi - 0.4, yi + 0.4], color="#c00000", lw=1.2, zorder=3)
            for c, v in enumerate(got):
                if v and c <= XMAX_WIDE:
                    ax.barh(yi, 1.0, left=c - 0.5, height=0.55, color=col, edgecolor="none", zorder=2)
            for c, (p, g_) in enumerate(zip(pred, got)):
                if p != g_ and c <= XMAX_WIDE:
                    ax.scatter([c], [yi], s=16, c="#c00000", zorder=4, marker="o")
        ax.set_yticks(range(len(gaps)))
        ax.set_yticklabels(
            [f"Δ={g}  I@{{{I_REF},{I_REF+g},{I_REF+2*g}}}" for g in reversed(gaps)],
            fontsize=7,
            family="monospace",
        )
        ax.set_xlim(-0.5, XMAX_WIDE + 0.5)
        ax.set_title(subtitle, fontsize=10)
        ax.grid(axis="x", color="#eee", lw=0.5)
    axes[-1].set_xlabel(f"cycle (0..{XMAX_WIDE}) · red ticks = I · dots = ≠ OR(singles)")
    fig.suptitle("Triple spaced I · three ones vs OR of three single-I responses", fontsize=11)
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_wide_board(by_mode: dict, base_s: dict, out_png: Path) -> Path:
    """One wide double-I board: I@{1, 1+44} so pulses are far apart."""
    g = 44
    lab = f"extra_g{g}"
    rows = by_mode[lab]
    ones = [I_REF, I_REF + g]
    order = [
        "I",
        "a22o_A2",
        "a221o_A2",
        "a221o_B2",
        "a22o_B2",
        "a22o_X",
        "a221o_X",
        "or4_X",
    ]
    fig, ax = plt.subplots(figsize=(14, 5.2), dpi=140)
    for yi, key in enumerate(reversed(order)):
        title = next(p[2] for p in PROBES if p[0] == key)
        col = next(p[3] for p in PROBES if p[0] == key)
        grp = next(p[4] for p in PROBES if p[0] == key)
        ys = series(rows, key)
        highs = ones_list(ys)
        diffs = [] if key == "I" else diff_cycles(base_s[key], ys)
        for c in highs:
            if c <= XMAX_WIDE:
                shade = col if key == "I" or grp == "fa_prior" else "#d9d9d9"
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=shade, edgecolor="none", zorder=1)
        for c in diffs:
            if c <= XMAX_WIDE:
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none", zorder=2)
        for c in ones:
            if c <= XMAX_WIDE:
                ax.plot([c, c], [yi - 0.4, yi + 0.4], color="#c00000", lw=1.1, zorder=3)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(
        [next(p[2] for p in PROBES if p[0] == k) for k in reversed(order)],
        fontsize=7.5,
        family="monospace",
    )
    ax.set_xlim(-0.5, XMAX_WIDE + 0.5)
    ax.set_xlabel(f"cycle · I@{{{ones[0]}, {ones[1]}}} (gap {g})")
    ax.set_title(
        f"Spaced double-I board · gap={g}\n"
        "Two well-separated shift cascades; color = ≠ all0"
    )
    ax.grid(axis="x", color="#eee", lw=0.5)
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_ref_board(by_mode: dict, base_s: dict, out_png: Path) -> Path:
    lab = f"k1_s{I_REF}"
    rows = by_mode[lab]
    keys = [p[0] for p in PROBES if p[4] in ("stim", "shift", "gated", "fa_prior") and p[0] != "enable"]
    # order: I, shift…, gated, fa (subset)
    order = [
        "I",
        "D_A2",
        "a22o_A2",
        "a221o_A2",
        "a221o_B2",
        "D_B2",
        "a22o_B2",
        "a22o_X",
        "a221o_X",
        "or4_X",
        "S",
    ]
    keys = [k for k in order if k in {p[0] for p in PROBES}]
    fig, ax = plt.subplots(figsize=(14, 6.0), dpi=140)
    for yi, key in enumerate(reversed(keys)):
        title = next(p[2] for p in PROBES if p[0] == key)
        col = next(p[3] for p in PROBES if p[0] == key)
        grp = next(p[4] for p in PROBES if p[0] == key)
        ys = series(rows, key)
        highs = ones_list(ys)
        diffs = [] if key == "I" else diff_cycles(base_s[key], ys)
        for c in highs:
            if c <= XMAX:
                shade = col if key == "I" or grp == "fa_prior" else "#d9d9d9"
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=shade, edgecolor="none", zorder=1)
        for c in diffs:
            if c <= XMAX:
                ax.barh(yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none", zorder=2)
        if I_REF <= XMAX:
            ax.plot([I_REF, I_REF], [yi - 0.4, yi + 0.4], color="#c00000", lw=1.2, zorder=3)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels(
        [next(p[2] for p in PROBES if p[0] == k) for k in reversed(keys)],
        fontsize=7.5,
        family="monospace",
    )
    ax.set_xlim(-0.5, XMAX + 0.5)
    ax.set_xlabel(f"cycle · reference I@{I_REF}")
    ax.set_title(
        f"Reference board · I@{I_REF}\n"
        "gray/color = high; for shift/gated, color overlay = ≠ all0; FA lanes show absolute high"
    )
    ax.grid(axis="x", color="#eee", lw=0.5)
    fig.tight_layout()
    return savefig_locked(fig, out_png)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    drivers, _stubs, _meta = parse_structural(STRUCT)
    stages = walk_shift_chain(drivers)

    # Patterns: all0, k1 at each start, spaced double-I, spaced triple-I
    pats: list[tuple[str, str]] = [("all0", "0" * N_CYC)]
    for s in STARTS:
        pats.append((f"k1_s{s}", bits_from_ones({s})))
    for g in EXTRA_GAPS:
        pats.append((f"extra_g{g}", bits_from_ones({I_REF, I_REF + g})))
    for g in TRIPLE_GAPS:
        pats.append(
            (f"triple_g{g}", bits_from_ones({I_REF, I_REF + g, I_REF + 2 * g}))
        )

    by_mode = run_sim(pats)
    base = by_mode["all0"]
    watch = [p[0] for p in PROBES if p[0] not in ("I", "enable")]
    base_s = {k: series(base, k) for k in watch}

    # Sanity: I actually fires at I_REF
    i_series = series(by_mode[f"k1_s{I_REF}"], "I")
    i_ones = ones_list(i_series)
    if i_ones != [I_REF]:
        raise SystemExit(f"BUG: expected I@[{I_REF}], got {i_ones} (endianness?)")

    # --- Match table ---
    tap_keys = [p[0] for p in PROBES if p[4] == "shift"]
    matches = []
    ref_lab = f"k1_s{I_REF}"
    for key in tap_keys:
        net = next(p[1] for p in PROBES if p[0] == key)
        exp = tap_expected_delay(stages, net)
        dcy = diff_cycles(base_s[key], series(by_mode[ref_lab], key))
        obs = (dcy[0] - I_REF) if dcy else None
        matches.append(
            {
                "key": key,
                "label": f"{key}  {short(net)}",
                "net": net,
                "expected": exp,
                "observed": obs,
                "first_cyc": dcy[0] if dcy else None,
                "ok": exp is not None and obs == exp,
            }
        )

    # --- FA-prior independence ---
    fa_keys = [p[0] for p in PROBES if p[4] == "fa_prior"]
    fa_indep = True
    fa_report = []
    for key in fa_keys:
        bad = []
        for s in STARTS:
            if series(by_mode[f"k1_s{s}"], key) != base_s[key]:
                bad.append(s)
                fa_indep = False
        fa_report.append({"key": key, "differs_at_starts": bad})

    # --- Shift invariance (aligned) — all starts, full compare window ---
    inv_report = []
    for key in ["a22o_A2", "a221o_A2", "a221o_B2", "a22o_B2", "a22o_X", "a221o_X"]:
        ref_rel = [
            1 if a != b else 0
            for a, b in zip(base_s[key], series(by_mode[ref_lab], key))
        ]
        n_bad = 0
        bad_starts = []
        for s in STARTS:
            if s == I_REF:
                continue
            rel = [
                1 if a != b else 0
                for a, b in zip(base_s[key], series(by_mode[f"k1_s{s}"], key))
            ]
            aligned = align_to_i(rel, s, I_REF)
            # only compare cycles where both sides are in-window after shift
            delta = s - I_REF
            ok = True
            for t in range(COMPARE_CYC):
                src = t + delta
                if not (0 <= src < COMPARE_CYC):
                    continue
                if aligned[t] != ref_rel[t]:
                    ok = False
                    break
            if not ok:
                n_bad += 1
                bad_starts.append(s)
        inv_report.append(
            {
                "key": key,
                "group": next(p[4] for p in PROBES if p[0] == key),
                "n_disagree_starts": n_bad,
                "bad_starts": bad_starts,
                "shift_invariant": n_bad == 0,
            }
        )

    # --- Extra I linearity (close + wide) ---
    def linearity_for_gaps(gaps: list[int]) -> list[dict]:
        out = []
        for key in ["a22o_A2", "a221o_A2", "a221o_B2", "a22o_B2", "a22o_X", "a221o_X"]:
            bad_gaps = []
            for g in gaps:
                sa = [
                    1 if a != b else 0
                    for a, b in zip(base_s[key], series(by_mode[f"k1_s{I_REF}"], key))
                ]
                sb = [
                    1 if a != b else 0
                    for a, b in zip(base_s[key], series(by_mode[f"k1_s{I_REF + g}"], key))
                ]
                pred = or_series(sa, sb)
                got = [
                    1 if a != b else 0
                    for a, b in zip(base_s[key], series(by_mode[f"extra_g{g}"], key))
                ]
                if pred != got:
                    bad_gaps.append(g)
            out.append(
                {
                    "key": key,
                    "group": next(p[4] for p in PROBES if p[0] == key),
                    "nonlinear_gaps": bad_gaps,
                    "linear_or": len(bad_gaps) == 0,
                }
            )
        return out

    extra_close = linearity_for_gaps(CLOSE_GAPS)
    extra_wide = linearity_for_gaps(WIDE_GAPS)
    extra_report = linearity_for_gaps(EXTRA_GAPS)

    # --- Triple I linearity ---
    triple_report = []
    for key in ["a22o_A2", "a221o_A2", "a221o_B2", "a22o_B2", "a22o_X", "a221o_X"]:
        bad = []
        for g in TRIPLE_GAPS:
            pred = [0] * N_CYC
            for s in (I_REF, I_REF + g, I_REF + 2 * g):
                rel = [
                    1 if a != b else 0
                    for a, b in zip(base_s[key], series(by_mode[f"k1_s{s}"], key))
                ]
                pred = or_series(pred, rel)
            got = [
                1 if a != b else 0
                for a, b in zip(base_s[key], series(by_mode[f"triple_g{g}"], key))
            ]
            if pred != got:
                bad.append(g)
        triple_report.append(
            {
                "key": key,
                "group": next(p[4] for p in PROBES if p[0] == key),
                "nonlinear_gaps": bad,
                "linear_or": len(bad) == 0,
            }
        )

    # Plots
    figs = []
    figs.append(plot_ref_board(by_mode, base_s, OUT / "board_I_at_1.png"))
    figs.append(plot_chain_match(stages, matches, OUT / "chain_delay_match.png"))
    figs.append(plot_fa_prior_board(by_mode, base_s, OUT / "fa_prior_vs_I.png"))
    figs.append(plot_time_entry(by_mode, base_s, OUT / "time_entry_shift_vs_gated.png"))
    figs.append(plot_aligned_overlay(by_mode, base_s, OUT / "aligned_invariance.png"))
    figs.append(
        plot_extra_i(
            by_mode,
            base_s,
            CLOSE_GAPS,
            OUT / "extra_I_close_vs_OR.png",
            XMAX,
            "Close double-I (Δ≤12) · two ones vs OR of singles",
        )
    )
    figs.append(
        plot_extra_i(
            by_mode,
            base_s,
            WIDE_GAPS,
            OUT / "extra_I_wide_vs_OR.png",
            XMAX_WIDE,
            "Wide double-I (Δ=15..88) · two ones vs OR of singles",
        )
    )
    figs.append(plot_triple_i(by_mode, base_s, OUT / "extra_I_triple_vs_OR.png"))
    figs.append(plot_wide_board(by_mode, base_s, OUT / "board_I_spaced_g44.png"))

    # JSON + MD
    payload = {
        "I_ref": I_REF,
        "n_cyc": N_CYC,
        "compare_cyc": COMPARE_CYC,
        "close_gaps": CLOSE_GAPS,
        "wide_gaps": WIDE_GAPS,
        "triple_gaps": TRIPLE_GAPS,
        "starts": STARTS,
        "chain_stages": [{**s, "net": short(s["net"])} for s in stages],
        "matches": matches,
        "fa_prior_independent": fa_indep,
        "fa_prior": fa_report,
        "shift_invariance": inv_report,
        "extra_I_all": extra_report,
        "extra_I_close": extra_close,
        "extra_I_wide": extra_wide,
        "extra_I_triple": triple_report,
        "figures": [p.name for p in figs],
    }
    (OUT / "shift_chain_report.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    def yn(b: bool) -> str:
        return "**yes**" if b else "**no**"

    def gap_table(rows: list[dict]) -> list[str]:
        lines = [
            "| net | linear OR? | nonlinear gaps |",
            "|-----|:----------:|----------------|",
        ]
        for r in rows:
            gaps = ",".join(str(g) for g in r["nonlinear_gaps"]) or "—"
            lines.append(f"| `{r['key']}` | {yn(r['linear_or'])} | {gaps} |")
        return lines

    md = [
        "# Shift-chain inspect (I entry @ cycle 1)",
        "",
        "**Rule:** sticky SET spacing → [`../rules/a31o_sticky_set_spacing.txt`](../rules/a31o_sticky_set_spacing.txt)",
        "(Δ∈{1,10,11,12} + FA gates ⇒ a31o / dfrtp_2_37 sticky sets).",
        "",
        "The A2/B2 path behind `a221o` / `a22o` is a **mux+flop shift register**",
        "fed by `mux2_1_13.A1 = I`. FA-side nets do not carry I; they **gate**",
        "whether a shifted pulse shows up on `a22o.X` / `a221o.X`.",
        "",
        f"- Reference stimulus: **`I=1` at cycle `{I_REF}`** (not 120).",
        f"- Diff window: cycles `0..{COMPARE_CYC - 1}`.",
        f"- FA-prior nets identical for all tested I placements: {yn(fa_indep)}",
        f"- Close gaps Δ∈`{CLOSE_GAPS}` · wide gaps Δ∈`{WIDE_GAPS}` · triples Δ∈`{TRIPLE_GAPS}`",
        "",
        "## Figures",
        "",
        "| Figure | What to look for |",
        "|--------|------------------|",
        "| [`board_I_at_1.png`](board_I_at_1.png) | Full cascade for I@1 |",
        "| [`board_I_spaced_g44.png`](board_I_spaced_g44.png) | Two cascades, Δ=44 |",
        "| [`chain_delay_match.png`](chain_delay_match.png) | Verilog depth == sim delay |",
        "| [`fa_prior_vs_I.png`](fa_prior_vs_I.png) | FA stubs unchanged with I |",
        "| [`time_entry_shift_vs_gated.png`](time_entry_shift_vs_gated.png) | Diagonal shift vs missing C1 pulses |",
        "| [`aligned_invariance.png`](aligned_invariance.png) | After align-to-I@1: taps overlap; gated may not |",
        "| [`extra_I_close_vs_OR.png`](extra_I_close_vs_OR.png) | Close double-I vs OR(singles) |",
        "| [`extra_I_wide_vs_OR.png`](extra_I_wide_vs_OR.png) | **Wide** double-I (Δ up to 88) vs OR |",
        "| [`extra_I_triple_vs_OR.png`](extra_I_triple_vs_OR.png) | **Triple** spaced I vs OR of 3 |",
        "",
        "Structural template scorecard: [`structure_match.md`](structure_match.md).",
        "",
        "## Verilog chain (S=1 path)",
        "",
        "```text",
    ]
    for s in stages:
        md.append(
            f"  [{s['stage']:2d}] +{s['expected_delay']}  {s['kind']:10s}  "
            f"{short(s['net']):28s}  {s['note']}"
        )
    md += ["```", "", "## Delay match (I@1)", "", "| tap | expected | observed | ok |", "|-----|--------:|---------:|:--:|"]
    for m in matches:
        md.append(
            f"| `{m['key']}` | {m['expected']} | {m['observed']} | "
            f"{'✓' if m['ok'] else '✗'} |"
        )

    md += [
        "",
        "## Does behavior depend on I entry cycle?",
        "",
        f"Checked across all single-I starts `{STARTS}` (near + wide).",
        "",
        "| net | group | shift-invariant (aligned to I@1)? |",
        "|-----|-------|:---------------------------------:|",
    ]
    for r in inv_report:
        md.append(
            f"| `{r['key']}` | {r['group']} | {yn(r['shift_invariant'])} |"
        )

    md += [
        "",
        "- **Shift taps** (`a22o.A2` … `a22o.B2`): same shape for every entry cycle;",
        "  only a delay. Matches the Verilog flop chain.",
        "- **Gated** (`a22o.X` / `a221o.X`): **depends on entry cycle**, because",
        "  `a22o.X = (or4.X ∧ A2) ∨ (buf ∧ B2)` and `or4.X` (FA bus) has holes",
        "  on a fixed schedule — an I pulse that arrives when `or4.X=0` is swallowed.",
        "",
        "## Extra I — close gaps",
        "",
        f"Δ ∈ `{CLOSE_GAPS}` (pulses can still interact inside the 12-stage chain).",
        "",
    ]
    md += gap_table(extra_close)
    md += [
        "",
        "## Extra I — wide gaps",
        "",
        f"Δ ∈ `{WIDE_GAPS}` (well past chain length / on or4 hole period).",
        "",
    ]
    md += gap_table(extra_wide)
    md += [
        "",
        "## Extra I — triple spaced",
        "",
        f"I@{{1, 1+Δ, 1+2Δ}} for Δ ∈ `{TRIPLE_GAPS}` vs OR of three singles.",
        "",
    ]
    md += gap_table(triple_report)

    md += [
        "",
        "## FA-prior independence",
        "",
        "These nets are upstream / beside FA and do **not** reach primary `I`.",
        "They must be identical under all0 and every `I@{s}`:",
        "",
    ]
    for r in fa_report:
        st = ",".join(str(s) for s in r["differs_at_starts"]) or "none"
        md.append(f"- `{r['key']}` differs at starts: {st}")

    md += [
        "",
        f"JSON: [`shift_chain_report.json`](shift_chain_report.json)",
        "",
        "Regenerate:",
        "```bash",
        "python3 phase3/a221o_set/match_known_delay_structures.py",
        "python3 phase3/a221o_set/run_shift_chain_inspect.py",
        "```",
        "",
    ]
    md_path = OUT / "README.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    print(f"wrote {md_path}")
    for p in figs:
        print(f"  {p.name}")
    print(f"FA-prior I-independent: {fa_indep}")
    print("matches:", {m["key"]: (m["expected"], m["observed"], m["ok"]) for m in matches})
    print("invariant:", {r["key"]: r["shift_invariant"] for r in inv_report})
    print("wide OR:", {r["key"]: r["linear_or"] for r in extra_wide})
    print("triple OR:", {r["key"]: r["linear_or"] for r in triple_report})


if __name__ == "__main__":
    main()
