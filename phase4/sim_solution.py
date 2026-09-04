#!/usr/bin/env python3
"""Sim the phase-4 forced I=1 pattern (extended a few cycles past 121).

Reads phase4/out/forced.json; if unidentified cycles remain, fills them with 0
(forced solution candidate = force_1 only). Probes success / and2 arms / and4.X.

Usage (from rework_coded/):
  python3 phase4/sim_solution.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from probe_timeline import pat_bits, run_probe  # noqa: E402

OUT = HERE / "out"
BUILD = ROOT / "phase2" / "build"
N_CYC_I = 121
EXTRA = 4
N_CYC = N_CYC_I + EXTRA
TAG = "phase4_forced_sol"

PROBES = [
    ("I", "I"),
    ("enable", "enable"),
    ("success", "success"),
    ("and2_X", "sky130_fd_sc_hd__and2_2_15__X"),
    ("inv6_Y", "sky130_fd_sc_hd__inv_2_6__Y"),
    ("and4_X", "sky130_fd_sc_hd__and4_2_3__X"),
    ("inv23_A", "sky130_fd_sc_hd__inv_2_23__A"),
]


def main() -> None:
    forced_path = OUT / "forced.json"
    if not forced_path.is_file():
        raise SystemExit(f"missing {forced_path} — run phase4/run_forcer.py first")
    data = json.loads(forced_path.read_text(encoding="utf-8"))
    ones = sorted(data["force_1"])
    unidentified = data.get("unidentified") or []
    bits = pat_bits(N_CYC, ones)  # extra cycles stay 0

    print(
        f"sim n_cyc={N_CYC} (I_span={N_CYC_I}+{EXTRA}) "
        f"#I={len(ones)} unidentified→0:{len(unidentified)}"
    )
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=BUILD / "phase4_sol",
        tag=TAG,
        probes=PROBES,
        modes=[("forced", bits)],
        n_cyc=N_CYC,
    )
    rs = [r for r in rows if r["mode_name"] == "forced"]

    def highs(lab: str) -> list[int]:
        return [int(r["cyc"]) for r in rs if int(r[lab])]

    summary = {
        "n_cyc": N_CYC,
        "extra": EXTRA,
        "I_ones": ones,
        "n_I": len(ones),
        "unidentified_as_0": unidentified,
        "success_n": len(highs("success")),
        "success_cycles": highs("success")[:32],
        "and2_X_n": len(highs("and2_X")),
        "inv6_Y_n": len(highs("inv6_Y")),
        "and4_X_n": len(highs("and4_X")),
        "and4_X_first": (highs("and4_X")[0] if highs("and4_X") else None),
        "inv23_A_n": len(highs("inv23_A")),
        "period_ones": [
            sum(1 for c in ones if 11 * w <= c < 11 * (w + 1)) for w in range(11)
        ],
    }
    (OUT / "sim_solution.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# Phase 4 — sim of forced solution",
        "",
        f"I pattern = `force_1` from [`forced.json`](forced.json) "
        f"({len(ones)} ones); unidentified cycles driven **0**.",
        f"Sim length **{N_CYC}** (= {N_CYC_I} + {EXTRA} extra).",
        "",
        f"**I ones:** `{ones}`",
        "",
        "## Observe",
        "",
        "| net | n high | first |",
        "|-----|-------:|------:|",
        f"| `success` | {summary['success_n']} | "
        f"{summary['success_cycles'][0] if summary['success_cycles'] else '—'} |",
        f"| `and2_2_15.X` | {summary['and2_X_n']} | — |",
        f"| `inv_2_6.Y` | {summary['inv6_Y_n']} | — |",
        f"| `and4_2_3.X` | {summary['and4_X_n']} | {summary['and4_X_first'] or '—'} |",
        f"| `inv_2_23.A` (SET sticky path) | {summary['inv23_A_n']} | — |",
        "",
        f"Period-11 ones: `{summary['period_ones']}`",
        "",
        "## Verdict",
        "",
    ]
    if summary["success_n"] > 0:
        md.append("**`success` rose** under the forced pattern.")
    else:
        md.append(
            "**`success` stayed 0.** Forced open-sum pattern alone may be incomplete "
            "(SET spacing / other locks still needed), or unidentified bits matter."
        )
    md += [
        "",
        f"JSON: [`sim_solution.json`](sim_solution.json)",
        "",
        "```bash",
        "python3 phase4/run_forcer.py",
        "python3 phase4/sim_solution.py",
        "```",
        "",
    ]
    (OUT / "sim_solution.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT / 'sim_solution.md'}")
    print(
        f"success_n={summary['success_n']} and4_X_n={summary['and4_X_n']} "
        f"inv6_Y_n={summary['inv6_Y_n']} and2_X_n={summary['and2_X_n']}"
    )


if __name__ == "__main__":
    main()
