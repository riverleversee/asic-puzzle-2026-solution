#!/usr/bin/env python3
"""Ik random-spacing timelines for every and4_2_3 pin folder.

Same I patterns as nor3_2_2/run_Ik_random_spacing_timeline.py; each pin's
output into and4 is highlighted (yellow band + ★).

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py
  python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py --pin dfrtp_2_24
"""
from __future__ import annotations

import argparse
import csv
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

# Reuse lane / highlight maps from the I-suite runner
sys.path.insert(0, str(HERE))
from run_i_suites_all_pins import (  # noqa: E402
    PIN_AND4,
    PIN_KEY,
    PIN_LANES,
    PIN_TITLE,
)

BUILD = ROOT / "phase2" / "build"
N_CYC = 121
TAG = "and215_and4_Ik_rand"
K_MAX = 12
SEED = 20260904
GAP_MIN = 1
GAP_MAX = 11


def place_random_ones(k: int, rng: random.Random) -> list[int]:
    if k <= 0:
        return []
    for _ in range(500):
        start = rng.randint(0, N_CYC - 1)
        pos = [start]
        ok = True
        cur = start
        for _i in range(k - 1):
            gap = rng.randint(GAP_MIN, GAP_MAX)
            cur = cur + gap
            if cur >= N_CYC:
                ok = False
                break
            pos.append(cur)
        if ok and len(set(pos)) == k:
            return sorted(pos)
    return sorted(rng.sample(range(N_CYC), k))


def build_modes(rng: random.Random) -> list[tuple[str, str, list[int]]]:
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for k in range(1, K_MAX + 1):
        pos = place_random_ones(k, rng)
        gaps = [pos[i] - pos[i - 1] for i in range(1, len(pos))]
        gtxt = ",".join(map(str, gaps)) if gaps else "—"
        name = f"Ik{k:02d}_n{k}_@{','.join(map(str, pos))}_g{gtxt}"
        if len(name) > 48:
            name = f"Ik{k:02d}_n{k}_g{gtxt}"
        out.append((name, pat_bits(N_CYC, pos), pos))
    return out


def fmt(xs: list[int], lim: int = 28) -> str:
    if len(xs) <= lim:
        return str(xs)
    return str(xs[:lim])[:-1] + f", …] (n={len(xs)})"


def all_probes() -> list[tuple[str, str]]:
    seen: set[str] = set()
    probes: list[tuple[str, str]] = [("I", "I"), ("enable", "enable")]
    for pin, lanes in PIN_LANES.items():
        tag = pin.replace("dfrtp_", "f").replace("nor3_", "n")
        for lab, net, *_ in lanes:
            if net in seen:
                continue
            seen.add(net)
            probes.append((f"{tag}__{lab}", net))
    return probes


def lab_for(pin: str, lane_lab: str, probes: list[tuple[str, str]]) -> str:
    net = next(n for l, n, *_ in PIN_LANES[pin] if l == lane_lab)
    for plab, pnet in probes:
        if pnet == net:
            return plab
    raise KeyError((pin, lane_lab))


def write_pin(
    pin: str,
    mode_defs: list[tuple[str, str, list[int]]],
    by_mode: dict[str, list[dict]],
    probes: list[tuple[str, str]],
) -> None:
    out = HERE / pin / "timelines"
    out.mkdir(parents=True, exist_ok=True)
    lanes = PIN_LANES[pin]
    key = PIN_KEY[pin]
    and4_name = PIN_AND4[pin]
    ones_by = {n: pos for n, _b, pos in mode_defs}
    modes = [(n, b) for n, b, _ in mode_defs]
    csv_labs = [(lab, lab_for(pin, lab, probes), title, col) for lab, _n, title, col in lanes]

    out_csv = out / "Ik_random_spacing.csv"
    fields = ["mode", "cyc"] + [a for a, *_ in lanes]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for name, _ in modes:
            for r in by_mode[name]:
                row = {"mode": name, "cyc": r["cyc"]}
                for lab, csv_lab, *_ in csv_labs:
                    row[lab] = r[csv_lab]
                w.writerow(row)

    hi_yi = next(i for i, (lab, *_r) in enumerate(reversed(csv_labs)) if lab == key)
    n_m = len(modes)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, 1.65 * n_m), dpi=120, sharex=True)
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
        for yi, (lab, csv_lab, title, col) in enumerate(reversed(csv_labs)):
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
            ax.axvline(p, color="#c00000", lw=0.7, alpha=0.4, zorder=1)
        ytick_labs, weights = [], []
        for lab, _c, title, _col in reversed(csv_labs):
            if lab == key:
                ytick_labs.append(f"★ {title}")
                weights.append("bold")
            else:
                ytick_labs.append(title)
                weights.append("normal")
        ax.set_yticks(range(len(csv_labs)))
        ax.set_yticklabels(ytick_labs, fontsize=6.5, family="monospace")
        for tick, w in zip(ax.get_yticklabels(), weights):
            tick.set_fontweight(w)
            if w == "bold":
                tick.set_color("#7a0000")
        ax.set_xlim(-0.5, N_CYC - 0.5)
        ax.set_ylabel(name, fontsize=6.5, fontweight="bold")
        ax.grid(axis="x", color="#eee", lw=0.5, zorder=0)
        key_csv = lab_for(pin, key, probes)
        kx = [int(r["cyc"]) for r in rs if int(r[key_csv])]
        ax4 = lab_for(pin, "and4_X", probes)
        ax4h = [int(r["cyc"]) for r in rs if int(r[ax4])]
        ax.set_title(
            f"{name} · #I={len(ones_by[name])} · {key}→{and4_name} n={len(kx)} "
            f"first={kx[0] if kx else '—'} · and4.X n={len(ax4h)}",
            fontsize=8,
            loc="left",
        )
    axes[-1].set_xlabel(
        f"cycle · seed={SEED} · gaps ∈ [{GAP_MIN},{GAP_MAX}] · yellow/★ = {key} → {and4_name}"
    )
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in lanes]
        + [Patch(facecolor="#ffe08a", edgecolor="#c00000", label=f"★ {key} → {and4_name}")],
        loc="upper right",
        ncol=4,
        fontsize=6.5,
        frameon=False,
    )
    fig.suptitle(
        f"{PIN_TITLE[pin]} · Ik random spacing k=0..{K_MAX} · highlight {key} → {and4_name}",
        fontsize=11,
    )
    fig.tight_layout()
    png = savefig_locked(fig, out / "Ik_random_spacing.png")

    md = [
        f"# `{pin}` — increasing #I with random spacing",
        "",
        f"{PIN_TITLE[pin]}",
        "",
        f"Seed `{SEED}` · k = 0..{K_MAX} · consecutive gaps uniform in "
        f"`[{GAP_MIN}, {GAP_MAX}]` cycles.",
        "",
        f"**Highlighted lane:** `{key}` → **{and4_name}** (yellow band + ★).",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "## Observe summary",
        "",
        f"| mode | #I | I ones | gaps | {key} n | first | and4.X n |",
        "|------|---:|--------|------|--------:|------:|---------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        pos = ones_by[name]
        gaps = [pos[i] - pos[i - 1] for i in range(1, len(pos))]
        key_csv = lab_for(pin, key, probes)
        kx = [int(r["cyc"]) for r in rs if int(r[key_csv])]
        ax4 = lab_for(pin, "and4_X", probes)
        ax4h = [int(r["cyc"]) for r in rs if int(r[ax4])]
        md.append(
            f"| `{name}` | {len(pos)} | `{fmt(pos, 16)}` | `{gaps or '—'}` | "
            f"{len(kx)} | {kx[0] if kx else '—'} | {len(ax4h)} |"
        )
    md += ["", "## Per-mode lanes", ""]
    for name, _ in modes:
        rs = by_mode[name]
        md.append(f"### `{name}`  I=`{fmt(ones_by[name])}`")
        md.append("")
        for lab, csv_lab, title, _c in csv_labs:
            mark = f" **← {and4_name}**" if lab == key else ""
            highs = [int(r["cyc"]) for r in rs if int(r[csv_lab])]
            md.append(f"- `{lab}` ({title}){mark} high @ `{fmt(highs)}`")
        md.append("")
    md += [
        "Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py",
        f"python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py --pin {pin}",
        "```",
        "",
    ]
    (out / "Ik_random_spacing.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  wrote {pin}/timelines/Ik_random_spacing.*")

    readme = HERE / pin / "README.md"
    if readme.is_file():
        t = readme.read_text(encoding="utf-8")
        link = (
            f"- Random-spaced Ik (highlight {and4_name}): "
            f"[`timelines/Ik_random_spacing.md`](timelines/Ik_random_spacing.md)"
        )
        if "Ik_random_spacing" not in t:
            if "- [`timelines/Ik_all11.md`](timelines/Ik_all11.md)\n" in t:
                t = t.replace(
                    "- [`timelines/Ik_all11.md`](timelines/Ik_all11.md)\n",
                    "- [`timelines/Ik_all11.md`](timelines/Ik_all11.md)\n" + link + "\n",
                )
            else:
                t = t.rstrip() + "\n\n" + link + "\n"
            if "run_Ik_random_spacing_all_pins.py" not in t:
                t = t.replace(
                    "```bash\n",
                    "```bash\n"
                    "python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py\n",
                    1,
                )
            readme.write_text(t, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pin", choices=sorted(PIN_LANES.keys()))
    args = ap.parse_args()
    pins = [args.pin] if args.pin else list(PIN_LANES.keys())

    rng = random.Random(SEED)
    mode_defs = build_modes(rng)
    modes = [(n, b) for n, b, _ in mode_defs]
    probes = all_probes()
    print(f"probes={len(probes)} modes={len(modes)} pins={pins} seed={SEED}")
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=BUILD / "and4_ik_rand",
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
