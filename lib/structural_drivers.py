#!/usr/bin/env python3
"""Parse trusted structural Verilog into a driver map for cone tracing.

Standalone rework copy — ROOT is the `rework/` directory.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # rework/
STRUCTURAL_V = ROOT / "netlist" / "puzzle_structural.v"
GATES_SPICE = ROOT / "netlist" / "puzzle_gates.spice"

PRIMARY = {"I", "clk", "enable", "rst_n", "success"}
OUTPUT_PINS = {"X", "Y", "Q", "Q_N", "ZN", "Z"}

INST_RE = re.compile(
    r"(sky130_fd_sc_hd__\w+)\s+(sky130_fd_sc_hd__\w+)\s*\((.*?)\);",
    re.S,
)
PIN_RE = re.compile(r"\.(\w+)\s*\(\s*([^)]+?)\s*\)")


def short_cell(cell: str) -> str:
    return cell.replace("sky130_fd_sc_hd__", "")


def classify_cell(cell: str) -> str:
    c = cell.lower()
    if "dfrtp" in c or "dfxtp" in c or "dfstp" in c:
        return "flop"
    if "mux" in c:
        return "mux"
    if "xnor" in c:
        return "xnor"
    if "xor" in c:
        return "xor"
    if c.startswith("nand") or "__nand" in c:
        return "nand"
    if "and" in c and "nand" not in c:
        return "and"
    if c.startswith("nor") or "__nor" in c:
        return "nor"
    if ("__or" in c or c.startswith("or")) and "nor" not in c and "xor" not in c:
        return "or"
    if "clkbuf" in c or "buf" in c:
        return "buf"
    if any(
        x in c
        for x in (
            "a21",
            "a22",
            "a31",
            "a32",
            "a211",
            "a221",
            "a311",
            "a41",
            "o21",
            "o22",
            "o31",
            "o32",
            "o211",
            "o221",
            "o311",
            "maj",
        )
    ):
        return "aoi"
    if "inv" in c:
        return "inv"
    return "other"


def is_clk(n: str) -> bool:
    return n == "clk" or "clkbuf" in n or n.endswith("__CLK") or n.startswith("stub_og_clk")


def parse_structural(path: Path | None = None) -> tuple[dict[str, dict], set[str], dict]:
    """Return (drivers, stubs, meta). stubs is empty — OG is real cells."""
    path = path or STRUCTURAL_V
    text = path.read_text(encoding="utf-8", errors="replace")
    drivers: dict[str, dict] = {}
    n_inst = 0
    multi_out = 0

    for m in INST_RE.finditer(text):
        cell, inst, body = m.group(1), m.group(2), m.group(3)
        pins = {pm.group(1): pm.group(2).strip() for pm in PIN_RE.finditer(body)}
        outs = {p: n for p, n in pins.items() if p in OUTPUT_PINS}
        inns = {
            p: n
            for p, n in pins.items()
            if p not in OUTPUT_PINS and not n.startswith("1'b")
        }
        if not outs:
            continue
        n_inst += 1
        if len(outs) > 1:
            multi_out += 1

        cell_s = short_cell(cell)
        cls = classify_cell(cell)
        kind = "flop" if cls == "flop" else "assign"
        deps = set(inns.values())
        clk = inns.get("CLK")
        rhs = ", ".join(f"{p}={n}" for p, n in sorted(inns.items()))

        for _pin, net in outs.items():
            if net in drivers and drivers[net]["instance"] != inst:
                continue
            info = {
                "deps": set(deps),
                "in_pins": dict(inns),  # pin → net (excl. constants)
                "rhs": rhs,
                "kind": kind,
                "cell": cell_s,
                "instance": inst,
                "class": cls,
            }
            if clk:
                info["clk"] = clk
            drivers[net] = info

    try:
        rel = str(path.relative_to(ROOT))
    except ValueError:
        rel = str(path)
    meta = {
        "source": rel,
        "trusted": "rework/netlist/puzzle_structural.v from puzzle_gates.spice",
        "instances_parsed": n_inst,
        "driven_nets": len(drivers),
        "multi_output_cells": multi_out,
        "has_success": "success" in drivers,
    }
    return drivers, set(), meta


def write_provenance(path: Path, meta: dict) -> None:
    lines = [
        "# Structural cone provenance",
        "",
        "Standalone rework chain:",
        "",
        "1. `rework/netlist/puzzle_gates.spice` (Magic extract snapshot)",
        "2. `rework/tools/spice_to_structural_verilog.py` → `rework/netlist/puzzle_structural.v`",
        "3. `rework/tools/structural_drivers.py` → driver map for fan-in diagrams",
        "",
        "**Forbidden:** `puzzle_core.v`, behavioral `spice_to_verilog`, core-derived",
        "`puzzle_success_cone.v`, stub_og stand-ins when expanding success fan-in.",
        "",
        "## This run",
        "",
    ]
    for k, v in meta.items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    drivers, stubs, meta = parse_structural()
    print(meta)
    print("success driver:", drivers.get("success"))
