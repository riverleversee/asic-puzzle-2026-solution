#!/usr/bin/env python3
"""dfrtp_2_24 — I2-per-cycle pass report (extended sim).

Rule: phase3/and2_2_15/rules/and4_2_3_two_per_cycle.txt
  Two I=1 per period-11 cycle (from entry 0) satisfies and4_2_3;
  likely a total-ones budget. Always sim a few extra cycles past 121.

Does not rewrite timeline plots — report only under reports/.

Usage (from rework_coded/):
  python3 phase2/and2_2_15/and4_2_3/dfrtp_2_24/run_I2win_extended_report.py
"""
from __future__ import annotations

import csv
import itertools
import os
import random
import sys
from pathlib import Path

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

REPORTS = HERE / "reports"
BUILD = ROOT / "phase2" / "build"
PERIOD = 11
N_WIN = 11  # covers cycles 0..120
I_SPAN = N_WIN * PERIOD  # 121
EXTRA = 4  # pad so and4.X after I@120 is observable
N_CYC = I_SPAN + EXTRA  # 125
SEED = 20260904
N_PW = 48
MID = (1, 3)
TAG = "and215_dfrtp24_I2win_ext_report"

PROBES = [
    ("I", "I"),
    ("Q", "sky130_fd_sc_hd__and4_2_3__A"),
    ("and4_X", "sky130_fd_sc_hd__and4_2_3__X"),
]


def ones_from_pairs(pairs: list[tuple[int, int]]) -> list[int]:
    assert len(pairs) == N_WIN
    pos: list[int] = []
    for w, (a, b) in enumerate(pairs):
        base = w * PERIOD
        pos.append(base + a)
        pos.append(base + b)
    return sorted(pos)


def build_modes(rng: random.Random) -> list[tuple[str, str, list[int], dict]]:
    out: list[tuple[str, str, list[int], dict]] = []

    # A) Exhaustive fixed pair every window — all C(11,2)
    for a, b in itertools.combinations(range(PERIOD), 2):
        pairs = [(a, b)] * N_WIN
        pos = ones_from_pairs(pairs)
        out.append(
            (
                f"ex_{a},{b}",
                pat_bits(N_CYC, pos),
                pos,
                {"suite": "exhaustive", "pair": (a, b), "hits_final_bit10": 120 in pos},
            )
        )

    # B) Per-window random pairs
    for i in range(1, N_PW + 1):
        pairs = [tuple(sorted(rng.sample(range(PERIOD), 2))) for _ in range(N_WIN)]
        pos = ones_from_pairs(pairs)
        out.append(
            (
                f"pw_r{i:02d}",
                pat_bits(N_CYC, pos),
                pos,
                {
                    "suite": "perwindow",
                    "pair": None,
                    "hits_final_bit10": 120 in pos,
                },
            )
        )

    # C) Entry 0 on first + last windows only; mid fixed (1,3)
    for sf in range(1, PERIOD):
        for sl in range(1, PERIOD):
            pairs = [(0, sf)] + [MID] * (N_WIN - 2) + [(0, sl)]
            pos = ones_from_pairs(pairs)
            out.append(
                (
                    f"e0ends_sf{sf}_sl{sl}",
                    pat_bits(N_CYC, pos),
                    pos,
                    {
                        "suite": "entry0_ends",
                        "pair": (sf, sl),
                        "hits_final_bit10": 120 in pos,
                    },
                )
            )

    # D) Force bit10 on every window (incl. last) — should pass with EXTRA>0
    last_bit = PERIOD - 1
    for comp in range(last_bit):
        pairs = [(comp, last_bit)] * N_WIN
        pos = ones_from_pairs(pairs)
        assert 120 in pos
        out.append(
            (
                f"force10_c{comp}",
                pat_bits(N_CYC, pos),
                pos,
                {
                    "suite": "force_bit10_all",
                    "pair": (comp, last_bit),
                    "hits_final_bit10": True,
                },
            )
        )
    return out


def score(rs: list[dict], pos: list[int]) -> dict:
    qx = [int(r["cyc"]) for r in rs if int(r["Q"])]
    ax = [int(r["cyc"]) for r in rs if int(r["and4_X"])]
    # Pass with extended horizon: and4.X must rise at least once
    return {
        "Q_n": len(qx),
        "and4_X_n": len(ax),
        "and4_X_first": ax[0] if ax else None,
        "and4_X_last": ax[-1] if ax else None,
        "has_I120": 120 in pos,
        "pass": len(ax) > 0,
    }


def main() -> None:
    rng = random.Random(SEED)
    mode_defs = build_modes(rng)
    modes = [(n, b) for n, b, _p, _m in mode_defs]
    print(
        f"modes={len(modes)} n_cyc={N_CYC} (I_span={I_SPAN}+EXTRA={EXTRA}) "
        f"2 ones × {N_WIN} windows from entry 0"
    )
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=BUILD / "dfrtp24_I2win_ext_report",
        tag=TAG,
        probes=PROBES,
        modes=modes,
        n_cyc=N_CYC,
    )
    by_mode = {name: [r for r in rows if r["mode_name"] == name] for name, _ in modes}
    meta_by = {n: m for n, _b, _p, m in mode_defs}
    ones_by = {n: p for n, _b, p, _m in mode_defs}
    stats = {n: score(by_mode[n], ones_by[n]) for n, _ in modes}

    REPORTS.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS / "I2win_2per_extended.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "mode",
                "suite",
                "pair",
                "has_I120",
                "pass",
                "Q_n",
                "and4_X_n",
                "and4_X_first",
                "and4_X_last",
            ],
        )
        w.writeheader()
        for name, _ in modes:
            m = meta_by[name]
            st = stats[name]
            pair = m.get("pair")
            w.writerow(
                {
                    "mode": name,
                    "suite": m["suite"],
                    "pair": ""
                    if pair is None
                    else (f"{pair[0]},{pair[1]}" if isinstance(pair, tuple) else str(pair)),
                    "has_I120": int(st["has_I120"]),
                    "pass": int(st["pass"]),
                    "Q_n": st["Q_n"],
                    "and4_X_n": st["and4_X_n"],
                    "and4_X_first": st["and4_X_first"] if st["and4_X_first"] is not None else "",
                    "and4_X_last": st["and4_X_last"] if st["and4_X_last"] is not None else "",
                }
            )

    total = len(modes)
    n_pass = sum(1 for s in stats.values() if s["pass"])
    n_fail = total - n_pass

    md = [
        "# `dfrtp_2_24` — I2-per-cycle pass report (extended sim)",
        "",
        "and4.A · `dfrtp_2_24` · `a32o_2_2`",
        "",
        "Rule: [`../../../../phase3/and2_2_15/rules/and4_2_3_two_per_cycle.txt`]"
        "(../../../../phase3/and2_2_15/rules/and4_2_3_two_per_cycle.txt) — "
        "**2 `I=1` per period-11 cycle** satisfies `and4_2_3` (likely total ones); "
        "always sim a few cycles past 121.",
        "",
        "## Setup",
        "",
        f"- Cycles from **entry 0**: `C_k = [11k .. 11k+10]`, `k=0..{N_WIN - 1}` "
        f"({I_SPAN} I cycles).",
        f"- Exactly **2** `I=1` per cycle.",
        f"- Sim length **{N_CYC}** = `{I_SPAN}` + **{EXTRA}** extra (`I=0`).",
        "",
        "Pass = `and4.X` high on at least one cycle.",
        "",
        f"**Result: {n_pass}/{total} pass"
        + (f", {n_fail} fail**" if n_fail else "** — all pass."),
        "",
        f"CSV: [`{csv_path.name}`]({csv_path.name})",
        "",
        f"Seed `{SEED}`.",
        "",
    ]

    for suite, title in (
        ("exhaustive", f"Exhaustive fixed pairs `C(11,2)={11*10//2}` · same offs every window"),
        ("perwindow", f"Per-window random ×{N_PW}"),
        ("entry0_ends", "Entry 0 on first+last windows only · mid `(1,3)` · sf/sl `1..10`"),
        ("force_bit10_all", "Force bit 10 every window (incl. last / cyc 120)"),
    ):
        rows_s = [
            (n, meta_by[n], stats[n])
            for n, _b, _p, m in mode_defs
            if m["suite"] == suite
        ]
        np = sum(1 for _, _, s in rows_s if s["pass"])
        nf = len(rows_s) - np
        with120 = [(n, m, s) for n, m, s in rows_s if s["has_I120"]]
        no120 = [(n, m, s) for n, m, s in rows_s if not s["has_I120"]]
        md += [
            f"## {title}",
            "",
            f"Modes **{len(rows_s)}** · pass **{np}** · fail **{nf}** "
            f"({100.0 * np / len(rows_s):.1f}%).",
            "",
            "| has I@120? | n | pass | fail |",
            "|------------|--:|-----:|-----:|",
            f"| yes | {len(with120)} | {sum(1 for _,_,s in with120 if s['pass'])} | "
            f"{sum(1 for _,_,s in with120 if not s['pass'])} |",
            f"| no | {len(no120)} | {sum(1 for _,_,s in no120 if s['pass'])} | "
            f"{sum(1 for _,_,s in no120 if not s['pass'])} |",
            "",
        ]
        fails = [(n, m, s) for n, m, s in rows_s if not s["pass"]]
        if fails:
            md += [
                "### Failures",
                "",
                "| mode | Q n | and4.X n | I@120 |",
                "|------|----:|---------:|:----:|",
            ]
            for n, _m, s in fails:
                md.append(
                    f"| `{n}` | {s['Q_n']} | {s['and4_X_n']} | "
                    f"{'yes' if s['has_I120'] else 'no'} |"
                )
            md.append("")
        else:
            xn = [s["and4_X_n"] for _, _, s in rows_s]
            md.append(f"**All passed.** `and4.X` n ∈ [`{min(xn)}`, `{max(xn)}`].\n")

        if suite == "force_bit10_all":
            md += [
                "| mode | offs | and4.X n | and4.X first | and4.X last | pass |",
                "|------|------|---------:|-------------:|------------:|:----:|",
            ]
            for n, m, s in rows_s:
                a, b = m["pair"]
                md.append(
                    f"| `{n}` | `{a},{b}` | {s['and4_X_n']} | "
                    f"{s['and4_X_first']} | {s['and4_X_last']} | "
                    f"{'✓' if s['pass'] else '✗'} |"
                )
            md.append("")

    md += [
        "## Notes",
        "",
        "- Standard timeline plots under `timelines/` were **not** regenerated.",
        "- At `n_cyc=121`, `I@120` looked like a hard fail because `and4.X` "
        "appears on cycle **121**; with EXTRA pad it passes.",
        "",
        "Parent: [`../README.md`](../README.md)",
        "",
        "```bash",
        "python3 phase2/and2_2_15/and4_2_3/dfrtp_2_24/run_I2win_extended_report.py",
        "```",
        "",
    ]
    md_path = REPORTS / "I2win_2per_extended.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"PASS {n_pass}/{total}" + (f" FAIL {n_fail}" if n_fail else " (all pass)"))
    if n_fail:
        sys.exit(1)

    # README: replace special-test links with report link
    readme = HERE / "README.md"
    if readme.is_file():
        t = readme.read_text(encoding="utf-8")
        # strip old special lines
        lines = []
        skip_cmds = {
            "run_I2win_no_last_entry.py",
            "run_I_last_entry_gap.py",
            "run_I2win_entry0",
            "run_I2win_force_final",
            "run_I2win_bit10",
            "run_extend_one_cycle",
        }
        for line in t.splitlines():
            if "I_last_entry_gap" in line or "I2win_no_last_entry" in line:
                continue
            if any(c in line for c in skip_cmds):
                continue
            lines.append(line)
        t2 = "\n".join(lines)
        link = (
            "- I2-per-window **pass report** (extended sim): "
            "[`reports/I2win_2per_extended.md`](reports/I2win_2per_extended.md)"
        )
        if "I2win_2per_extended" not in t2:
            needle = (
                "- I2 every window · **per-window** random offs: "
                "[`timelines/I2win_perwindow_rand.md`](timelines/I2win_perwindow_rand.md)"
            )
            if needle in t2:
                t2 = t2.replace(needle, needle + "\n" + link)
            else:
                t2 = t2.rstrip() + "\n\n" + link + "\n"
        cmd = "python3 phase2/and2_2_15/and4_2_3/dfrtp_2_24/run_I2win_extended_report.py\n"
        if "run_I2win_extended_report.py" not in t2:
            t2 = t2.replace("```bash\n", "```bash\n" + cmd, 1)
        readme.write_text(t2.rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
