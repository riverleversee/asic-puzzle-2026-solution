#!/usr/bin/env python3
"""Run the inv_2_6 I-pattern suite on every and4_2_3 pin subfolder.

Suites (same patterns as inv_2_6 / o211a):
  I1_probe, I2_I3_spacing, I2_I3_from30, I2_I3_from75,
  I4eq_delta, I2_every_window, Ik_all11

One structural sim probes all pin nets; figures land under each pin's
`timelines/`.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
  python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py --only I2_every_window
  python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py --pin dfrtp_2_24
"""
from __future__ import annotations

import argparse
import csv
import os
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
TAG = "and215_and4_pins_i_suite"
PERIOD = 11

# Per-pin observe lanes (label, net, title, color)
PIN_LANES: dict[str, list[tuple[str, str, str, str]]] = {
    "dfrtp_2_24": [
        ("inv7_A", "sky130_fd_sc_hd__inv_2_7__A", "stub A2  inv_2_7__A", "#c45911"),
        ("A3", "sky130_fd_sc_hd__and3_2_10__B", "A3  and3_2_10__B", "#1f4e79"),
        ("B1", "sky130_fd_sc_hd__inv_2_10__Y", "B1  inv_2_10__Y", "#548235"),
        ("a32o_X", "sky130_fd_sc_hd__a32o_2_2__X", "a32o.X → flop.D", "#c00000"),
        ("Q", "sky130_fd_sc_hd__and4_2_3__A", "★ Q → and4.A", "#7030a0"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X", "#833c0c"),
    ],
    "dfrtp_2_25": [
        ("A_N", "sky130_fd_sc_hd__and3_2_11__X", "A_N  and3_2_11__X", "#c45911"),
        ("B", "sky130_fd_sc_hd__a21o_2_10__X", "B  a21o_2_10__X", "#1f4e79"),
        ("D", "sky130_fd_sc_hd__dfrtp_2_25__D", "D  and2b_2_10.X", "#c00000"),
        ("Q", "sky130_fd_sc_hd__and4_2_3__B", "★ Q → and4.B", "#7030a0"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X", "#833c0c"),
    ],
    "dfrtp_2_20": [
        ("xnor_B", "sky130_fd_sc_hd__xnor2_2_11__B", "B  xnor2_2_11__B", "#1f4e79"),
        ("xnor_Y", "sky130_fd_sc_hd__xnor2_2_11__Y", "Y  xnor → flop.D", "#c00000"),
        ("Q", "sky130_fd_sc_hd__and4_2_3__C", "★ Q → and4.C", "#7030a0"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X", "#833c0c"),
    ],
    "nor3_2_2": [
        ("A", "sky130_fd_sc_hd__nor3_2_2__A", "A  dfrtp_2_21.Q", "#c45911"),
        ("B", "sky130_fd_sc_hd__nor3_2_2__B", "B  dfrtp_2_19.Q", "#1f4e79"),
        ("C", "sky130_fd_sc_hd__or3_2_8__X", "C  or3_2_8__X", "#548235"),
        ("Y", "sky130_fd_sc_hd__nor3_2_2__Y", "★ Y → and4.D", "#c00000"),
        ("and4_X", "sky130_fd_sc_hd__and4_2_3__X", "and4.X", "#833c0c"),
    ],
}

PIN_TITLE = {
    "dfrtp_2_24": "and4.A · dfrtp_2_24 · a32o_2_2",
    "dfrtp_2_25": "and4.B · dfrtp_2_25 · and2b_2_10",
    "dfrtp_2_20": "and4.C · dfrtp_2_20 · xnor2_2_11",
    "nor3_2_2": "and4.D · nor3_2_2",
}

# Primary observe label = pin output into and4 (highlighted on plots)
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


def fmt(xs: list[int], lim: int = 24) -> str:
    if len(xs) <= lim:
        return str(xs)
    return str(xs[:lim])[:-1] + f", …] (n={len(xs)})"


def ones_every_window(delta: int, off0: int = 0) -> list[int]:
    assert 0 <= off0 < PERIOD
    assert 1 <= delta < PERIOD
    assert off0 + delta < PERIOD
    pos: list[int] = []
    for w in range(N_CYC // PERIOD):
        base = w * PERIOD
        pos.append(base + off0)
        pos.append(base + off0 + delta)
    return pos


def suite_I1() -> list[tuple[str, str, list[int]]]:
    specs = [
        ("all0", []),
        ("all1", None),  # special
        ("I1_cyc1", [1]),
        ("I1_cyc10", [10]),
        ("I1_cyc1_12", [1, 12]),
    ]
    out = []
    for name, pos in specs:
        if name == "all1":
            out.append((name, pat_bits(N_CYC, fill="1"), list(range(N_CYC))))
        else:
            out.append((name, pat_bits(N_CYC, pos or []), pos or []))
    return out


def suite_I2_I3_spacing() -> list[tuple[str, str, list[int]]]:
    i_ref, win_last = 1, 13
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for d in range(1, win_last - i_ref + 1):
        pos = [i_ref, i_ref + d]
        out.append((f"I2_d{d:02d}_@{','.join(map(str, pos))}", pat_bits(N_CYC, pos), pos))
    for d in range(1, (win_last - i_ref) // 2 + 1):
        pos = [i_ref, i_ref + d, i_ref + 2 * d]
        out.append((f"I3eq_d{d:02d}_@{','.join(map(str, pos))}", pat_bits(N_CYC, pos), pos))
    return out


def suite_I2_I3_from(i_ref: int) -> list[tuple[str, str, list[int]]]:
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for d in range(1, 13):
        pos = [i_ref, i_ref + d]
        assert max(pos) < N_CYC
        out.append((f"I2_d{d:02d}_@{','.join(map(str, pos))}", pat_bits(N_CYC, pos), pos))
    for d in range(1, 7):
        pos = [i_ref, i_ref + d, i_ref + 2 * d]
        assert max(pos) < N_CYC
        out.append((f"I3eq_d{d:02d}_@{','.join(map(str, pos))}", pat_bits(N_CYC, pos), pos))
    return out


def suite_I4eq_delta() -> list[tuple[str, str, list[int]]]:
    i_ref = 2
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for d in range(1, 12):
        pos = [i_ref + i * d for i in range(4)]
        out.append((f"I4eq_d{d:02d}_@{','.join(map(str, pos))}", pat_bits(N_CYC, pos), pos))
    return out


def suite_I2_every_window() -> list[tuple[str, str, list[int]]]:
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for d in range(1, PERIOD):
        pos = ones_every_window(d, off0=0)
        out.append((f"I2win_d{d:02d}_off0", pat_bits(N_CYC, pos), pos))
    return out


def suite_Ik_all11() -> list[tuple[str, str, list[int]]]:
    i_ref, win_last = 1, 10
    out: list[tuple[str, str, list[int]]] = [("all0", pat_bits(N_CYC), [])]
    for k in range(2, 6):
        max_d = (win_last - i_ref) // (k - 1)
        for d in range(1, max_d + 1):
            pos = [i_ref + i * d for i in range(k)]
            out.append(
                (f"I{k}eq_d{d:02d}_@{','.join(map(str, pos))}", pat_bits(N_CYC, pos), pos)
            )
    all11 = list(range(0, win_last + 1))
    out.append((f"all11_@{all11[0]}..{all11[-1]}", pat_bits(N_CYC, all11), all11))
    return out


SUITES: dict[str, tuple] = {
    "I1_probe": ("I1_probe_timeline", suite_I1),
    "I2_I3_spacing": ("I2_I3_spacing", suite_I2_I3_spacing),
    "I2_I3_from30": ("I2_I3_from30", lambda: suite_I2_I3_from(30)),
    "I2_I3_from75": ("I2_I3_from75", lambda: suite_I2_I3_from(75)),
    "I4eq_delta": ("I4eq_delta", suite_I4eq_delta),
    "I2_every_window": ("I2_every_window", suite_I2_every_window),
    "Ik_all11": ("Ik_all11", suite_Ik_all11),
}


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


def write_suite(
    pin: str,
    suite_key: str,
    stem: str,
    mode_defs: list[tuple[str, str, list[int]]],
    by_mode: dict[str, list[dict]],
    probes: list[tuple[str, str]],
) -> None:
    out = HERE / pin / "timelines"
    out.mkdir(parents=True, exist_ok=True)
    lanes = PIN_LANES[pin]
    key = PIN_KEY[pin]
    ones_by = {n: pos for n, _b, pos in mode_defs}
    modes = [(n, b) for n, b, _ in mode_defs]

    # map display labs → csv labs
    csv_labs = [(lab, lab_for(pin, lab, probes), title, col) for lab, _n, title, col in lanes]

    out_csv = out / f"{stem}.csv"
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

    n_m = len(modes)
    fig_h = max(1.35 * n_m, 4.0)
    fig, axes = plt.subplots(n_m, 1, figsize=(14, fig_h), dpi=120, sharex=True)
    if n_m == 1:
        axes = [axes]
    hi_yi = next(i for i, (lab, *_r) in enumerate(reversed(csv_labs)) if lab == key)
    and4_name = PIN_AND4[pin]
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
            ax.axvline(p, color="#c00000", lw=0.55, alpha=0.35, zorder=1)
        if suite_key == "I2_every_window":
            for w in range(N_CYC // PERIOD + 1):
                ax.axvline(w * PERIOD - 0.5, color="#bbb", lw=0.6, ls=":", zorder=0)
        ytick_labs = []
        weights = []
        for lab, _c, title, _col in reversed(csv_labs):
            if lab == key:
                ytick_labs.append(f"★ {title}")
                weights.append("bold")
            else:
                ytick_labs.append(title)
                weights.append("normal")
        ax.set_yticks(range(len(csv_labs)))
        ax.set_yticklabels(ytick_labs, fontsize=6.0, family="monospace")
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
            fontsize=7.5,
            loc="left",
        )
    axes[-1].set_xlabel(f"cycle (red = I=1 · yellow/★ = {key} → {and4_name})")
    axes[0].legend(
        handles=[Patch(facecolor=c, label=lab) for lab, _n, _t, c in lanes]
        + [Patch(facecolor="#ffe08a", edgecolor="#c00000", label=f"★ {key} → {and4_name}")],
        loc="upper right",
        ncol=min(6, len(lanes) + 1),
        fontsize=6,
        frameon=False,
    )
    fig.suptitle(f"{PIN_TITLE[pin]} · {stem} · highlight {key} → {and4_name}", fontsize=11)
    fig.tight_layout()
    png = savefig_locked(fig, out / f"{stem}.png")

    md = [
        f"# `{pin}` — `{stem}`",
        "",
        f"{PIN_TITLE[pin]}",
        "",
        f"**Highlighted lane:** `{key}` → **{and4_name}** (yellow band + ★).",
        "",
        f"Figure: [`{png.name}`]({png.name})",
        "",
        f"CSV: [`{out_csv.name}`]({out_csv.name})",
        "",
        "## Observe summary",
        "",
        f"| mode | #I | {key} n | first | and4.X n |",
        "|------|---:|--------:|------:|---------:|",
    ]
    for name, _ in modes:
        rs = by_mode[name]
        key_csv = lab_for(pin, key, probes)
        kx = [int(r["cyc"]) for r in rs if int(r[key_csv])]
        ax4 = lab_for(pin, "and4_X", probes)
        ax4h = [int(r["cyc"]) for r in rs if int(r[ax4])]
        md.append(
            f"| `{name}` | {len(ones_by[name])} | {len(kx)} | "
            f"{kx[0] if kx else '—'} | {len(ax4h)} |"
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
        f"Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py",
        "```",
        "",
    ]
    (out / f"{stem}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  wrote {pin}/timelines/{stem}.*  ({n_m} modes)")


def update_pin_readme(pin: str, stems: list[str]) -> None:
    readme = HERE / pin / "README.md"
    if not readme.is_file():
        return
    text = readme.read_text(encoding="utf-8")
    block_lines = [
        "## Timelines (I-pattern suite)",
        "",
        "Same patterns as `inv_2_6` / `o211a_2_8` for pattern ID.",
        "",
    ]
    for stem in stems:
        block_lines.append(f"- [`timelines/{stem}.md`](timelines/{stem}.md)")
    block_lines += [
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py",
        f"python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py --pin {pin}",
        "```",
        "",
    ]
    marker = "## Timelines (I-pattern suite)"
    related = "## Related"
    if marker in text:
        pre, rest = text.split(marker, 1)
        if related in rest:
            _, post = rest.split(related, 1)
            text = pre + "\n".join(block_lines) + related + post
        else:
            # replace through bash block end roughly
            text = pre + "\n".join(block_lines)
    elif related in text:
        pre, post = text.split(related, 1)
        text = pre + "\n".join(block_lines) + related + post
    else:
        text = text.rstrip() + "\n\n" + "\n".join(block_lines)
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=sorted(SUITES.keys()), help="One suite only")
    ap.add_argument("--pin", choices=sorted(PIN_LANES.keys()), help="One pin folder only")
    args = ap.parse_args()

    suite_keys = [args.only] if args.only else list(SUITES.keys())
    pins = [args.pin] if args.pin else list(PIN_LANES.keys())

    suite_modes: dict[str, list[tuple[str, str, list[int]]]] = {}
    mode_map: dict[str, str] = {}  # name -> bits
    for sk in suite_keys:
        _stem, builder = SUITES[sk]
        defs = builder()
        fixed: list[tuple[str, str, list[int]]] = []
        for name, bits, pos in defs:
            if name in mode_map and mode_map[name] != bits:
                name = f"{sk}__{name}"
            mode_map[name] = bits
            fixed.append((name, bits, pos))
        suite_modes[sk] = fixed

    modes = [("all0", mode_map["all0"])] + sorted(
        [(n, b) for n, b in mode_map.items() if n != "all0"], key=lambda x: x[0]
    )

    probes = all_probes()
    print(f"probes={len(probes)} modes={len(modes)} suites={suite_keys} pins={pins}")
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=BUILD / "and4_i_suite",
        tag=TAG,
        probes=probes,
        modes=modes,
        n_cyc=N_CYC,
    )
    by_mode = {name: [r for r in rows if r["mode_name"] == name] for name, _ in modes}

    stems_done: dict[str, list[str]] = {p: [] for p in pins}
    for sk in suite_keys:
        stem, _ = SUITES[sk]
        defs = suite_modes[sk]
        # ensure all0 present
        names = {n for n, _, _ in defs}
        if "all0" not in names:
            defs = [("all0", pat_bits(N_CYC), [])] + defs
        for pin in pins:
            write_suite(pin, sk, stem, defs, by_mode, probes)
            stems_done[pin].append(stem)

    for pin in pins:
        update_pin_readme(pin, stems_done[pin])

    # parent README note
    parent = HERE / "README.md"
    if parent.is_file():
        t = parent.read_text(encoding="utf-8")
        note = (
            "- I-pattern suites (per pin): "
            "`dfrtp_2_24|25|20|nor3_2_2/timelines/` "
            "(I1, I2_I3 spacing/from30/from75, I4eq, I2win, Ik_all11)\n"
        )
        if "I-pattern suites (per pin)" not in t:
            t = t.replace(
                "- Inputs timeline: [`timelines/and4_inputs.md`](timelines/and4_inputs.md)\n",
                "- Inputs timeline: [`timelines/and4_inputs.md`](timelines/and4_inputs.md)\n"
                + note,
            )
            if "run_i_suites_all_pins.py" not in t:
                t = t.replace(
                    "python3 phase2/and2_2_15/and4_2_3/expand_pin_subs.py\n",
                    "python3 phase2/and2_2_15/and4_2_3/expand_pin_subs.py\n"
                    "python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py\n",
                )
            parent.write_text(t, encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
