#!/usr/bin/env python3
"""Exactly 2 I=1 per period-11 window · per-window random offs · active pins.

Unlike I2win_rand_spacing (one offset pair repeated every window), each
window independently draws (off_a, off_b). Sweep = different RNG streams.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py
  python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py --pin dfrtp_2_25
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

from probe_timeline import pat_bits, run_probe  # noqa: E402
from rework_paths import savefig_locked  # noqa: E402

# Reuse expanded watches / helpers from the fixed-pair I2win runner
sys.path.insert(0, str(HERE))
from run_I2win_rand_spacing_timeline import (  # noqa: E402
    MIN_ACTIVE,
    PIN_AND4,
    PIN_KEY,
    PIN_TITLE,
    WATCHES,
    activity_score,
    all_probes,
    fmt,
    lab_for,
    palette,
    select_lanes,
)

BUILD = ROOT / "phase2" / "build"
N_CYC = 121
PERIOD = 11
N_WIN = N_CYC // PERIOD
TAG = "and215_and4_I2win_pwrand"
SEED = 20260904
N_SWEEP = 16


def ones_per_window_independent(rng: random.Random) -> tuple[list[int], list[tuple[int, int]]]:
    """Exactly 2 ones per window; each window draws its own (off_lo, off_hi)."""
    pos: list[int] = []
    pairs: list[tuple[int, int]] = []
    for w in range(N_WIN):
        a, b = rng.sample(range(PERIOD), 2)
        pair = (min(a, b), max(a, b))
        pairs.append(pair)
        base = w * PERIOD
        pos.append(base + pair[0])
        pos.append(base + pair[1])
    return sorted(pos), pairs


def build_modes(
    seed: int, n_sweep: int
) -> list[tuple[str, str, list[int], list[tuple[int, int]]]]:
    out: list[tuple[str, str, list[int], list[tuple[int, int]]]] = [
        ("all0", pat_bits(N_CYC), [], [])
    ]
    for i in range(1, n_sweep + 1):
        # independent stream per mode
        rng = random.Random(seed + 10007 * i)
        pos, pairs = ones_per_window_independent(rng)
        deltas = [p[1] - p[0] for p in pairs]
        name = f"I2pw_r{i:02d}_d{min(deltas)}-{max(deltas)}"
        out.append((name, pat_bits(N_CYC, pos), pos, pairs))
    return out


def pairs_fmt(pairs: list[tuple[int, int]], lim: int = 11) -> str:
    if not pairs:
        return "—"
    bits = [f"{a},{b}" for a, b in pairs]
    if len(bits) <= lim:
        return "[" + "; ".join(bits) + "]"
    return "[" + "; ".join(bits[:lim]) + "; …]"


def write_pin(
    pin: str,
    mode_defs: list[tuple[str, str, list[int], list[tuple[int, int]]]],
    by_mode: dict[str, list[dict]],
    probes: list[tuple[str, str]],
) -> None:
    out = HERE / pin / "timelines"
    out.mkdir(parents=True, exist_ok=True)
    key = PIN_KEY[pin]
    and4_name = PIN_AND4[pin]
    ones_by = {n: pos for n, _b, pos, _pairs in mode_defs}
    pairs_by = {n: pairs for n, _b, _pos, pairs in mode_defs}
    modes = [(n, b) for n, b, _p, _pairs in mode_defs]

    rows_all = [r for name, _ in modes for r in by_mode[name]]
    lanes = select_lanes(pin, probes, rows_all)

    all_labs = [lab for lab, _n, _t in WATCHES[pin]]
    out_csv = out / "I2win_perwindow_rand.csv"
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
        for w in range(N_WIN + 1):
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
        ax4h = [int(r["cyc"]) for r in rs if int(r[lab_for(pin, "and4_X", probes)])]
        pairs = pairs_by[name]
        dspan = "—"
        if pairs:
            ds = [p[1] - p[0] for p in pairs]
            dspan = f"Δ∈[{min(ds)},{max(ds)}]"
        ax.set_title(
            f"{name} · {dspan} · #I={len(ones_by[name])} · {key}→{and4_name} n={len(kx)} "
            f"first={kx[0] if kx else '—'} · and4.X n={len(ax4h)} · lanes={len(lanes)}",
            fontsize=7.2,
            loc="left",
        )
    axes[-1].set_xlabel(
        f"cycle · dotted=period-11 · 2 I/window · per-window random offs "
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
        f"{PIN_TITLE[pin]} · I2/window · per-window random start+spacing ×{len(mode_defs)-1}",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, out / "I2win_perwindow_rand.png")

    act_rows = []
    for lab, _n, title in WATCHES[pin]:
        csv_lab = lab_for(pin, lab, probes)
        active, flips = activity_score(rows_all, csv_lab)
        plotted = any(l == lab for l, *_ in lanes)
        act_rows.append((lab, title, active, flips, plotted))

    md = [
        f"# `{pin}` — I2 every window · **per-window** random start + spacing",
        "",
        f"{PIN_TITLE[pin]}",
        "",
        f"Exactly **2** `I=1` in every period-`{PERIOD}` window, but "
        f"**each window independently** draws `(off_a, off_b)` ∈ `0..{PERIOD-1}` "
        f"(not a repeated pair). Sweep = `{len(mode_defs)-1}` RNG streams "
        f"(seed `{SEED}`).",
        "",
        "Contrast: [`I2win_rand_spacing.md`](I2win_rand_spacing.md) uses one "
        "offset pair for all windows.",
        "",
        f"Probed **{len(WATCHES[pin])}** nets; plotted **{len(lanes)}** "
        f"non-static (≥{MIN_ACTIVE}). Highlight `{key}` → **{and4_name}**.",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "## Per-mode window offset pairs",
        "",
        "| mode | #I | per-window offs `(lo,hi)` ×11 | Δ range |",
        "|------|---:|-------------------------------|---------|",
    ]
    for name, _b, pos, pairs in mode_defs:
        if not pairs:
            md.append(f"| `{name}` | 0 | — | — |")
        else:
            ds = [p[1] - p[0] for p in pairs]
            md.append(
                f"| `{name}` | {len(pos)} | `{pairs_fmt(pairs)}` | "
                f"`[{min(ds)},{max(ds)}]` |"
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
        f"| mode | {key} n | first | and4.X n |",
        "|------|--------:|------:|---------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        kx = [int(r["cyc"]) for r in rs if int(r[lab_for(pin, key, probes)])]
        ax4h = [int(r["cyc"]) for r in rs if int(r[lab_for(pin, "and4_X", probes)])]
        md.append(
            f"| `{name}` | {len(kx)} | {kx[0] if kx else '—'} | {len(ax4h)} |"
        )
    md += [
        "",
        "Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py",
        f"python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py --pin {pin}",
        "```",
        "",
    ]
    (out / "I2win_perwindow_rand.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  {pin}: lanes={len(lanes)}/{len(WATCHES[pin])}")

    readme = HERE / pin / "README.md"
    if readme.is_file():
        t = readme.read_text(encoding="utf-8")
        link = (
            "- I2 every window · **per-window** random offs (active pins): "
            "[`timelines/I2win_perwindow_rand.md`](timelines/I2win_perwindow_rand.md)"
        )
        if "I2win_perwindow_rand" not in t:
            if "I2win_rand_spacing.md" in t:
                t = t.replace(
                    "I2win_rand_spacing.md`)](timelines/I2win_rand_spacing.md)\n",
                    "I2win_rand_spacing.md`)](timelines/I2win_rand_spacing.md)\n"
                    + link
                    + "\n",
                )
            else:
                t = t.rstrip() + "\n\n" + link + "\n"
            if "run_I2win_perwindow_rand_timeline.py" not in t:
                t = t.replace(
                    "```bash\n",
                    "```bash\n"
                    "python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py\n",
                    1,
                )
            readme.write_text(t, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pin", choices=sorted(WATCHES.keys()))
    ap.add_argument("--sweep", type=int, default=N_SWEEP)
    args = ap.parse_args()
    pins = [args.pin] if args.pin else list(WATCHES.keys())

    mode_defs = build_modes(SEED, args.sweep)
    modes = [(n, b) for n, b, _p, _pairs in mode_defs]
    probes = all_probes()
    print(
        f"probes={len(probes)} modes={len(modes)} "
        f"sweep={args.sweep} pins={pins} seed={SEED} (per-window)"
    )
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=BUILD / "and4_I2win_pwrand",
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
