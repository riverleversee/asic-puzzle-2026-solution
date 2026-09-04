#!/usr/bin/env python3
"""Phase 3 — sweep k ones on FA open windows; watch sticky leaf A/B/Y.

For each sticky leaf in selected hasI groups:
  - put I=1 on the first k open cycles
  - watch input pins (A_N/B for and2b, A/B for and2) and leaf Y

Default groups: t01, t02, t05 (set_once and2b). Also supports t03/t04 (sticky_or and2).

Usage (from rework_coded/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 phase3/and4b/groups/run_k_ones.py
  python3 phase3/and4b/groups/run_k_ones.py --groups 3 4 --k-max 5
"""
from __future__ import annotations

import argparse
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
ROOT = _p  # rework_coded/
import sys
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))
REPO = ROOT.parent

from run_sim import find_iverilog  # noqa: E402
from structural_drivers import parse_structural  # noqa: E402
from rework_paths import savefig_locked  # noqa: E402

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
PDK = REPO / "netlist" / "structural" / "pdk"
INC = PDK / "include"
SUMMARY = ROOT / "phase2" / "and4b" / "groups" / "summary.json"
OPENS_JSON = REPO / "sim" / "opens_exact_shift1.json"
RETRACE = REPO / "sim" / "retrace_all22_opens_structural.json"
GROUPS = HERE
BUILD = ROOT / "phase3" / "build"
N_CYC = 121
DEFAULT_GROUP_IDX = (1, 2, 5)
DEFAULT_K_MAX = 6
K_VALUES: tuple[int, ...] = tuple(range(1, DEFAULT_K_MAX + 1))

# Magic out-pin → leaf name
OUT_TO_LEAF: dict[str, str] = {}
for _p in "ABCD":
    OUT_TO_LEAF[f"and4_2_0__{_p}"] = f"slot.0.{_p}"
    OUT_TO_LEAF[f"and4_2_1__{_p}"] = f"slot.1.{_p}"
    OUT_TO_LEAF[f"and4_2_5__{_p}"] = f"a5.{_p}"
    OUT_TO_LEAF[f"and4_2_6__{_p}"] = f"a6.{_p}"
for _p in "ABC":
    OUT_TO_LEAF[f"and3_2_5__{_p}"] = f"and3.{_p}"
    OUT_TO_LEAF[f"and3_2_12__{_p}"] = f"a12.{_p}"


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def full(n: str) -> str:
    return n if n.startswith("sky130_") or n in ("I", "enable") else f"sky130_fd_sc_hd__{n}"


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
    val = sum(1 << c for c in ones if 0 <= c < N_CYC)
    return format(val, f"0{N_CYC}b")


def load_leaf_opens() -> dict[str, dict]:
    opens = {r["name"]: r for r in json.loads(OPENS_JSON.read_text(encoding="utf-8"))["opens"]}
    retrace = {
        r["name"]: r for r in json.loads(RETRACE.read_text(encoding="utf-8"))["opens"]
    }
    out = {}
    for name, o in opens.items():
        rt = retrace.get(name) or {}
        # Prefer full all0 open list from rework FA watch when present; else JSON.
        # Do not drop cycles 0 or 120 — rework has not shown them invalid.
        raw = list(o.get("opens_all0") or [])
        out[name] = {
            "opens": raw,
            "open_net": o.get("open_net") or rt.get("open_net"),
            "open_when": int(rt.get("open_when", 1)),
            "kind": o.get("kind"),
            "bank": o.get("bank"),
            "phase": o.get("phase") or rt.get("phase"),
        }
    return out


def build_members(drivers: dict, leaf_meta: dict, group_idx: set[int]) -> list[dict]:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    members: list[dict] = []
    by_inst = {
        short(info["instance"]): (net, info)
        for net, info in drivers.items()
        if info.get("instance")
    }
    for t in summary["types"]:
        if t["index"] not in group_idx:
            continue
        for m in t["members"]:
            inst = m["instance"]
            if inst not in by_inst:
                raise SystemExit(f"instance not in drivers: {inst}")
            net, info = by_inst[inst]
            pins = info.get("in_pins") or {}
            leaf = OUT_TO_LEAF.get(m["out_net"])
            if not leaf or leaf not in leaf_meta:
                raise SystemExit(f"no leaf meta for {inst} out={m['out_net']}")
            lm = leaf_meta[leaf]
            opens = lm["opens"]
            if not opens:
                raise SystemExit(f"{leaf} has empty opens_all0")
            open_net = lm["open_net"]
            phase = lm.get("phase")
            # set_once / deep sticky_or: real open_net probe
            # shallow sticky_or: open iff or4_2_4 == phase (no single open_net)
            if open_net:
                open_lab = short(open_net)
            elif phase and len(str(phase)) == 4 and set(str(phase)) <= {"0", "1"}:
                open_lab = f"or4_2_4=={phase}"
                open_net = None
            else:
                raise SystemExit(f"{leaf} has no open_net / phase")
            # and2b: A_N × B ; and2 (sticky_or): A × B
            if "A_N" in pins and "B" in pins:
                pin_a_lab, pin_a = "A_N", full(pins["A_N"])
            elif "A" in pins and "B" in pins:
                pin_a_lab, pin_a = "A", full(pins["A"])
            else:
                raise SystemExit(f"{inst}: expected A_N/B or A/B pins, got {sorted(pins)}")
            slug = leaf.replace(".", "_")
            members.append(
                {
                    "group": t["index"],
                    "folder": t["folder"],
                    "label": t["label"],
                    "instance": inst,
                    "leaf": leaf,
                    "slug": slug,
                    "Y": net,
                    "AN": pin_a,  # A_N or A
                    "pin_a_lab": pin_a_lab,
                    "B": full(pins["B"]),
                    "open": open_net,
                    "open_lab": open_lab,
                    "open_when": lm["open_when"],
                    "opens": opens,
                    "kind": lm.get("kind"),
                    "phase": phase,
                }
            )
    return members


def collapse_keep(opens: list[int], timelines: dict[str, list[int]], pad: int = 1) -> list[int]:
    """Cycles to keep: open neighborhoods + any AN/B/Y/I transition."""
    keep: set[int] = set()
    for c in opens:
        for d in range(-pad, pad + 1):
            if 0 <= c + d < N_CYC:
                keep.add(c + d)
    # transitions across all k timelines for this leaf
    for series in timelines.values():
        prev = None
        for c, v in enumerate(series):
            if prev is None or v != prev:
                keep.add(c)
                if c > 0:
                    keep.add(c - 1)
                if c + 1 < N_CYC:
                    keep.add(c + 1)
            prev = v
    return sorted(keep)


def plot_group_figure(
    group: int,
    members: list[dict],
    by_mode: dict[str, list[dict]],
    out_png: Path,
) -> None:
    """One leaf per row-block; within block, k=1..6 with AN/B/Y lanes; x collapsed."""
    mems = [m for m in members if m["group"] == group]
    n_leaf = len(mems)
    # layout: each leaf gets 6 (k) * 3 (signals) lanes + gaps
    lanes_per_leaf = len(K_VALUES) * 3 + 1
    total_lanes = n_leaf * lanes_per_leaf
    fig_h = max(8.0, 0.22 * total_lanes + 1.8)
    fig, ax = plt.subplots(figsize=(14, fig_h), dpi=140)

    colors = {"AN": "#1f4e79", "B": "#c45911", "Y": "#2e7d32", "I": "#111111"}
    ytick_pos: list[float] = []
    ytick_lab: list[str] = []
    yi = 0.0

    for mi, m in enumerate(mems):
        # gather timelines for collapse
        timelines: dict[str, list[int]] = {}
        for k in K_VALUES:
            mode = f"t{group:02d}_{m['slug']}_k{k}"
            rows = by_mode[mode]
            timelines[f"AN_k{k}"] = [int(r[f"AN_{m['slug']}"]) for r in rows]
            timelines[f"B_k{k}"] = [int(r[f"B_{m['slug']}"]) for r in rows]
            timelines[f"Y_k{k}"] = [int(r[f"Y_{m['slug']}"]) for r in rows]
            timelines[f"I_k{k}"] = [int(r["I"]) for r in rows]
        keep = collapse_keep(m["opens"], timelines, pad=1)
        # display x: contiguous index; mark breaks
        xpos = {c: i for i, c in enumerate(keep)}
        breaks = []
        for i in range(1, len(keep)):
            if keep[i] != keep[i - 1] + 1:
                breaks.append(i - 0.5)

        # leaf separator
        if mi > 0:
            ax.axhline(yi - 0.55, color="#888888", lw=0.9, zorder=1)

        # leaf label at mid of block
        block_mid = yi + (len(K_VALUES) * 3 - 1) / 2
        ax.text(
            -0.8,
            block_mid,
            f"{m['leaf']}\n{m['instance']}",
            ha="right",
            va="center",
            fontsize=7,
            family="monospace",
            color="#333333",
        )

        for k in K_VALUES:
            mode = f"t{group:02d}_{m['slug']}_k{k}"
            rows = by_mode[mode]
            ones = set(m["opens"][:k])
            for sig, key in (("AN", f"AN_{m['slug']}"), ("B", f"B_{m['slug']}"), ("Y", f"Y_{m['slug']}")):
                vals = [int(r[key]) for r in rows]
                # draw high segments on collapsed x
                for i, c in enumerate(keep):
                    if vals[c]:
                        ax.barh(
                            yi,
                            1.0,
                            left=i - 0.5,
                            height=0.78,
                            color=colors[sig],
                            edgecolor="none",
                            alpha=0.9,
                            zorder=2,
                        )
                # I=1 markers on this k's open hits
                if sig == "Y":
                    for c in ones:
                        if c in xpos:
                            ax.plot(
                                xpos[c],
                                yi,
                                marker="|",
                                color="#111111",
                                ms=9,
                                mew=1.4,
                                zorder=4,
                            )
                ytick_pos.append(yi)
                ytick_lab.append(f"k{k} {sig}")
                yi += 1.0
            yi += 0.35  # gap between k groups within leaf — actually we want tight; small gap only between k
            # undo last extra — keep k blocks tight: remove the +=0.35 and use tiny gap
            yi -= 0.15

        yi += 0.7  # gap between leaves

        # draw break markers for this leaf's x (same keep for whole leaf)
        for b in breaks:
            ax.axvline(b, color="#cccccc", lw=0.7, ls=":", zorder=0)

        # open reference ticks (all opens) on a faint baseline under first k of leaf
        # (already marked I ones on Y)

    ax.set_yticks(ytick_pos)
    ax.set_yticklabels(ytick_lab, fontsize=5.5, family="monospace")
    ax.set_xlim(-0.5, max(len(collapse_keep(mems[0]["opens"], {}, 1)), 1))
    # widen to max keep length across leaves
    max_x = 0
    for m in mems:
        timelines = {}
        for k in K_VALUES:
            mode = f"t{group:02d}_{m['slug']}_k{k}"
            rows = by_mode[mode]
            timelines[f"AN_k{k}"] = [int(r[f"AN_{m['slug']}"]) for r in rows]
            timelines[f"B_k{k}"] = [int(r[f"B_{m['slug']}"]) for r in rows]
            timelines[f"Y_k{k}"] = [int(r[f"Y_{m['slug']}"]) for r in rows]
        max_x = max(max_x, len(collapse_keep(m["opens"], timelines, pad=1)))
    ax.set_xlim(-0.5, max_x - 0.5)

    # x ticks: use first leaf's keep labels as approximate — better per-leaf
    # Show sparse real-cycle labels from first leaf
    m0 = mems[0]
    timelines0 = {}
    for k in K_VALUES:
        mode = f"t{group:02d}_{m0['slug']}_k{k}"
        rows = by_mode[mode]
        timelines0[f"Y_k{k}"] = [int(r[f"Y_{m0['slug']}"]) for r in rows]
    keep0 = collapse_keep(m0["opens"], timelines0, pad=1)
    tick_idx = list(range(0, len(keep0), max(1, len(keep0) // 16)))
    ax.set_xticks([i for i in tick_idx if i < max_x])
    ax.set_xticklabels([str(keep0[i]) if i < len(keep0) else "" for i in tick_idx if i < max_x], fontsize=7)
    ax.set_xlabel("cycle (gate-off gaps collapsed; | = I=1 on an open)", fontsize=9)
    ax.set_title(
        f"t{group:02d} and2b — A_N / B flops + Y vs k=1..6 ones on FA opens\n"
        f"(empty closed-gate space collapsed)",
        fontsize=11,
    )
    ax.invert_yaxis()
    ax.legend(
        handles=[
            Patch(facecolor=colors["AN"], label="A_N flop"),
            Patch(facecolor=colors["B"], label="B flop"),
            Patch(facecolor=colors["Y"], label="and2b Y"),
        ],
        loc="upper right",
        fontsize=8,
    )
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    savefig_locked(fig, out_png)
    print(f"wrote {out_png}")


def _a_col(slug: str, row: dict) -> str:
    """Probe column for the A-side pin (AN_* from k-ones, A_* from gap tools)."""
    if f"AN_{slug}" in row:
        return f"AN_{slug}"
    return f"A_{slug}"


def plot_ab_y_lane_variants(
    mems: list[dict],
    by_mode: dict[str, list[dict]],
    variant_fn,
    out_png: Path,
    title: str,
) -> None:
    """k-ones-style figure: one subplot per leaf; each variant = A/B/Y lanes.

    variant_fn(m) -> list of (mode_label, row_prefix, ones:set[int])
    """
    n = len(mems)
    # estimate lanes for height
    n_var = max((len(variant_fn(m)) for m in mems), default=1)
    lanes = n_var * 3
    fig_h = max(0.22 * lanes * n + 1.5, 6.0)
    fig, axes = plt.subplots(n, 1, figsize=(14, fig_h), dpi=140, sharex=False)
    if n == 1:
        axes = [axes]
    colors = {"A": "#1f4e79", "B": "#c45911", "Y": "#2e7d32"}

    for ax, m in zip(axes, mems):
        variants = variant_fn(m)
        slug = m["slug"]
        timelines: dict[str, list[int]] = {}
        mode_rows: dict[str, list[dict]] = {}
        for mode, _pref, _ones in variants:
            rows = by_mode[mode]
            mode_rows[mode] = rows
            acol = _a_col(slug, rows[0])
            timelines[f"A_{mode}"] = [int(r[acol]) for r in rows]
            timelines[f"B_{mode}"] = [int(r[f"B_{slug}"]) for r in rows]
            timelines[f"Y_{mode}"] = [int(r[f"Y_{slug}"]) for r in rows]
        keep = collapse_keep(m["opens"], timelines, pad=1)
        breaks = [i - 0.5 for i in range(1, len(keep)) if keep[i] != keep[i - 1] + 1]

        yi = 0.0
        yticks: list[float] = []
        ylabels: list[str] = []
        for mode, pref, ones in variants:
            rows = mode_rows[mode]
            acol = _a_col(slug, rows[0])
            for sig, key in (("A", acol), ("B", f"B_{slug}"), ("Y", f"Y_{slug}")):
                vals = [int(r[key]) for r in rows]
                for i, c in enumerate(keep):
                    if vals[c]:
                        ax.barh(
                            yi,
                            1.0,
                            left=i - 0.5,
                            height=0.82,
                            color=colors[sig],
                            edgecolor="none",
                            zorder=2,
                        )
                if sig == "Y":
                    for c in ones:
                        if c in keep:
                            ax.plot(
                                keep.index(c),
                                yi,
                                marker="|",
                                color="#000000",
                                ms=10,
                                mew=1.6,
                                zorder=4,
                            )
                yticks.append(yi)
                pin = m.get("pin_a_lab", "A") if sig == "A" else sig
                ylabels.append(f"{pref}  {pin}")
                yi += 1.0
            yi += 0.25

        for b in breaks:
            ax.axvline(b, color="#dddddd", lw=0.8, ls=":", zorder=0)

        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels, fontsize=6.5, family="monospace")
        ax.set_xlim(-0.5, len(keep) - 0.5)
        ax.invert_yaxis()
        open_lab = m.get("open_lab") or (
            short(m["open"]) if m.get("open") else "?"
        )
        ax.set_title(
            f"{m['leaf']}  ·  `{m['instance']}` → `{short(m['Y'])}`   "
            f"{m.get('pin_a_lab', 'A')}=`{short(m['AN'])}`  B=`{short(m['B'])}`  "
            f"open=`{open_lab}`",
            fontsize=8,
            loc="left",
            family="monospace",
        )
        open_ticks = [keep.index(c) for c in m["opens"] if c in keep]
        open_labs = [str(c) for c in m["opens"] if c in keep]
        ax.set_xticks(open_ticks)
        ax.set_xticklabels(open_labs, fontsize=6, rotation=90)
        ax.grid(axis="x", color="#f0f0f0", lw=0.5, zorder=0)

    pin_a = mems[0].get("pin_a_lab", "A") if mems else "A"
    axes[-1].set_xlabel("open cycles (gate-off gaps collapsed; | = I=1)")
    fig.suptitle(title, fontsize=12, y=0.995)
    fig.legend(
        handles=[
            Patch(facecolor=colors["A"], label=pin_a),
            Patch(facecolor=colors["B"], label="B"),
            Patch(facecolor=colors["Y"], label="Y"),
        ],
        loc="upper right",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    savefig_locked(fig, out_png)
    print(f"wrote {out_png}")


def plot_group_figure_v2(
    group: int,
    members: list[dict],
    by_mode: dict[str, list[dict]],
    out_png: Path,
) -> None:
    """Clearer layout: one subplot per leaf; rows=k; lanes AN/B/Y; shared collapsed x."""
    mems = [m for m in members if m["group"] == group]

    def variant_fn(m: dict) -> list[tuple[str, str, set[int]]]:
        out = []
        for k in K_VALUES:
            mode = f"t{group:02d}_{m['slug']}_k{k}"
            out.append((mode, f"k={k}", set(m["opens"][:k])))
        return out

    k_lo, k_hi = K_VALUES[0], K_VALUES[-1]
    pin_a = mems[0]["pin_a_lab"] if mems else "A_N"
    plot_ab_y_lane_variants(
        mems,
        by_mode,
        variant_fn,
        out_png,
        f"t{group:02d} — {pin_a} / B + Y while placing k={k_lo}..{k_hi} ones on FA opens",
    )


def main() -> None:
    global K_VALUES
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--groups",
        type=int,
        nargs="+",
        default=list(DEFAULT_GROUP_IDX),
        help="hasI type indices (default: 1 2 5)",
    )
    ap.add_argument(
        "--k-max",
        type=int,
        default=DEFAULT_K_MAX,
        help="place ones on first 1..k_max open cycles (default: 6)",
    )
    args = ap.parse_args()
    group_idx = set(args.groups)
    if args.k_max < 1:
        raise SystemExit("--k-max must be >= 1")
    K_VALUES = tuple(range(1, args.k_max + 1))

    drivers, _stubs, meta = parse_structural()
    print("structural:", meta)
    leaf_meta = load_leaf_opens()
    members = build_members(drivers, leaf_meta, group_idx)
    print(f"members: {len(members)}  groups={sorted(group_idx)}  k=1..{args.k_max}")

    BUILD.mkdir(parents=True, exist_ok=True)
    GROUPS.mkdir(parents=True, exist_ok=True)

    # Probes: I, enable, per-member open/AN/B/Y
    # (phase-only sticky_or leaves have no single open_net — synthesize later)
    probes: list[tuple[str, str]] = [("I", "I"), ("enable", "enable")]
    for m in members:
        if m["open"]:
            probes.append((f"op_{m['slug']}", m["open"]))
        probes += [
            (f"AN_{m['slug']}", m["AN"]),
            (f"B_{m['slug']}", m["B"]),
            (f"Y_{m['slug']}", m["Y"]),
        ]

    # Patterns: one mode per (member, k)
    pats: list[tuple[str, str]] = []
    for m in members:
        for k in K_VALUES:
            ones = set(m["opens"][:k])
            lab = f"t{m['group']:02d}_{m['slug']}_k{k}"
            pats.append((lab, bits_from_ones(ones)))

    pats_path = BUILD / "pats_k_ones_flops.txt"
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

    csv_raw = BUILD / "probe_k_ones_flops.csv"
    tb = BUILD / "tb_k_ones_flops.v"
    vvp = BUILD / "tb_k_ones_flops.vvp"

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
        row["label"] = lab
        by_mode[lab].append(row)

    # Synthesize open probe for phase-only sticky_or leaves (open_net was null).
    open_sets = {m["slug"]: set(m["opens"]) for m in members if not m["open"]}
    if open_sets:
        for lab, rows in by_mode.items():
            for slug, opens in open_sets.items():
                key = f"op_{slug}"
                for row in rows:
                    row[key] = "1" if int(row["cyc"]) in opens else "0"

    # Per-group summary + figures
    for gi in sorted(group_idx):
        mems = [m for m in members if m["group"] == gi]
        if not mems:
            print(f"skip t{gi:02d}: no members")
            continue
        folder = mems[0]["folder"]
        gdir = GROUPS / folder
        gdir.mkdir(parents=True, exist_ok=True)

        pin_a = mems[0]["pin_a_lab"]
        k_lo, k_hi = K_VALUES[0], K_VALUES[-1]
        if pin_a == "A_N":
            y_eq = "`Y = (¬A_N) ∧ B`"
        else:
            y_eq = "`Y = A ∧ B`"
        md = [
            f"# k-ones flop watch — t{gi:02d}",
            "",
            f"Group: `{mems[0]['label']}`",
            "",
            f"For each leaf, place `I=1` on the first **k** FA-open cycles "
            f"(k={k_lo}..{k_hi}). Watch **{pin_a}**, **B**, **Y** "
            f"({y_eq}).",
            "",
            f"Figure: [`k_ones_flops_timeline.png`](k_ones_flops_timeline.png)",
            "",
        ]
        for m in mems:
            md += [
                f"## `{m['leaf']}` (`{m['instance']}`)",
                "",
                f"- {m['pin_a_lab']} ← `{short(m['AN'])}`",
                f"- B ← `{short(m['B'])}`",
                f"- Y → `{short(m['Y'])}`",
                f"- open: `{m['open_lab']}`",
                f"- opens: `{m['opens']}`",
                "",
                f"| k | I@opens | Y first↑ | Y last | {m['pin_a_lab']} final | B final | Y high cycles |",
                "|--:|---------|---------:|-------:|----------:|--------:|--------------:|",
            ]
            for k in K_VALUES:
                mode = f"t{gi:02d}_{m['slug']}_k{k}"
                rows = by_mode[mode]
                ys = [int(r[f"Y_{m['slug']}"]) for r in rows]
                ans = [int(r[f"AN_{m['slug']}"]) for r in rows]
                bs = [int(r[f"B_{m['slug']}"]) for r in rows]
                first_up = next((c for c, v in enumerate(ys) if v), None)
                last_hi = max((c for c, v in enumerate(ys) if v), default=None)
                md.append(
                    f"| {k} | `{m['opens'][:k]}` | {first_up} | {last_hi} | "
                    f"{ans[-1]} | {bs[-1]} | {sum(ys)} |"
                )
            md.append("")

        (gdir / "k_ones_flops.md").write_text("\n".join(md), encoding="utf-8")

        # CSV dump for group
        out_csv = gdir / "k_ones_flops.csv"
        fields = ["label", "mode", "cyc", "I", "enable"]
        for m in mems:
            fields += [f"op_{m['slug']}", f"AN_{m['slug']}", f"B_{m['slug']}", f"Y_{m['slug']}"]
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for m in mems:
                for k in K_VALUES:
                    mode = f"t{gi:02d}_{m['slug']}_k{k}"
                    for row in by_mode[mode]:
                        w.writerow({k_: row.get(k_, "") for k_ in fields})

        png = gdir / "k_ones_flops_timeline.png"
        plot_group_figure_v2(gi, members, by_mode, png)
        dest = GROUPS / f"t{gi:02d}_k_ones_flops_timeline.png"
        dest.write_bytes(png.read_bytes())
        print(f"copied {dest}")

    # Index blurb (rewrite k-ones section if present)
    idx_path = GROUPS / "README.md"
    text = idx_path.read_text(encoding="utf-8") if idx_path.exists() else ""
    k_lo, k_hi = K_VALUES[0], K_VALUES[-1]
    lines = [
        f"## k-ones flop timelines\n",
        f"Sweep `I=1` on the first k FA-open cycles (k={k_lo}..{k_hi}); "
        "watch A_N/B/Y (and2b) or A/B/Y (and2).\n",
        "```bash",
        "python3 phase3/and4b/groups/run_k_ones.py",
        "python3 phase3/and4b/groups/run_k_ones.py --groups 3 4 --k-max 5",
        "```\n",
    ]
    for gi in sorted(group_idx):
        mems = [m for m in members if m["group"] == gi]
        if not mems:
            continue
        folder = mems[0]["folder"]
        lines.append(
            f"- t{gi:02d}: [`{folder}/k_ones_flops_timeline.png`]"
            f"({folder}/k_ones_flops_timeline.png)"
        )
    blurb = "\n".join(lines) + "\n"
    marker = "## k-ones flop timelines"
    if marker in text:
        pre, _, rest = text.partition(marker)
        nxt = rest.find("\n## ")
        after = rest[nxt + 1 :] if nxt >= 0 else ""
        text = pre.rstrip() + "\n\n" + blurb + ("\n" + after if after else "\n")
    else:
        text = text.rstrip() + "\n\n" + blurb + "\n"
    idx_path.write_text(text, encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
