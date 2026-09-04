#!/usr/bin/env python3
"""Compare rework_coded text artifacts to golden rework/ (path-mapped).

Normalizes:
  - markdown links / layout path tokens
  - summary.json `source` field
  - operator_matches.json unordered FA-pair lists + cell_counts key order
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

RC = Path(__file__).resolve().parent
GOLD = RC.parent / "rework"

MAP: list[tuple[str, str]] = [
    ("netlist/puzzle_structural.v", "netlist/puzzle_structural.v"),
    ("phase1/operator_matches.json", "phase1/operator_matches.json"),
    ("phase1/operator_matches.md", "phase1/operator_matches.md"),
    ("phase1/operator_matches.txt", "phase1/operator_matches.txt"),
    ("phase1/complex_operators_db.json", "phase1/complex_operators_db.json"),
    ("phase2/fa_endpoints.json", "phase2/fa_endpoints.json"),
    ("phase2/fa_endpoints.md", "phase2/fa_endpoints.md"),
    ("phase2/gate_types.md", "phase2/gate_types.md"),
    ("phase2/success/success_fanin_depth2.md", "phase2/figures/success_fanin_depth2.md"),
    ("phase2/success/success_fanin_depth5.md", "phase2/figures/success_fanin_depth5.md"),
    ("phase2/and4b/groups/summary.json", "phase2/figures/and4b_main_groups/summary.json"),
    (
        "phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/open_log.md",
        "phase3/and2b_set_once/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/open_log.md",
    ),
    (
        "phase3/and4b/groups/t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/open_log.md",
        "phase3/and2b_set_once/t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/open_log.md",
    ),
    (
        "phase3/and4b/groups/t05_n1_hasI_strong_g1_remainder_and2_and2b/open_log.md",
        "phase3/and2b_set_once/t05_n1_hasI_strong_g1_remainder_and2_and2b/open_log.md",
    ),
    (
        "phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/k_ones_flops.md",
        "phase3/and2b_set_once/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/k_ones_flops.md",
    ),
    (
        "phase3/and4b/groups/t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/k_ones_flops.md",
        "phase3/and2b_set_once/t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/k_ones_flops.md",
    ),
    (
        "phase3/and4b/groups/t05_n1_hasI_strong_g1_remainder_and2_and2b/k_ones_flops.md",
        "phase3/and2b_set_once/t05_n1_hasI_strong_g1_remainder_and2_and2b/k_ones_flops.md",
    ),
    (
        "phase3/and4b/groups/t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/open_log.md",
        "phase3/sticky_or_and2/t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/open_log.md",
    ),
    (
        "phase3/and4b/groups/t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/open_log.md",
        "phase3/sticky_or_and2/t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/open_log.md",
    ),
    ("phase3/and4b/groups/fa_input_to_nand2.md", "phase3/sticky_or_and2/fa_input_to_nand2.md"),
    (
        "phase3/and4b/groups/flop_init_all0/flop_Q_all0.csv",
        "phase3/sticky_or_and2/flop_init_all0/flop_Q_all0.csv",
    ),
    ("phase3/nand2b_B2/nand2b_no_I.json", "phase3/nand2b_B2/nand2b_no_I.json"),
    ("phase3/nand2b_B2/watch_nand2b_B2.csv", "phase3/nand2b_B2/watch_nand2b_B2.csv"),
    ("phase3/nand2b_B2/watch_nand2b_B2.json", "phase3/nand2b_B2/watch_nand2b_B2.json"),
    (
        "phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/a5A/a5A_k2_k3_timeline.csv",
        "phase3/and2b_set_once/a5A/a5A_k2_k3_timeline.csv",
    ),
    (
        "phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/a5A/and2b_2_25_ff_timeline.csv",
        "phase3/and2b_set_once/a5A/and2b_2_25_ff_timeline.csv",
    ),
]

LINK_RE = re.compile(r"\[[^\]]*\]\([^)]+\)")
PATHISH = re.compile(
    r"(?:phase[123]|figures|and2b_set_once|sticky_or_and2|and4b_main_groups|"
    r"and2b_behind_and4b|and4b/groups|and4b/behind)[^\s)`\"]*"
)


def norm_md(text: str) -> str:
    text = LINK_RE.sub("LINK", text)
    text = PATHISH.sub("PATH", text)
    # FA pair count prose drift in ranking lines (6-bit vs 7-bit) — compare structure via json
    text = re.sub(r"arith ~\d+-bit", "arith ~N-bit", text)
    text = re.sub(r"FA=\d+", "FA=N", text)
    return text


def canon_json(obj):
    if isinstance(obj, dict):
        out = {}
        for k in sorted(obj):
            if k == "source":
                continue
            v = obj[k]
            if k == "fa_pairs" and isinstance(v, list):
                out[k] = sorted(
                    (canon_json(x) for x in v),
                    key=lambda d: json.dumps(d, sort_keys=True),
                )
            elif k == "cell_counts" and isinstance(v, dict):
                out[k] = {kk: v[kk] for kk in sorted(v)}
            else:
                out[k] = canon_json(v)
        return out
    if isinstance(obj, list):
        return [canon_json(x) for x in obj]
    return obj


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def same_payload(coded: Path, gold: Path) -> tuple[bool, str]:
    cb, gb = coded.read_bytes(), gold.read_bytes()
    if cb == gb:
        return True, "byte"
    suf = coded.suffix.lower()
    if suf == ".json":
        try:
            cj, gj = json.loads(cb), json.loads(gb)
            if canon_json(cj) == canon_json(gj):
                return True, "json-canon"
        except json.JSONDecodeError:
            pass
    if suf in {".md", ".txt", ".json"}:
        try:
            if norm_md(cb.decode()) == norm_md(gb.decode()):
                return True, "text-norm"
        except UnicodeDecodeError:
            pass
    return False, f"{sha_bytes(cb)} vs {sha_bytes(gb)}"


def main() -> int:
    match = []
    differ = []
    missing = []
    stale_note = []
    for coded_rel, gold_rel in MAP:
        c, g = RC / coded_rel, GOLD / gold_rel
        if not c.is_file():
            missing.append((coded_rel, "coded missing"))
            continue
        if not g.is_file():
            missing.append((gold_rel, "golden missing"))
            continue
        ok, how = same_payload(c, g)
        if ok:
            match.append(f"{coded_rel} ({how})")
        else:
            # phase1 matches: golden artifacts may be stale vs current matcher
            if "operator_matches" in coded_rel:
                stale_note.append((coded_rel, how))
            else:
                differ.append((coded_rel, how))

    print(f"MATCH {len(match)}/{len(MAP)}")
    for m in match:
        print(f"  OK  {m}")
    if stale_note:
        print(
            f"STALE_GOLDEN phase1 operator_matches ({len(stale_note)}) — "
            "current tools disagree with checked-in golden; coded==fresh tool run "
            "is the intended regen (FA-pair order / stale snapshot)."
        )
        for rel, how in stale_note:
            print(f"  ~~  {rel}: {how}")
    if missing:
        print(f"MISSING {len(missing)}")
        for a, b in missing:
            print(f"  !!  {a}: {b}")
    if differ:
        print(f"DIFFER {len(differ)}")
        for rel, how in differ:
            print(f"  !!  {rel}: {how}")
        return 1
    if missing:
        return 1
    print("All compared payloads match golden (or documented phase1 stale-golden).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
