#!/usr/bin/env python3
"""Phase 4 forcer — leaf Σ=2 + period exactly-2 + a221o neighbor/hot-offset.

Rules (phase3, aligned):
  • each and4b hasI leaf: exactly 2 ones on FA opens  (= slot oracle)
  • each period-11 cycle: exactly 2 ones (≤2 while partial)
  • neighbor / Δ∈{1,10,11,12}: partner forced 0 unless later on allowed window
        Δ∈{1,12} → later ≡ 0  (mod 11)
        Δ=10     → later ≡ 10 (mod 11)
        Δ=11     → never
  • D-leaf Σ=2 → hold remaining opens to 0

Usage (from rework_coded/):
  python3 phase4/run_forcer.py --skip-triples
  python3 phase4/run_forcer.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
OUT = HERE / "out"
N_CYC = 121
PERIOD = 11
NEED = 2
MAX_COMBOS = 500_000
HOT_DELTAS = (1, 10, 11, 12)


def load_leaves(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["opens"] if isinstance(data, dict) and "opens" in data else data
    return [
        {
            "name": r["name"],
            "kind": r.get("kind", "set_once"),
            "bank": r.get("bank", "main"),
            "opens": list(r.get("opens_all0") or r.get("opens") or []),
        }
        for r in rows
    ]


def d_leaves(leaves: list[dict]) -> list[dict]:
    return [L for L in leaves if L["bank"] == "and4b_D"]


def main_leaves(leaves: list[dict]) -> list[dict]:
    return sorted(
        [L for L in leaves if L["bank"] != "and4b_D"],
        key=lambda L: (len(L["opens"]), L["name"]),
    )


def fa_period_counts(ones: set[int]) -> list[int]:
    return [
        sum(1 for c in ones if w * PERIOD <= c < (w + 1) * PERIOD)
        for w in range(N_CYC // PERIOD)
    ]


def later_allowed(delta: int, later: int) -> bool:
    # Windows are grid-adjacency under col = cyc % 11, row = cyc // 11 — the same
    # numbering leaf_sigma_ok() and fa_period_counts() use. A pair at delta is
    # legal only when it wraps a row boundary and so does not touch.
    if delta == 11:
        return False
    if delta in (1, 12):
        return later % PERIOD == 0
    if delta == 10:
        return later % PERIOD == 10
    return True


def propagate_hot_offset(ones: set[int]) -> set[int]:
    """Force partners to 0 when (t, t±Δ) would be a forbidden fold pair."""
    z: set[int] = set()
    for t in ones:
        for k in HOT_DELTAS:
            later = t + k
            if later < N_CYC and not later_allowed(k, later):
                z.add(later)
            earlier = t - k
            if earlier >= 0 and not later_allowed(k, t):
                z.add(earlier)
    return z - ones


def fold_pairs_ok(ones: set[int]) -> bool:
    s = sorted(ones)
    for i, a in enumerate(s):
        for b in s[i + 1 :]:
            d = b - a
            if d in HOT_DELTAS and not later_allowed(d, b):
                return False
    return True


def propagate_d_hold(ones: set[int], d_bank: list[dict]) -> set[int]:
    z: set[int] = set()
    for L in d_bank:
        O = set(L["opens"])
        hits = ones & O
        if len(hits) == NEED:
            z |= O - hits
    return z - ones


def propagate_zeros(ones: set[int], d_bank: list[dict]) -> set[int]:
    return (propagate_hot_offset(ones) | propagate_d_hold(ones, d_bank)) - ones


def locks_consistent(ones: set[int], force_1: set[int], force_0: set[int]) -> bool:
    return not (ones & force_0) and not (force_1 - ones)


def leaf_sigma_ok(ones: set[int], focus: list[dict]) -> bool:
    return all(len(ones & set(L["opens"])) == NEED for L in focus)


def d_over_hit(ones: set[int], d_bank: list[dict]) -> bool:
    return any(len(ones & set(L["opens"])) > NEED for L in d_bank)


def survivor_ok(
    ones: set[int],
    focus: list[dict],
    force_1: set[int],
    force_0: set[int],
    d_bank: list[dict],
) -> bool:
    if not locks_consistent(ones, force_1, force_0):
        return False
    if not leaf_sigma_ok(ones, focus):
        return False
    if d_over_hit(ones, d_bank):
        return False
    if any(n > NEED for n in fa_period_counts(ones)):
        return False
    if not fold_pairs_ok(ones):
        return False
    prop0 = propagate_zeros(ones, d_bank)
    if prop0 & ones or prop0 & force_1:
        return False
    return True


def free_opens(leaf: dict, force_1: set[int], force_0: set[int]) -> list[int]:
    return [c for c in leaf["opens"] if c not in force_0 and c not in force_1]


def enumerate_combos(free: list[int], need_pick: int) -> list[tuple[int, ...]]:
    if need_pick == 0:
        return [()]
    n = len(free)
    if n < need_pick:
        return []
    count = 1
    for i in range(1, need_pick + 1):
        count = count * (n - i + 1) // i
    if count > MAX_COMBOS:
        return []
    return list(combinations(free, need_pick))


def analyze_focus(
    focus: list[dict],
    force_1: set[int],
    force_0: set[int],
    d_bank: list[dict],
) -> dict:
    names = [L["name"] for L in focus]
    per: list[dict] = []
    total = 1
    for L in focus:
        opens = set(L["opens"])
        fixed_1 = sorted(opens & force_1)
        free = free_opens(L, force_1, force_0)
        if len(fixed_1) > NEED:
            return {"status": "OVER_HIT", "focus": names}
        need_pick = NEED - len(fixed_1)
        if len(free) < need_pick:
            return {"status": "UNSAT", "focus": names}
        combos = enumerate_combos(free, need_pick)
        if need_pick and not combos:
            return {"status": "SKIP_TOO_MANY", "focus": names}
        total *= max(len(combos), 1)
        if total > MAX_COMBOS:
            return {"status": "SKIP_TOO_MANY", "focus": names, "n_combos": total}
        per.append({"fixed_1": fixed_1, "free": free, "combos": combos})

    survivors = []
    for picks in product(*(p["combos"] for p in per)):
        ones = force_1 | set().union(*(set(pick) for pick in picks))
        if not survivor_ok(ones, focus, force_1, force_0, d_bank):
            continue
        survivors.append({"ones": ones, "prop0": propagate_zeros(ones, d_bank)})

    if not survivors:
        return {"status": "UNSAT", "focus": names, "n_combos": total, "n_survivors": 0}

    inter_ones = set.intersection(*(s["ones"] for s in survivors))
    inter_prop0 = set.intersection(*(s["prop0"] for s in survivors))
    all_free: set[int] = set()
    for p in per:
        all_free |= set(p["free"])
    inter_free0 = {c for c in all_free if all(c not in s["ones"] for s in survivors)}
    return {
        "status": "OK",
        "focus": names,
        "n_combos": total,
        "n_survivors": len(survivors),
        "new_force_1": sorted(inter_ones - force_1),
        "new_force_0": sorted((inter_prop0 | inter_free0) - force_0 - force_1),
    }


def close_force(
    force_1: set[int], force_0: set[int], d_bank: list[dict]
) -> tuple[set[int], set[int]]:
    while True:
        prop = propagate_zeros(force_1, d_bank)
        new0 = prop - force_0 - force_1
        if not new0:
            break
        force_0 |= new0
    # Period exact-2: if a period already has 2 forced ones, zero the rest
    for w in range(N_CYC // PERIOD):
        lo, hi = w * PERIOD, (w + 1) * PERIOD
        hits = {c for c in force_1 if lo <= c < hi}
        if len(hits) == NEED:
            force_0 |= set(range(lo, hi)) - hits
        force_0 -= force_1
    return force_1, force_0


def apply_locks(
    force_1: set[int],
    force_0: set[int],
    new_f1: list[int],
    new_f0: list[int],
    d_bank: list[dict],
) -> tuple[set[int], set[int], bool]:
    before = (len(force_1), len(force_0))
    force_1 |= set(new_f1)
    force_0 |= set(new_f0)
    force_0 -= force_1
    force_1, force_0 = close_force(force_1, force_0, d_bank)
    return force_1, force_0, (len(force_1), len(force_0)) != before


def fixpoint_k(
    mains: list[dict],
    force_1: set[int],
    force_0: set[int],
    d_bank: list[dict],
    k: int,
) -> tuple[set[int], set[int], int]:
    sweep = 0
    groups = list(combinations(mains, k))
    while True:
        sweep += 1
        changed = False
        for group in groups:
            r = analyze_focus(list(group), force_1, force_0, d_bank)
            if r.get("status") != "OK":
                continue
            force_1, force_0, ch = apply_locks(
                force_1,
                force_0,
                r.get("new_force_1", []),
                r.get("new_force_0", []),
                d_bank,
            )
            changed |= ch
        if not changed:
            break
    return force_1, force_0, sweep


def write_out(
    opens_src: str,
    force_1: set[int],
    force_0: set[int],
    sweeps: dict,
    leaves: list[dict],
    cpsat_ones: set[int] | None,
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    unid = sorted(c for c in range(N_CYC) if c not in force_1 and c not in force_0)
    period = fa_period_counts(force_1)
    payload = {
        "schema": 2,
        "method": "phase4_forcer",
        "opens_src": opens_src,
        "rules": [
            "leaf_sigma2",
            "period11_exact2",
            "a221o_hot_offset_allowed_windows",
            "d_hold",
        ],
        "sweeps": sweeps,
        "force_1": sorted(force_1),
        "force_0": sorted(force_0),
        "unidentified": unid,
        "period_ones": period,
        "n_force_1": len(force_1),
        "n_force_0": len(force_0),
        "n_unidentified": len(unid),
        "leaf_sigma": [
            {
                "name": L["name"],
                "bank": L["bank"],
                "sigma": len(set(L["opens"]) & force_1),
                "n_opens": len(L["opens"]),
            }
            for L in leaves
        ],
    }
    if cpsat_ones is not None:
        payload["vs_cpsat_exact"] = {
            "cpsat_n": len(cpsat_ones),
            "match_force1": force_1 == cpsat_ones,
            "missing_from_forcer": sorted(cpsat_ones - force_1),
            "extra_in_forcer": sorted(force_1 - cpsat_ones),
            "cpsat_covered": cpsat_ones <= force_1,
        }
    (OUT / "forced.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Phase 4 — forced I",
        "",
        f"Opens: `{opens_src}`",
        "",
        "Rules: leaf Σ=2 · period-11 **exactly 2** · a221o hot-offset "
        "(Δ 1/12 → later≡0; Δ10 → later≡10; Δ11 never) · D-hold",
        "",
        f"Sweeps: `{sweeps}`",
        "",
        f"**I=1 ({len(force_1)}):** `{sorted(force_1)}`",
        "",
        f"**I=0 ({len(force_0)}):** `{sorted(force_0)}`",
        "",
        f"**Unidentified ({len(unid)}):** `{unid}`",
        "",
        f"Period ones: `{period}` "
        + ("(all 2 ✓)" if period == [NEED] * 11 else ""),
        "",
    ]
    if cpsat_ones is not None:
        v = payload["vs_cpsat_exact"]
        md += [
            "## vs `cpsat_exact`",
            "",
            f"- match force_1: **{v['match_force1']}**",
            f"- missing: `{v['missing_from_forcer']}`",
            f"- extra: `{v['extra_in_forcer']}`",
            "",
        ]
    md += ["```bash", "python3 phase4/run_forcer.py --skip-triples", "```", ""]
    (OUT / "forced.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT / 'forced.md'}")
    print(
        f"I=1:{len(force_1)} I=0:{len(force_0)} unid:{len(unid)} period={period}"
    )
    if cpsat_ones is not None:
        print(
            f"vs cpsat: match={force_1 == cpsat_ones} "
            f"missing={sorted(cpsat_ones - force_1)} extra={sorted(force_1 - cpsat_ones)}"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--opens",
        type=Path,
        default=REPO / "sim" / "opens_exact_shift1.json",
    )
    ap.add_argument("--skip-pairs", action="store_true")
    ap.add_argument("--skip-triples", action="store_true")
    args = ap.parse_args()

    opens_path = args.opens
    if not opens_path.is_file():
        opens_path = REPO / "sim" / "retrace_all22_opens_structural.json"
    leaves = load_leaves(opens_path)
    mains = main_leaves(leaves)
    d_bank = d_leaves(leaves)
    try:
        opens_src = str(opens_path.relative_to(REPO))
    except ValueError:
        opens_src = str(opens_path)
    print(f"leaves={len(leaves)} mains={len(mains)} d={len(d_bank)} opens={opens_src}")

    cpsat_ones = None
    cpsat = REPO / "sim" / "cpsat_exact.json"
    if cpsat.is_file():
        cpsat_ones = set(json.loads(cpsat.read_text())["I_ones"])

    force_1: set[int] = set()
    force_0: set[int] = set()
    force_1, force_0 = close_force(force_1, force_0, d_bank)
    sweeps: dict[str, int] = {}

    t0 = time.time()
    force_1, force_0, s1 = fixpoint_k(mains, force_1, force_0, d_bank, 1)
    sweeps["solo"] = s1
    print(f"solo sweeps={s1} I=1:{len(force_1)} I=0:{len(force_0)} ({time.time()-t0:.1f}s)")

    if not args.skip_pairs:
        t1 = time.time()
        force_1, force_0, s2 = fixpoint_k(mains, force_1, force_0, d_bank, 2)
        sweeps["pairs"] = s2
        print(
            f"pairs sweeps={s2} I=1:{len(force_1)} I=0:{len(force_0)} ({time.time()-t1:.1f}s)"
        )

    if not args.skip_triples:
        t2 = time.time()
        force_1, force_0, s3 = fixpoint_k(mains, force_1, force_0, d_bank, 3)
        sweeps["triples"] = s3
        print(
            f"triples sweeps={s3} I=1:{len(force_1)} I=0:{len(force_0)} ({time.time()-t2:.1f}s)"
        )

    write_out(opens_src, force_1, force_0, sweeps, leaves, cpsat_ones)


if __name__ == "__main__":
    main()
