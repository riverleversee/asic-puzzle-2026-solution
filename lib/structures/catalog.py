#!/usr/bin/env python3
"""Deterministic logic-structure pattern catalog (pin-connectivity rules only)."""
from __future__ import annotations

from typing import Callable

from structures.graph import (
    Check,
    Match,
    cell_family,
    find_flop_driven_by,
    short,
)

Matcher = Callable[[dict], list]

def match_mux_hold_flop_stage(drivers: dict) -> list[Match]:
    hits: list[Match] = []
    for net, info in drivers.items():
        if info.get("class") != "mux":
            continue
        pins = info.get("in_pins") or {}
        a0, a1, s = pins.get("A0"), pins.get("A1"), pins.get("S")
        flop = find_flop_driven_by(drivers, net)
        if flop is None:
            continue
        q, finfo = flop
        checks = [
            Check("A0_holds_Q", a0 == q, f"A0={short(a0 or '?')} Q={short(q)}"),
            Check("flop_D_is_mux_X", finfo["in_pins"].get("D") == net, "D=mux.X"),
            Check("has_S", bool(s), short(s) if s else "missing"),
            Check("has_A1", bool(a1), short(a1) if a1 else "missing"),
        ]
        ok = all(c.ok for c in checks)
        if not ok:
            continue
        hits.append(
            Match(
                pattern_id="mux_hold_flop_stage",
                anchor=q,
                ports={"S": s or "", "din": a1 or "", "Q": q, "mux_X": net},
                members={net, q},
                checks=checks,
                ok=True,
                extra={
                    "mux": short(info["instance"]),
                    "flop": short(finfo["instance"]),
                },
            )
        )
    return hits


def match_and2b_enable_gate(drivers: dict) -> list[Match]:
    hits = []
    for net, info in drivers.items():
        if "and2b" not in (info.get("cell") or "").lower():
            continue
        pins = info.get("in_pins") or {}
        if pins.get("B") != "enable":
            continue
        hits.append(
            Match(
                pattern_id="and2b_enable_gate",
                anchor=net,
                ports={"A_N": pins.get("A_N", ""), "B": "enable", "Y": net},
                members={net},
                checks=[Check("B_is_enable", True, "B=enable")],
                ok=True,
                extra={"instance": short(info["instance"])},
            )
        )
    return hits


def match_inv_on_flop_Q(drivers: dict) -> list[Match]:
    hits = []
    for net, info in drivers.items():
        if info.get("class") != "inv":
            continue
        a = (info.get("in_pins") or {}).get("A")
        if not a:
            continue
        drv = drivers.get(a)
        if not drv or drv.get("class") != "flop":
            continue
        hits.append(
            Match(
                pattern_id="inv_on_flop_Q",
                anchor=net,
                ports={"A": a, "Y": net},
                members={net, a},
                checks=[Check("A_is_flop_Q", True, short(a))],
                ok=True,
                extra={"inv": short(info["instance"]), "flop": short(drv["instance"])},
            )
        )
    return hits


def match_nand2_I_gate(drivers: dict) -> list[Match]:
    hits = []
    for net, info in drivers.items():
        if "nand2" not in (info.get("cell") or "").lower():
            continue
        pins = info.get("in_pins") or {}
        if pins.get("A") != "I" and pins.get("B") != "I":
            continue
        other = pins.get("B") if pins.get("A") == "I" else pins.get("A")
        hits.append(
            Match(
                pattern_id="nand2_I_gate",
                anchor=net,
                ports={"I": "I", "other": other or "", "Y": net},
                members={net},
                checks=[Check("has_I_pin", True, "I")],
                ok=True,
                extra={"instance": short(info["instance"])},
            )
        )
    return hits


def match_sticky_ao_latch(drivers: dict) -> list[Match]:
    """AO cell with some input = flop Q and flop.D == AO output."""
    hits = []
    for net, info in drivers.items():
        if info.get("class") != "aoi":
            continue
        fam = cell_family(info)
        if fam not in ("a31o", "a32o", "a21o", "a22o", "a221o"):
            continue
        pins = info.get("in_pins") or {}
        for pin, pnet in pins.items():
            drv = drivers.get(pnet)
            if not drv or drv.get("class") != "flop":
                continue
            if drv["in_pins"].get("D") != net:
                continue
            # feedback pin found
            set_pins = {k: v for k, v in pins.items() if k != pin}
            hits.append(
                Match(
                    pattern_id="sticky_ao_latch",
                    anchor=net,
                    ports={"Y": net, "Q": pnet, "feedback_pin": pin, **{f"in_{k}": v for k, v in set_pins.items()}},
                    members={net, pnet},
                    checks=[
                        Check("feedback_is_flop_Q", True, f"{pin}={short(pnet)}"),
                        Check("flop_D_is_Y", True, f"D={short(net)}"),
                    ],
                    ok=True,
                    extra={
                        "cell_family": fam,
                        "instance": short(info["instance"]),
                        "flop": short(drv["instance"]),
                        "feedback_pin": pin,
                    },
                )
            )
            break
    return hits


def match_enabled_mux_shift_register(drivers: dict) -> list[Match]:
    """Discover chains of mux_hold_flop_stage with shared S; stage0 A1=I or continue from any."""
    stages = match_mux_hold_flop_stage(drivers)
    by_q = {m.ports["Q"]: m for m in stages}
    by_din = {}
    for m in stages:
        by_din.setdefault(m.ports.get("din"), []).append(m)

    used_q: set[str] = set()
    chains: list[Match] = []

    # Prefer chains that start at I
    seeds = [m for m in stages if m.ports.get("din") == "I"]
    # Also any stage whose din is not another stage Q (orphan starts)
    for m in stages:
        if m.ports.get("din") not in by_q and m not in seeds:
            seeds.append(m)

    for seed in seeds:
        if seed.ports["Q"] in used_q:
            continue
        s0 = seed.ports.get("S")
        chain = [seed]
        cur = seed
        while True:
            nxts = [
                m
                for m in by_din.get(cur.ports["Q"], [])
                if m.ports.get("S") == s0 and m.ports["Q"] not in used_q
            ]
            if not nxts:
                break
            nxt = nxts[0]
            chain.append(nxt)
            cur = nxt
        if len(chain) < 2:
            continue
        for st in chain:
            used_q.add(st.ports["Q"])
        members: set[str] = set()
        for st in chain:
            members |= st.members
        chains.append(
            Match(
                pattern_id="enabled_mux_shift_register",
                anchor=chain[0].ports["Q"],
                ports={
                    "S": s0 or "",
                    "din0": chain[0].ports.get("din") or "",
                    "Q0": chain[0].ports["Q"],
                    "Q_last": chain[-1].ports["Q"],
                },
                members=members,
                checks=[
                    Check("n_stages_ge_2", True, f"n={len(chain)}"),
                    Check("shared_S", True, short(s0 or "")),
                ],
                ok=True,
                extra={
                    "n_stages": len(chain),
                    "stages": [
                        {
                            "i": i,
                            "Q": short(st.ports["Q"]),
                            "mux": st.extra.get("mux"),
                            "flop": st.extra.get("flop"),
                            "din": short(st.ports.get("din") or ""),
                        }
                        for i, st in enumerate(chain)
                    ],
                },
            )
        )
    return chains


def match_andN_flopped_inputs(drivers: dict) -> list[Match]:
    hits = []
    for net, info in drivers.items():
        fam = cell_family(info)
        if fam not in ("and2", "and3", "and4"):
            continue
        if "and2b" in (info.get("cell") or "").lower():
            continue
        pins = info.get("in_pins") or {}
        flop_ins = {
            p: n
            for p, n in pins.items()
            if (drivers.get(n) or {}).get("class") == "flop"
        }
        if len(flop_ins) < 2:
            continue
        hits.append(
            Match(
                pattern_id="andN_flopped_inputs",
                anchor=net,
                ports={"Y": net, **flop_ins},
                members={net, *flop_ins.values()},
                checks=[Check("ge2_flop_inputs", True, f"n={len(flop_ins)}")],
                ok=True,
                extra={
                    "family": fam,
                    "instance": short(info["instance"]),
                    "n_flop_inputs": len(flop_ins),
                },
            )
        )
    return hits


def match_fa_prior_stub_driver(drivers: dict, stubs: set[str] | None = None) -> list[Match]:
    """Outputs whose fan-in never reaches I but reach FA endpoints."""
    stubs = stubs or set()
    try:
        from render_success_logic_depth import load_fa_endpoints, reaches_I
        from structures.graph import fanin_cone
    except ImportError:
        return []

    ends = load_fa_endpoints(drivers)
    fa_any: set[str] = set(ends.get("fa_any") or [])
    hits = []
    seen: set[str] = set()
    for net, info in drivers.items():
        if net in seen or net in ("I", "enable"):
            continue
        if reaches_I(net, drivers, stubs):
            continue
        cone = fanin_cone(net, drivers)
        if not (cone & fa_any) and net not in fa_any:
            continue
        fam = cell_family(info)
        if fam not in ("and2b", "and4bb", "or4bb", "or4", "inv", "and4", "nor", "nand"):
            continue
        seen.add(net)
        hits.append(
            Match(
                pattern_id="fa_prior_stub_driver",
                anchor=net,
                ports={"Y": net},
                members={net},
                checks=[
                    Check("no_I", True, "reaches_I=False"),
                    Check("reaches_FA", True, "yes"),
                ],
                ok=True,
                extra={"family": fam, "instance": short(info.get("instance") or "")},
            )
        )
    return hits


PATTERNS: list[tuple[str, Matcher]] = [
    ("mux_hold_flop_stage", match_mux_hold_flop_stage),
    ("and2b_enable_gate", match_and2b_enable_gate),
    ("inv_on_flop_Q", match_inv_on_flop_Q),
    ("nand2_I_gate", match_nand2_I_gate),
    ("sticky_ao_latch", match_sticky_ao_latch),
    ("enabled_mux_shift_register", match_enabled_mux_shift_register),
    ("andN_flopped_inputs", match_andN_flopped_inputs),
]


def all_pattern_matchers() -> list[tuple[str, Matcher]]:
    return list(PATTERNS)
