#!/usr/bin/env python3
"""Compact AO/OA (AND-OR / OR-AND) formula strings for diagram labels.

Standalone subset of sky130 compound cells used in the puzzle cone.
"""
from __future__ import annotations

import re

# Human-readable formulas (pin groups). Used on AO/OA node boxes.
AO_OA_FORMULA: dict[str, str] = {
    "a21o": "(A1∧A2)∨B1",
    "a21oi": "¬((A1∧A2)∨B1)",
    "a22o": "(A1∧A2)∨(B1∧B2)",
    "a22oi": "¬((A1∧A2)∨(B1∧B2))",
    "a31o": "(A1∧A2∧A3)∨B1",
    "a31oi": "¬((A1∧A2∧A3)∨B1)",
    "a32o": "(A1∧A2∧A3)∨(B1∧B2)",
    "a41o": "(A1∧A2∧A3∧A4)∨B1",
    "a41oi": "¬((A1∧A2∧A3∧A4)∨B1)",
    "a211o": "(A1∧A2)∨B1∨C1",
    "a211oi": "¬((A1∧A2)∨B1∨C1)",
    "a221o": "(A1∧A2)∨(B1∧B2)∨C1",
    "a221oi": "¬((A1∧A2)∨(B1∧B2)∨C1)",
    "a222o": "(A1∧A2)∨(B1∧B2)∨(C1∧C2)",
    "a311o": "(A1∧A2∧A3)∨B1∨C1",
    "a2111o": "(A1∧A2)∨B1∨C1∨D1",
    "a2111oi": "¬((A1∧A2)∨B1∨C1∨D1)",
    "a21bo": "(A1∧A2)∨(¬B1_N)",
    "a21boi": "¬((A1∧A2)∨(¬B1_N))",
    "a2bb2o": "((¬A1_N)∧(¬A2_N))∨(B1∧B2)",
    "o21a": "(A1∨A2)∧B1",
    "o21ai": "¬((A1∨A2)∧B1)",
    "o22a": "(A1∨A2)∧(B1∨B2)",
    "o22ai": "¬((A1∨A2)∧(B1∨B2))",
    "o31a": "(A1∨A2∨A3)∧B1",
    "o31ai": "¬((A1∨A2∨A3)∧B1)",
    "o32a": "(A1∨A2∨A3)∧(B1∨B2)",
    "o32ai": "¬((A1∨A2∨A3)∧(B1∨B2))",
    "o211a": "(A1∨A2)∧B1∧C1",
    "o211ai": "¬((A1∨A2)∧B1∧C1)",
    "o221a": "(A1∨A2)∧(B1∨B2)∧C1",
    "o311a": "(A1∨A2∨A3)∧B1∧C1",
    "o2111a": "(A1∨A2)∧B1∧C1∧D1",
    "o21ba": "(A1∨A2)∧(¬B1_N)",
    "o21bai": "¬((A1∨A2)∧(¬B1_N))",
    "o2bb2a": "(¬(A1_N∧A2_N))∧(B1∨B2)",
    "o2bb2ai": "¬((¬(A1_N∧A2_N))∧(B1∨B2))",
    "maj3": "maj(A,B,C)",
    "mux2": "X=S?A1:A0",
    "mux2i": "Y=¬(S?A1:A0)",
}

# Edge colors by pin letter-group for AO/OA readability.
PIN_GROUP_COLOR = {
    "A": "#c45911",  # orange — AND/OR group A
    "B": "#2e75b6",  # blue — group B
    "C": "#548235",  # green
    "D": "#7030a0",  # purple
    "?": "#666666",
}

# Mux pin colors — make S / A0 / A1 visually distinct on fan-in edges.
MUX_PIN_COLOR = {
    "S": "#1f4e79",   # select
    "A0": "#548235",  # data0 (S=0)
    "A1": "#c45911",  # data1 (S=1)
}


def cell_family(cell: str) -> str:
    """a32o_2 → a32o; sky130_fd_sc_hd__a32o_2 → a32o."""
    c = cell.replace("sky130_fd_sc_hd__", "")
    return re.sub(r"_\d+$", "", c)


def ao_oa_formula(cell: str) -> str | None:
    return AO_OA_FORMULA.get(cell_family(cell))


def pin_group(pin: str) -> str:
    m = re.match(r"^([A-Za-z])", pin)
    return m.group(1).upper() if m else "?"


def pins_for_net(in_pins: dict[str, str], net: str) -> list[str]:
    return sorted(p for p, n in in_pins.items() if n == net)


def pin_edge_style(pins: list[str]) -> tuple[str, str]:
    """Return (label, color) for an edge into an AO/OA cell."""
    if not pins:
        return ("", PIN_GROUP_COLOR["?"])
    label = "+".join(pins)
    color = PIN_GROUP_COLOR.get(pin_group(pins[0]), PIN_GROUP_COLOR["?"])
    return label, color


def mux_pin_edge_style(pins: list[str]) -> tuple[str, str]:
    """Return (label, color) for an edge into a mux (S / A0 / A1)."""
    if not pins:
        return ("", PIN_GROUP_COLOR["?"])
    label = "+".join(pins)
    # Prefer explicit mux pin color when single known pin.
    if len(pins) == 1 and pins[0] in MUX_PIN_COLOR:
        return label, MUX_PIN_COLOR[pins[0]]
    color = MUX_PIN_COLOR.get(pins[0], PIN_GROUP_COLOR["?"])
    return label, color
