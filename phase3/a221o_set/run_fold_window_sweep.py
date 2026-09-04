#!/usr/bin/env python3
"""Phase 3 — measure the a221o fold ALLOWED-window residues directly.

Question
--------
`a31o_sticky_set_spacing.txt` states the allowed later-cycle windows as
    Δ ∈ {1,12} → later ≡ 10 (mod 11)
    Δ = 10     → later ≡  9 (mod 11)
    Δ = 11     → never
anchored to the `or4_2_4` ABCD phase schedule. The phase-4 forcer works in the
leaf/period numbering (`row = cyc // 11`, `col = cyc % 11`), where adjacency
geometry instead wants ≡0 / ≡10. Those disagree by one residue.

This sweep decides it from the netlist rather than from either derivation.

Mechanism being observed
------------------------
    a31o_2_12.X  = (I ∧ inv_2_7.A ∧ a221o_2_1.X) ∨ inv_2_11__A
    dfrtp_2_37.Q = inv_2_11__A        # set-once sticky, holds via B1
    inv_2_23.A   = ¬inv_2_11__A

So a two-one pattern arms the sticky iff `a221o_2_1.X` is live on the later `I`.
A residue is ALLOWED when the sticky stays low.

Method
------
For each Δ ∈ {1,10,11,12} and each residue r ∈ 0..10, place exactly two ones at
`t1 = 11*row + r` and `t0 = t1 - Δ`, all other cycles 0. Two rows are used so a
result cannot be a single-row accident. Single-one and all-zero controls confirm
the sticky needs the pair.

Usage (from rework_coded/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 phase3/a221o_set/run_fold_window_sweep.py
"""
from __future__ import annotations

import json
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

OUT = HERE / "fold_windows"
BUILD = ROOT / "phase3" / "build"
N_CYC_I = 121
EXTRA = 4
N_CYC = N_CYC_I + EXTRA
PERIOD = 11
DELTAS = (1, 10, 11, 12)
ROWS = (5, 8)
TAG = "a221o_fold_windows"

PROBES = [
    ("I", "I"),
    ("enable", "enable"),
    ("sticky", "sky130_fd_sc_hd__inv_2_11__A"),
    ("inv23_A", "sky130_fd_sc_hd__inv_2_23__A"),
    ("a221o_X", "sky130_fd_sc_hd__a221o_2_1__X"),
    ("a31o_X", "sky130_fd_sc_hd__a31o_2_12__X"),
    ("inv7_A", "sky130_fd_sc_hd__inv_2_7__A"),
    ("or4_X", "sky130_fd_sc_hd__or4_2_4__X"),
    ("success", "success"),
]


def build_modes() -> list[tuple[str, str, dict]]:
    modes: list[tuple[str, str, dict]] = []
    modes.append(("ctl_all0", pat_bits(N_CYC, []), {"suite": "control", "ones": []}))
    for row in ROWS:
        for r in (0, 9, 10):
            t1 = PERIOD * row + r
            modes.append(
                (
                    f"ctl_single_r{r}_row{row}",
                    pat_bits(N_CYC, [t1]),
                    {"suite": "control", "ones": [t1]},
                )
            )
    for d in DELTAS:
        for row in ROWS:
            for r in range(PERIOD):
                t1 = PERIOD * row + r
                t0 = t1 - d
                if t0 < 0 or t1 >= N_CYC_I:
                    continue
                modes.append(
                    (
                        f"d{d}_r{r}_row{row}",
                        pat_bits(N_CYC, [t0, t1]),
                        {
                            "suite": "pair",
                            "delta": d,
                            "residue": r,
                            "row": row,
                            "ones": [t0, t1],
                        },
                    )
                )
    return modes


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    modes = build_modes()
    print(f"sweep n_cyc={N_CYC} modes={len(modes)}")
    rows = run_probe(
        root=ROOT,
        build=BUILD,
        out_dir=OUT,
        tag=TAG,
        probes=PROBES,
        modes=[(n, b) for n, b, _ in modes],
        n_cyc=N_CYC,
    )
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["mode_name"], []).append(r)

    def highs(rs: list[dict], lab: str) -> list[int]:
        return [int(x["cyc"]) for x in rs if int(x[lab])]

    recs = []
    for name, _bits, meta in modes:
        rs = by[name]
        st = highs(rs, "sticky")
        recs.append(
            {
                "mode": name,
                **meta,
                "sticky_n": len(st),
                "sticky_first": st[0] if st else None,
                "armed": bool(st),
                "a221o_n": len(highs(rs, "a221o_X")),
                "success_n": len(highs(rs, "success")),
            }
        )

    # allowed residue = pair present but sticky never armed, in BOTH rows
    allowed: dict[int, list[int]] = {}
    disagree: list[dict] = []
    for d in DELTAS:
        ok = []
        for r in range(PERIOD):
            got = [x for x in recs if x.get("delta") == d and x.get("residue") == r]
            if not got:
                continue
            armed = {x["armed"] for x in got}
            if len(armed) > 1:
                disagree.append({"delta": d, "residue": r, "rows": got})
            elif not any(armed):
                ok.append(r)
        allowed[d] = ok

    coded_now = {1: [0], 10: [10], 11: [], 12: [0]}
    rule_txt = {1: [10], 10: [9], 11: [], 12: [10]}

    payload = {
        "n_cyc": N_CYC,
        "rows_tested": list(ROWS),
        "observe": "sky130_fd_sc_hd__inv_2_11__A (dfrtp_2_37.Q sticky)",
        "criterion": "residue ALLOWED when a two-one pair does NOT arm the sticky",
        "measured_allowed": {str(k): v for k, v in allowed.items()},
        "matches_patched_forcer": {
            str(d): allowed[d] == coded_now[d] for d in DELTAS
        },
        "matches_rule_txt": {str(d): allowed[d] == rule_txt[d] for d in DELTAS},
        "row_disagreements": disagree,
        "modes": recs,
    }
    (OUT / "fold_windows.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# a221o fold — measured allowed windows",
        "",
        f"Observe: `inv_2_11__A` (= `dfrtp_2_37.Q`, set-once sticky). "
        f"Sim length **{N_CYC}** (121 + {EXTRA}). Rows tested: `{list(ROWS)}`.",
        "",
        "A residue is **allowed** when a two-one pair at that spacing does "
        "**not** arm the sticky.",
        "",
        "## Controls",
        "",
        "| mode | ones | sticky armed |",
        "|------|------|:-----------:|",
    ]
    for x in recs:
        if x["suite"] != "control":
            continue
        md.append(f"| `{x['mode']}` | `{x['ones']}` | {'YES' if x['armed'] else 'no'} |")
    md += [
        "",
        "## Measured allowed residues",
        "",
        "| Δ | measured | patched forcer | rule .txt | agrees with |",
        "|--:|----------|----------------|-----------|-------------|",
    ]
    for d in DELTAS:
        m = allowed[d]
        who = []
        if m == coded_now[d]:
            who.append("patched forcer")
        if m == rule_txt[d]:
            who.append("rule .txt")
        md.append(
            f"| {d} | `{m}` | `{coded_now[d]}` | `{rule_txt[d]}` | "
            f"{' + '.join(who) if who else '**neither**'} |"
        )
    md += ["", "## Per-pair detail", "", "| Δ | residue | row | ones | sticky first | armed |", "|--:|--------:|----:|------|-------------:|:-----:|"]
    for x in recs:
        if x["suite"] != "pair":
            continue
        md.append(
            f"| {x['delta']} | {x['residue']} | {x['row']} | `{x['ones']}` | "
            f"{x['sticky_first'] if x['sticky_first'] is not None else '—'} | "
            f"{'YES' if x['armed'] else 'no'} |"
        )
    if disagree:
        md += ["", f"**Row disagreements: {len(disagree)}** — see JSON.", ""]
    md += [
        "",
        "JSON: [`fold_windows.json`](fold_windows.json)",
        "",
        "```bash",
        "python3 phase3/a221o_set/run_fold_window_sweep.py",
        "```",
        "",
    ]
    (OUT / "fold_windows.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT / 'fold_windows.md'}")
    for d in DELTAS:
        print(
            f"  delta={d:>2} allowed={allowed[d]} "
            f"(patched={coded_now[d]} rule_txt={rule_txt[d]})"
        )
    if disagree:
        print(f"  WARNING row disagreements: {len(disagree)}")


if __name__ == "__main__":
    main()
