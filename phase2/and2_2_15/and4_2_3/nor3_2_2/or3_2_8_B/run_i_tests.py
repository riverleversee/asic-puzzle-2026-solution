#!/usr/bin/env python3
"""I-test suite for or3_2_8_B — watches filtered by 1-hop-to-I pin rule.

Suites:
  I1_probe, I2win_rand_spacing (fixed pair/window), I2win_perwindow_rand

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run_i_tests.py
"""
from __future__ import annotations

import csv
import colorsys
import json
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
AND4 = HERE.parents[1]
for p in (ROOT / "lib", AND4):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from probe_timeline import pat_bits, run_probe  # noqa: E402
from rework_paths import savefig_locked  # noqa: E402
from structural_drivers import parse_structural  # noqa: E402
from render_success_logic_depth import reaches_I  # noqa: E402
from pin_i_hop_rule import allowed_watch_nets, short  # noqa: E402

OUT = HERE / "timelines"
BUILD = ROOT / "phase2" / "build"
N_CYC = 121
PERIOD = 11
N_WIN = N_CYC // PERIOD
SEED = 20260904
N_SWEEP = 12
MIN_ACTIVE = 7
TAG = "and215_or3b_i"

Q_NET = "sky130_fd_sc_hd__or3_2_8__B"
ROOT_NET = "sky130_fd_sc_hd__o21a_2_11__X"
OR3_X = "sky130_fd_sc_hd__or3_2_8__X"
NOR3_Y = "sky130_fd_sc_hd__nor3_2_2__Y"
AND4_X = "sky130_fd_sc_hd__and4_2_3__X"

HIGHLIGHT = "Q"  # or3_2_8.B → and4.D path


def palette(n: int) -> list[str]:
    cols = []
    for i in range(n):
        h = (0.02 + 0.85 * i / max(n, 1)) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.72, 0.78)
        cols.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
    return cols


def build_watch_lanes(drivers, stubs) -> list[tuple[str, str, str]]:
    """Allowed watches + forced observe of Q / o21a / or3.X / nor3.Y / and4.X."""
    rows = allowed_watch_nets(ROOT_NET, drivers, stubs, reaches_I, max_depth=5)
    allowed = [r for r in rows if r["allowed"]]
    # Always include these observe points (must pass rule or be forced highlight)
    forced = [
        ("Q", Q_NET, "★ Q  or3_2_8.B → or3.X"),
        ("o21a_X", ROOT_NET, "o21a_2_11.X → flop.D"),
        ("or3_X", OR3_X, "or3_2_8.X → nor3.C"),
        ("nor3_Y", NOR3_Y, "nor3.Y → and4.D"),
        ("and4_X", AND4_X, "and4.X"),
    ]
    lanes: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for lab, net, title in forced:
        seen.add(net)
        lanes.append((lab, net, title))
    # Add other allowed nets (skip clk/rst already filtered)
    for r in allowed:
        net = r["net_full"]
        if net in seen:
            continue
        if net == "I":
            continue
        seen.add(net)
        lab = r["net"].replace("__", "_")
        # shorten label
        if len(lab) > 18:
            lab = lab.split("_")[-2] + "_" + lab.split("_")[-1] if "_" in lab else lab[:18]
        # uniquify
        base = lab
        k = 2
        while any(l == lab for l, *_ in lanes):
            lab = f"{base}_{k}"
            k += 1
        why = r["why"]
        lanes.append((lab, net, f"{r['net']} ({why})"))
    return lanes


def ones_every_window(off_a: int, off_b: int) -> list[int]:
    pos = []
    for w in range(N_WIN):
        base = w * PERIOD
        pos += [base + off_a, base + off_b]
    return sorted(pos)


def ones_per_window_independent(rng: random.Random) -> list[int]:
    pos = []
    for w in range(N_WIN):
        a, b = rng.sample(range(PERIOD), 2)
        base = w * PERIOD
        pos += [base + min(a, b), base + max(a, b)]
    return sorted(pos)


def suite_modes() -> list[tuple[str, str, list[int], str]]:
    """(name, bits, ones, suite_tag)."""
    out: list[tuple[str, str, list[int], str]] = [
        ("all0", pat_bits(N_CYC), [], "I1"),
        ("I1_cyc1", pat_bits(N_CYC, [1]), [1], "I1"),
        ("I1_cyc10", pat_bits(N_CYC, [10]), [10], "I1"),
        ("I1_cyc1_12", pat_bits(N_CYC, [1, 12]), [1, 12], "I1"),
    ]
    rng = random.Random(SEED)
    seen: set[tuple[int, int]] = set()
    while len(seen) < N_SWEEP:
        a, b = rng.sample(range(PERIOD), 2)
        pair = (min(a, b), max(a, b))
        if pair in seen:
            continue
        seen.add(pair)
        pos = ones_every_window(pair[0], pair[1])
        name = f"I2win_off{pair[0]},{pair[1]}_d{pair[1]-pair[0]}"
        out.append((name, pat_bits(N_CYC, pos), pos, "I2win_fixed"))
    for i in range(1, N_SWEEP + 1):
        r2 = random.Random(SEED + 10007 * i)
        pos = ones_per_window_independent(r2)
        out.append((f"I2pw_r{i:02d}", pat_bits(N_CYC, pos), pos, "I2win_perwindow"))
    return out


def activity(rows_all, csv_lab: str) -> tuple[bool, int]:
    vals = [int(r[csv_lab]) for r in rows_all]
    if len(set(vals)) <= 1:
        return False, 0
    flips = sum(1 for i in range(1, len(vals)) if vals[i] != vals[i - 1])
    return True, flips


def select_active(lanes, probes_map, rows_all):
    scored = []
    for lab, net, title in lanes:
        csv_lab = probes_map[net]
        act, flips = activity(rows_all, csv_lab)
        scored.append((flips if act else -1, lab, csv_lab, title, net))
    active = sorted([s for s in scored if s[0] >= 0], key=lambda t: -t[0])
    static = [s for s in scored if s[0] < 0]
    chosen = [HIGHLIGHT]
    for _f, lab, *_ in active:
        if lab not in chosen:
            chosen.append(lab)
    if len(chosen) < MIN_ACTIVE:
        for _f, lab, *_ in static:
            if lab not in chosen:
                chosen.append(lab)
            if len(chosen) >= MIN_ACTIVE:
                break
    cols = palette(len(chosen))
    out = []
    for i, lab in enumerate(chosen):
        _f, lab2, csv_lab, title, net = next(s for s in scored if s[1] == lab)
        col = "#c00000" if lab == HIGHLIGHT else cols[i]
        out.append((lab, csv_lab, title, col))
    return out


def write_suite_figure(
    suite: str,
    mode_defs: list,
    by_mode: dict,
    lanes_disp,
    probes_map,
    ones_by,
):
    modes = [(n, b) for n, b, _p, s in mode_defs if s == suite or (suite == "I1" and s == "I1")]
    if suite == "I1":
        modes = [(n, b) for n, b, _p, s in mode_defs if s == "I1"]
    elif suite == "I2win_fixed":
        modes = [(n, b) for n, b, _p, s in mode_defs if s in ("I1", "I2win_fixed") and (s != "I1" or n == "all0")]
        # all0 + fixed
        modes = [("all0", pat_bits(N_CYC))] + [
            (n, b) for n, b, _p, s in mode_defs if s == "I2win_fixed"
        ]
    else:
        modes = [("all0", pat_bits(N_CYC))] + [
            (n, b) for n, b, _p, s in mode_defs if s == "I2win_perwindow"
        ]

    stem = {
        "I1": "I1_probe",
        "I2win_fixed": "I2win_rand_spacing",
        "I2win_perwindow": "I2win_perwindow_rand",
    }[suite]

    n_m = len(modes)
    hi_yi = next(i for i, (lab, *_r) in enumerate(reversed(lanes_disp)) if lab == HIGHLIGHT)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, 1.45 * n_m), dpi=120, sharex=True)
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
        for yi, (lab, csv_lab, title, col) in enumerate(reversed(lanes_disp)):
            highs = [int(r["cyc"]) for r in rs if int(r[csv_lab])]
            for c in highs:
                ax.barh(
                    yi,
                    1.0,
                    left=c - 0.5,
                    height=0.78 if lab == HIGHLIGHT else 0.72,
                    color=col,
                    edgecolor="#7a0000" if lab == HIGHLIGHT else "none",
                    lw=0.6 if lab == HIGHLIGHT else 0,
                    zorder=3 if lab == HIGHLIGHT else 2,
                )
        for p in ones_by.get(name, []):
            ax.axvline(p, color="#c00000", lw=0.5, alpha=0.35, zorder=1)
        if suite != "I1":
            for w in range(N_WIN + 1):
                ax.axvline(w * PERIOD - 0.5, color="#bbb", lw=0.5, ls=":", zorder=0)
        ytick, weights = [], []
        for lab, _c, title, _col in reversed(lanes_disp):
            ytick.append(f"★ {title}" if lab == HIGHLIGHT else title)
            weights.append("bold" if lab == HIGHLIGHT else "normal")
        ax.set_yticks(range(len(lanes_disp)))
        ax.set_yticklabels(ytick, fontsize=5.4, family="monospace")
        for tick, wt in zip(ax.get_yticklabels(), weights):
            tick.set_fontweight(wt)
            if wt == "bold":
                tick.set_color("#7a0000")
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=5.8, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5, zorder=0)
        qlab = next(c for l, c, *_ in lanes_disp if l == HIGHLIGHT)
        qx = [int(r["cyc"]) for r in rs if int(r[qlab])]
        ax.set_title(
            f"{name} · #I={len(ones_by.get(name, []))} · Q n={len(qx)} "
            f"first={qx[0] if qx else '—'} · lanes={len(lanes_disp)}",
            fontsize=7.0,
            loc="left",
        )
    axes[-1].set_xlabel("cycle · yellow/★ = or3_2_8.B (Q) · pin rule: 1-hop to I")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _c, _t, c in lanes_disp],
        loc="upper right",
        ncol=min(5, len(lanes_disp)),
        fontsize=5.2,
        frameon=False,
    )
    fig.suptitle(f"or3_2_8_B · {stem} · 1-hop-to-I watches · active only", fontsize=11)
    fig.tight_layout()
    png = savefig_locked(fig, OUT / f"{stem}.png")

    # csv + md
    out_csv = OUT / f"{stem}.csv"
    fields = ["mode", "cyc"] + [lab for lab, *_ in lanes_disp]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in modes:
            for r in by_mode[name]:
                row = {"mode": name, "cyc": r["cyc"]}
                for lab, csv_lab, *_ in lanes_disp:
                    row[lab] = r[csv_lab]
                w.writerow(row)

    md = [
        f"# `or3_2_8_B` — `{stem}`",
        "",
        "Watches restricted by **1-hop-to-I** pin rule "
        "([`../../pin_i_hop_rule.py`](../../../../pin_i_hop_rule.py)); "
        "plot shows non-static lanes only (★ = `or3_2_8.B`).",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "## Summary",
        "",
        "| mode | #I | Q n | first |",
        "|------|---:|----:|------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        qlab = next(c for l, c, *_ in lanes_disp if l == HIGHLIGHT)
        qx = [int(r["cyc"]) for r in rs if int(r[qlab])]
        md.append(
            f"| `{name}` | {len(ones_by.get(name, []))} | {len(qx)} | "
            f"{qx[0] if qx else '—'} |"
        )
    md += [
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run_i_tests.py",
        "```",
        "",
    ]
    (OUT / f"{stem}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  wrote timelines/{stem}.* ({n_m} modes, {len(lanes_disp)} lanes)")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    drivers, stubs, meta = parse_structural()
    print("structural:", meta)
    lanes = build_watch_lanes(drivers, stubs)
    print(f"watch candidates (rule+forced): {len(lanes)}")
    for lab, net, title in lanes[:12]:
        print(f"  {lab}: {short(net)}")

    # unique probes
    probes = [("I", "I"), ("enable", "enable")]
    probes_map: dict[str, str] = {}
    for lab, net, _t in lanes:
        if net in probes_map:
            continue
        plab = f"w_{lab}"
        probes.append((plab, net))
        probes_map[net] = plab

    mode_defs = suite_modes()
    modes = [(n, b) for n, b, _p, _s in mode_defs]
    ones_by = {n: pos for n, _b, pos, _s in mode_defs}
    print(f"modes={len(modes)}")
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=BUILD / "or3b_i",
        tag=TAG,
        probes=probes,
        modes=modes,
        n_cyc=N_CYC,
    )
    by_mode = {name: [r for r in rows if r["mode_name"] == name] for name, _ in modes}
    rows_all = rows
    lanes_disp = select_active(lanes, probes_map, rows_all)
    print(f"active plotted: {len(lanes_disp)} {[l for l,*_ in lanes_disp]}")

    for suite in ("I1", "I2win_fixed", "I2win_perwindow"):
        write_suite_figure(suite, mode_defs, by_mode, lanes_disp, probes_map, ones_by)

    # index
    (OUT / "README.md").write_text(
        "\n".join(
            [
                "# `or3_2_8_B` timelines",
                "",
                "Pin rule: [`../../../pin_i_hop_rule.py`](../../../pin_i_hop_rule.py) "
                "(≤1 hop from an I-reaching net).",
                "",
                "- [`I1_probe.md`](I1_probe.md)",
                "- [`I2win_rand_spacing.md`](I2win_rand_spacing.md) — same offs every window",
                "- [`I2win_perwindow_rand.md`](I2win_perwindow_rand.md) — offs per window",
                "",
                "```bash",
                "python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run_i_tests.py",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("done")


if __name__ == "__main__":
    main()
