#!/usr/bin/env python3
"""Exactly 2 I=1 per period-11 window · randomized spacing sweep · active pins.

For each and4 pin folder:
  - every window W_k = [11k .. 11k+10] gets exactly two ones
  - each sweep mode draws a random (off_a, off_b) pair in 0..10
    and applies that same pair to every window
  - probe an expanded fan-in watch list; plot only non-static lanes
  - always keep the and4-input highlight; ≥ MIN_ACTIVE lanes

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py
  python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py --pin nor3_2_2
"""
from __future__ import annotations

import argparse
import csv
import colorsys
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from probe_timeline import ones, pat_bits, run_probe  # noqa: E402
from rework_paths import savefig_locked  # noqa: E402

BUILD = ROOT / "phase2" / "build"
N_CYC = 121
PERIOD = 11
TAG = "and215_and4_I2win_rand"
SEED = 20260904
N_SWEEP = 16  # randomizations of (off_a, off_b)
MIN_ACTIVE = 7

# Expanded watches (more than active_watches); highlight = PIN_KEY
WATCHES: dict[str, list[tuple[str, str, str]]] = {
    "dfrtp_2_24": [
        ("Q", "sky130_fd_sc_hd__and4_2_3__A", "★ Q → and4.A"),
        ("a32o_X", "sky130_fd_sc_hd__a32o_2_2__X", "a32o.X → flop.D"),
        ("A3", "sky130_fd_sc_hd__and3_2_10__B", "A3  and3_2_10__B"),
        ("B1", "sky130_fd_sc_hd__inv_2_10__Y", "B1  inv_2_10__Y"),
        ("inv10_A", "sky130_fd_sc_hd__inv_2_10__A", "inv_2_10__A"),
        ("or3_A", "sky130_fd_sc_hd__or3_2_8__A", "or3_2_8__A"),
        ("or3_B", "sky130_fd_sc_hd__or3_2_8__B", "or3_2_8__B"),
        ("or3_X", "sky130_fd_sc_hd__or3_2_8__X", "or3_2_8__X"),
        ("nor2_Y", "sky130_fd_sc_hd__nor2_2_30__Y", "nor2_2_30__Y"),
        ("nor2_B", "sky130_fd_sc_hd__nor2_2_30__B", "nor2_2_30__B"),
        ("inv7_A", "sky130_fd_sc_hd__inv_2_7__A", "stub inv_2_7__A"),
        ("and4_B", "sky130_fd_sc_hd__and4_2_3__B", "sib and4.B"),
        ("and4_C", "sky130_fd_sc_hd__and4_2_3__C", "sib and4.C"),
        ("and4_D", "sky130_fd_sc_hd__nor3_2_2__Y", "sib and4.D"),
        ("a21o", "sky130_fd_sc_hd__a21o_2_10__X", "a21o_2_10__X"),
        ("and3_11", "sky130_fd_sc_hd__and3_2_11__X", "and3_2_11__X"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X"),
    ],
    "dfrtp_2_25": [
        ("Q", "sky130_fd_sc_hd__and4_2_3__B", "★ Q → and4.B"),
        ("D", "sky130_fd_sc_hd__dfrtp_2_25__D", "D  and2b_2_10.X"),
        ("A_N", "sky130_fd_sc_hd__and3_2_11__X", "A_N  and3_2_11__X"),
        ("B", "sky130_fd_sc_hd__a21o_2_10__X", "B  a21o_2_10__X"),
        ("and4_A", "sky130_fd_sc_hd__and4_2_3__A", "sib and4.A"),
        ("and4_C", "sky130_fd_sc_hd__and4_2_3__C", "sib and4.C"),
        ("inv10_A", "sky130_fd_sc_hd__inv_2_10__A", "inv_2_10__A"),
        ("a32o_X", "sky130_fd_sc_hd__a32o_2_2__X", "a32o_2_2__X"),
        ("or3_A", "sky130_fd_sc_hd__or3_2_8__A", "or3_2_8__A"),
        ("or3_X", "sky130_fd_sc_hd__or3_2_8__X", "or3_2_8__X"),
        ("A3", "sky130_fd_sc_hd__and3_2_10__B", "and3_2_10__B"),
        ("inv10_Y", "sky130_fd_sc_hd__inv_2_10__Y", "inv_2_10__Y"),
        ("nor2_Y", "sky130_fd_sc_hd__nor2_2_30__Y", "nor2_2_30__Y"),
        ("nor2_B", "sky130_fd_sc_hd__nor2_2_30__B", "nor2_2_30__B"),
        ("o21a", "sky130_fd_sc_hd__o21a_2_11__X", "o21a_2_11__X"),
        ("inv7_A", "sky130_fd_sc_hd__inv_2_7__A", "stub inv_2_7__A"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X"),
    ],
    "dfrtp_2_20": [
        ("Q", "sky130_fd_sc_hd__and4_2_3__C", "★ Q → and4.C"),
        ("xnor_Y", "sky130_fd_sc_hd__xnor2_2_11__Y", "xnor.Y → flop.D"),
        ("xnor_B", "sky130_fd_sc_hd__xnor2_2_11__B", "xnor.B"),
        ("and4_4D", "sky130_fd_sc_hd__and4_2_4__D", "and4_2_4__D"),
        ("inv10_A", "sky130_fd_sc_hd__inv_2_10__A", "inv_2_10__A"),
        ("and4_A", "sky130_fd_sc_hd__and4_2_3__A", "sib and4.A"),
        ("and4_B", "sky130_fd_sc_hd__and4_2_3__B", "sib and4.B"),
        ("and4_D", "sky130_fd_sc_hd__nor3_2_2__Y", "sib and4.D"),
        ("or3_A", "sky130_fd_sc_hd__or3_2_8__A", "or3_2_8__A"),
        ("or3_B", "sky130_fd_sc_hd__or3_2_8__B", "or3_2_8__B"),
        ("or3_C", "sky130_fd_sc_hd__or3_2_8__C", "or3_2_8__C"),
        ("or3_X", "sky130_fd_sc_hd__or3_2_8__X", "or3_2_8__X"),
        ("o21a", "sky130_fd_sc_hd__o21a_2_11__X", "o21a_2_11__X"),
        ("a21o", "sky130_fd_sc_hd__a21o_2_10__X", "a21o_2_10__X"),
        ("and3_11", "sky130_fd_sc_hd__and3_2_11__X", "and3_2_11__X"),
        ("nor2_Y", "sky130_fd_sc_hd__nor2_2_30__Y", "nor2_2_30__Y"),
        ("a32o_X", "sky130_fd_sc_hd__a32o_2_2__X", "a32o_2_2__X"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X"),
    ],
    "nor3_2_2": [
        ("Y", "sky130_fd_sc_hd__nor3_2_2__Y", "★ Y → and4.D"),
        ("A", "sky130_fd_sc_hd__nor3_2_2__A", "A  dfrtp_2_21.Q"),
        ("B", "sky130_fd_sc_hd__nor3_2_2__B", "B  dfrtp_2_19.Q"),
        ("C", "sky130_fd_sc_hd__or3_2_8__X", "C  or3_2_8__X"),
        ("and2b9", "sky130_fd_sc_hd__and2b_2_9__X", "and2b_2_9__X"),
        ("and2b9B", "sky130_fd_sc_hd__and2b_2_9__B", "and2b_2_9__B"),
        ("o21a12", "sky130_fd_sc_hd__o21a_2_12__X", "o21a_2_12__X"),
        ("o21a12A", "sky130_fd_sc_hd__o21a_2_12__A1", "o21a_2_12__A1"),
        ("or3_A", "sky130_fd_sc_hd__or3_2_8__A", "or3_2_8__A"),
        ("or3_B", "sky130_fd_sc_hd__or3_2_8__B", "or3_2_8__B"),
        ("or3_C", "sky130_fd_sc_hd__or3_2_8__C", "or3_2_8__C"),
        ("a31o9", "sky130_fd_sc_hd__a31o_2_9__X", "a31o_2_9__X"),
        ("and4_4X", "sky130_fd_sc_hd__and4_2_4__X", "and4_2_4__X"),
        ("and4_4B", "sky130_fd_sc_hd__and4_2_4__B", "and4_2_4__B"),
        ("and4_4D", "sky130_fd_sc_hd__and4_2_4__D", "and4_2_4__D"),
        ("xor10", "sky130_fd_sc_hd__xor2_2_10__X", "xor2_2_10__X"),
        ("xnor_B", "sky130_fd_sc_hd__xnor2_2_11__B", "xnor2_2_11__B"),
        ("xnor_Y", "sky130_fd_sc_hd__xnor2_2_11__Y", "xnor2_2_11__Y"),
        ("o21a11", "sky130_fd_sc_hd__o21a_2_11__X", "o21a_2_11__X"),
        ("nor2_Y", "sky130_fd_sc_hd__nor2_2_30__Y", "nor2_2_30__Y"),
        ("and4_A", "sky130_fd_sc_hd__and4_2_3__A", "sib and4.A"),
        ("and4_B", "sky130_fd_sc_hd__and4_2_3__B", "sib and4.B"),
        ("and4_C", "sky130_fd_sc_hd__and4_2_3__C", "sib and4.C"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X"),
    ],
}

PIN_KEY = {
    "dfrtp_2_24": "Q",
    "dfrtp_2_25": "Q",
    "dfrtp_2_20": "Q",
    "nor3_2_2": "Y",
}
PIN_AND4 = {
    "dfrtp_2_24": "and4.A",
    "dfrtp_2_25": "and4.B",
    "dfrtp_2_20": "and4.C",
    "nor3_2_2": "and4.D",
}
PIN_TITLE = {
    "dfrtp_2_24": "and4.A · dfrtp_2_24 · a32o_2_2",
    "dfrtp_2_25": "and4.B · dfrtp_2_25 · and2b_2_10",
    "dfrtp_2_20": "and4.C · dfrtp_2_20 · xnor2_2_11",
    "nor3_2_2": "and4.D · nor3_2_2",
}


def palette(n: int) -> list[str]:
    cols = []
    for i in range(n):
        h = (0.02 + 0.85 * i / max(n, 1)) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.72, 0.78)
        cols.append(f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}")
    return cols


def ones_every_window(off_a: int, off_b: int) -> list[int]:
    assert 0 <= off_a < PERIOD and 0 <= off_b < PERIOD and off_a != off_b
    pos: list[int] = []
    for w in range(N_CYC // PERIOD):
        base = w * PERIOD
        pos.append(base + off_a)
        pos.append(base + off_b)
    return sorted(pos)


def build_modes(
    rng: random.Random, n_sweep: int
) -> list[tuple[str, str, list[int], tuple[int, int]]]:
    """(name, bits, ones, (off_lo, off_hi))."""
    out: list[tuple[str, str, list[int], tuple[int, int]]] = [
        ("all0", pat_bits(N_CYC), [], (-1, -1))
    ]
    seen: set[tuple[int, int]] = set()
    tries = 0
    while len(seen) < n_sweep and tries < 500:
        tries += 1
        a, b = rng.sample(range(PERIOD), 2)
        pair = (min(a, b), max(a, b))
        if pair in seen:
            continue
        seen.add(pair)
        pos = ones_every_window(pair[0], pair[1])
        delta = pair[1] - pair[0]
        name = f"I2win_r{len(seen):02d}_off{pair[0]},{pair[1]}_d{delta}"
        out.append((name, pat_bits(N_CYC, pos), pos, pair))
    return out


def fmt(xs: list[int], lim: int = 24) -> str:
    if len(xs) <= lim:
        return str(xs)
    return str(xs[:lim])[:-1] + f", …] (n={len(xs)})"


def all_probes() -> list[tuple[str, str]]:
    seen: set[str] = set()
    probes: list[tuple[str, str]] = [("I", "I"), ("enable", "enable")]
    for pin, watches in WATCHES.items():
        tag = pin.replace("dfrtp_", "f").replace("nor3_", "n")
        for lab, net, _t in watches:
            if net in seen:
                continue
            seen.add(net)
            probes.append((f"{tag}__{lab}", net))
    return probes


def lab_for(pin: str, lane_lab: str, probes: list[tuple[str, str]]) -> str:
    net = next(n for l, n, _t in WATCHES[pin] if l == lane_lab)
    for plab, pnet in probes:
        if pnet == net:
            return plab
    raise KeyError((pin, lane_lab))


def activity_score(rows_all: list[dict], csv_lab: str) -> tuple[bool, int]:
    vals = [int(r[csv_lab]) for r in rows_all]
    if len(set(vals)) <= 1:
        return False, 0
    flips = sum(1 for i in range(1, len(vals)) if vals[i] != vals[i - 1])
    return True, flips


def select_lanes(
    pin: str,
    probes: list[tuple[str, str]],
    rows_all: list[dict],
) -> list[tuple[str, str, str, str]]:
    key = PIN_KEY[pin]
    scored: list[tuple[int, str, str, str]] = []
    for lab, _net, title in WATCHES[pin]:
        csv_lab = lab_for(pin, lab, probes)
        active, flips = activity_score(rows_all, csv_lab)
        scored.append((flips if active else -1, lab, csv_lab, title))

    active = sorted([s for s in scored if s[0] >= 0], key=lambda t: -t[0])
    static = [s for s in scored if s[0] < 0]

    chosen: list[str] = [key]
    for _fl, lab, _c, _t in active:
        if lab not in chosen:
            chosen.append(lab)

    if len(chosen) < MIN_ACTIVE:

        def mid_score(lab: str) -> int:
            csv_lab = lab_for(pin, lab, probes)
            n1 = sum(int(r[csv_lab]) for r in rows_all)
            return -abs(n1 - len(rows_all) // 2)

        for _fl, lab, _c, _t in sorted(static, key=lambda t: mid_score(t[1])):
            if lab not in chosen:
                chosen.append(lab)
            if len(chosen) >= MIN_ACTIVE:
                break

    for lab, _n, _t in WATCHES[pin]:
        if len(chosen) >= MIN_ACTIVE:
            break
        if lab not in chosen:
            chosen.append(lab)

    cols = palette(len(chosen))
    out = []
    for i, lab in enumerate(chosen):
        title = next(t for l, _n, t in WATCHES[pin] if l == lab)
        csv_lab = lab_for(pin, lab, probes)
        col = "#c00000" if lab == key else cols[i]
        out.append((lab, csv_lab, title, col))
    return out


def write_pin(
    pin: str,
    mode_defs: list[tuple[str, str, list[int], tuple[int, int]]],
    by_mode: dict[str, list[dict]],
    probes: list[tuple[str, str]],
) -> None:
    out = HERE / pin / "timelines"
    out.mkdir(parents=True, exist_ok=True)
    key = PIN_KEY[pin]
    and4_name = PIN_AND4[pin]
    ones_by = {n: pos for n, _b, pos, _p in mode_defs}
    pair_by = {n: pair for n, _b, _pos, pair in mode_defs}
    modes = [(n, b) for n, b, _p, _pair in mode_defs]

    rows_all = [r for name, _ in modes for r in by_mode[name]]
    lanes = select_lanes(pin, probes, rows_all)

    all_labs = [lab for lab, _n, _t in WATCHES[pin]]
    out_csv = out / "I2win_rand_spacing.csv"
    fields = ["mode", "cyc"] + all_labs
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in modes:
            for r in by_mode[name]:
                row = {"mode": name, "cyc": r["cyc"]}
                for lab in all_labs:
                    row[lab] = r[lab_for(pin, lab, probes)]
                w.writerow(row)

    hi_yi = next(i for i, (lab, *_r) in enumerate(reversed(lanes)) if lab == key)
    n_m = len(modes)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, 1.5 * n_m), dpi=120, sharex=True)
    if n_m == 1:
        axes = [axes]
    for ax, (name, _) in zip(axes, modes):
        rs = by_mode[name]
        ax.add_patch(
            Rectangle(
                (-0.5, hi_yi - 0.48),
                N_CYC,
                0.96,
                facecolor="#ffe08a",
                edgecolor="#c00000",
                lw=1.4,
                zorder=0,
                alpha=0.55,
            )
        )
        for yi, (lab, csv_lab, title, col) in enumerate(reversed(lanes)):
            highs = [int(r["cyc"]) for r in rs if int(r[csv_lab])]
            for c in highs:
                if lab == key:
                    ax.barh(
                        yi,
                        1.0,
                        left=c - 0.5,
                        height=0.78,
                        color=col,
                        edgecolor="#7a0000",
                        lw=0.6,
                        zorder=3,
                    )
                else:
                    ax.barh(
                        yi, 1.0, left=c - 0.5, height=0.72, color=col, edgecolor="none", zorder=2
                    )
        for p in ones_by[name]:
            ax.axvline(p, color="#c00000", lw=0.55, alpha=0.35, zorder=1)
        for w in range(N_CYC // PERIOD + 1):
            ax.axvline(w * PERIOD - 0.5, color="#bbb", lw=0.55, ls=":", zorder=0)
        ytick_labs, weights = [], []
        for lab, _c, title, _col in reversed(lanes):
            if lab == key:
                ytick_labs.append(f"★ {title}")
                weights.append("bold")
            else:
                ytick_labs.append(title)
                weights.append("normal")
        ax.set_yticks(range(len(lanes)))
        ax.set_yticklabels(ytick_labs, fontsize=5.5, family="monospace")
        for tick, wt in zip(ax.get_yticklabels(), weights):
            tick.set_fontweight(wt)
            if wt == "bold":
                tick.set_color("#7a0000")
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=6.0, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5, zorder=0)
        kx = [int(r["cyc"]) for r in rs if int(r[lab_for(pin, key, probes)])]
        ax4 = lab_for(pin, "and4_X", probes)
        ax4h = [int(r["cyc"]) for r in rs if int(r[ax4])]
        pair = pair_by[name]
        ptxt = f"off={pair}" if pair[0] >= 0 else "—"
        ax.set_title(
            f"{name} · {ptxt} · #I={len(ones_by[name])} · {key}→{and4_name} n={len(kx)} "
            f"first={kx[0] if kx else '—'} · and4.X n={len(ax4h)} · lanes={len(lanes)}",
            fontsize=7.2,
            loc="left",
        )
    axes[-1].set_xlabel(
        f"cycle · dotted=period-11 · exactly 2 I/window · random off sweep "
        f"(seed={SEED}) · yellow/★ = {key} → {and4_name}"
    )
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _c, _t, c in lanes]
        + [Patch(facecolor="#ffe08a", edgecolor="#c00000", label=f"★ {key} → {and4_name}")],
        loc="upper right",
        ncol=min(6, len(lanes)),
        fontsize=5.5,
        frameon=False,
    )
    fig.suptitle(
        f"{PIN_TITLE[pin]} · I2 every window · random spacing ×{len(mode_defs)-1} · "
        f"active pins n={len(lanes)}",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, out / "I2win_rand_spacing.png")

    act_rows = []
    for lab, _n, title in WATCHES[pin]:
        csv_lab = lab_for(pin, lab, probes)
        active, flips = activity_score(rows_all, csv_lab)
        plotted = any(l == lab for l, *_ in lanes)
        act_rows.append((lab, title, active, flips, plotted))

    md = [
        f"# `{pin}` — I2 every window · random spacing sweep",
        "",
        f"{PIN_TITLE[pin]}",
        "",
        f"Exactly **2** `I=1` in every period-`{PERIOD}` window. "
        f"Each of **{len(mode_defs)-1}** modes draws a random offset pair "
        f"`(off_a, off_b)` ∈ `0..{PERIOD-1}` (seed `{SEED}`) and repeats "
        f"it in every window.",
        "",
        f"Probed **{len(WATCHES[pin])}** nets; plotted **{len(lanes)}** "
        f"non-static (≥{MIN_ACTIVE}). Highlight `{key}` → **{and4_name}**.",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "## Sweep pairs",
        "",
        "| mode | offs | Δ | #I |",
        "|------|------|--:|---:|",
    ]
    for name, _b, pos, pair in mode_defs:
        if pair[0] < 0:
            md.append(f"| `{name}` | — | — | 0 |")
        else:
            md.append(
                f"| `{name}` | `{pair[0]},{pair[1]}` | {pair[1]-pair[0]} | {len(pos)} |"
            )
    md += [
        "",
        "## Watch activity",
        "",
        "| lab | title | active? | flips | plotted |",
        "|-----|-------|:-------:|------:|:-------:|",
    ]
    for lab, title, active, flips, plotted in act_rows:
        md.append(
            f"| `{lab}` | {title} | {'yes' if active else 'no'} | "
            f"{flips if active else 0} | {'✓' if plotted else ''} |"
        )
    md += [
        "",
        "## Observe summary",
        "",
        f"| mode | offs | {key} n | first | and4.X n |",
        "|------|------|--------:|------:|---------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        kx = [int(r["cyc"]) for r in rs if int(r[lab_for(pin, key, probes)])]
        ax4h = [int(r["cyc"]) for r in rs if int(r[lab_for(pin, "and4_X", probes)])]
        pair = pair_by[name]
        ptxt = f"{pair[0]},{pair[1]}" if pair[0] >= 0 else "—"
        md.append(
            f"| `{name}` | `{ptxt}` | {len(kx)} | {kx[0] if kx else '—'} | {len(ax4h)} |"
        )
    md += [
        "",
        "Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py",
        f"python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py --pin {pin}",
        "```",
        "",
    ]
    (out / "I2win_rand_spacing.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  {pin}: lanes={len(lanes)}/{len(WATCHES[pin])} → { [l for l,*_ in lanes] }")

    readme = HERE / pin / "README.md"
    if readme.is_file():
        t = readme.read_text(encoding="utf-8")
        link = (
            "- I2 every window · random spacing sweep (active pins): "
            "[`timelines/I2win_rand_spacing.md`](timelines/I2win_rand_spacing.md)"
        )
        if "I2win_rand_spacing" not in t:
            needle = "active_watches.md`)](timelines/active_watches.md)\n"
            if needle in t:
                t = t.replace(needle, needle + link + "\n")
            else:
                t = t.rstrip() + "\n\n" + link + "\n"
            if "run_I2win_rand_spacing_timeline.py" not in t:
                t = t.replace(
                    "```bash\n",
                    "```bash\n"
                    "python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py\n",
                    1,
                )
            readme.write_text(t, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pin", choices=sorted(WATCHES.keys()))
    ap.add_argument("--sweep", type=int, default=N_SWEEP)
    args = ap.parse_args()
    pins = [args.pin] if args.pin else list(WATCHES.keys())
    n_sweep = args.sweep

    rng = random.Random(SEED)
    mode_defs = build_modes(rng, n_sweep)
    modes = [(n, b) for n, b, _p, _pair in mode_defs]
    probes = all_probes()
    print(
        f"probes={len(probes)} modes={len(modes)} "
        f"sweep={n_sweep} pins={pins} seed={SEED}"
    )
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=BUILD / "and4_I2win_rand",
        tag=TAG,
        probes=probes,
        modes=modes,
        n_cyc=N_CYC,
    )
    by_mode = {name: [r for r in rows if r["mode_name"] == name] for name, _ in modes}
    for pin in pins:
        write_pin(pin, mode_defs, by_mode, probes)
    print("done")


if __name__ == "__main__":
    main()
