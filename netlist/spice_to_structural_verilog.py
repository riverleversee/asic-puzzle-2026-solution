#!/usr/bin/env python3
"""Emit structural Verilog from Magic hierarchical gate SPICE (no behavioral rewrite).

Uses named port connections from Magic .subckt pin lists. Simulate with official
sky130_fd_sc_hd Verilog models (-DFUNCTIONAL), not our hand-written equations.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

POWER = {"VGND", "VPWR", "VPB", "VNB"}


def join_cont(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("+") and lines:
            lines[-1] += " " + line[1:].strip()
        else:
            lines.append(line)
    return lines


def vnet(name: str) -> str:
    name = name.replace("/", "__")
    name = re.sub(r"\[(\d+)\]", r"_\1", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if not name or name[0].isdigit():
        name = "n_" + name
    return name


def parse_subckts(lines: list[str]) -> dict[str, list[str]]:
    subckts: dict[str, list[str]] = {}
    cur = None
    for line in lines:
        s = line.strip()
        if s.lower().startswith(".subckt"):
            parts = s.split()
            cur = parts[1]
            # keep ALL pins including power — needed for mapping positions
            subckts[cur] = parts[2:]
        elif s.lower().startswith(".ends"):
            cur = None
    return subckts


def map_instance(subckts: dict[str, list[str]], toks: list[str]) -> tuple[str, str, dict[str, str]]:
    """Return (inst_name, cell, pin->net) including only non-power signal pins."""
    inst = toks[0][1:]
    cell = toks[-1]
    pins = subckts[cell]
    nets = toks[1:-1]
    if len(nets) != len(pins):
        # Magic sometimes inserts extra power aliases; zip min
        pass
    pin_map: dict[str, str] = {}
    for pin, net in zip(pins, nets):
        if pin.upper() in POWER:
            continue
        if net.upper() in POWER:
            # signal pin tied to power — keep as 1'b0 / 1'b1?
            if net.upper() in {"VGND", "VNB"}:
                pin_map[pin] = "1'b0"
            else:
                pin_map[pin] = "1'b1"
            continue
        pin_map[pin] = net
    return inst, cell, pin_map


def convert(spice: Path, out_v: Path, module: str) -> dict:
    lines = join_cont(spice.read_text(errors="replace"))
    subckts = parse_subckts(lines)

    ports: list[str] = []
    insts: list[tuple[str, str, dict[str, str]]] = []
    in_top = False
    skip_kw = ("fill", "decap", "tap", "diode")
    for line in lines:
        s = line.strip()
        if s.lower().startswith(f".subckt {module.lower()}"):
            ports = [p for p in s.split()[2:] if p.upper() not in POWER]
            in_top = True
            continue
        if in_top and s.lower().startswith(".ends"):
            break
        if not in_top or not s.startswith("X"):
            continue
        toks = s.split()
        cell = toks[-1]
        if any(k in cell.lower() for k in skip_kw):
            continue
        if cell.startswith("sky130_fd_pr__"):
            continue
        if cell not in subckts:
            continue
        insts.append(map_instance(subckts, toks))

    # Infer outputs: ports driven by Q/X/Y of any instance
    driven = set()
    for _i, _c, pm in insts:
        for pin, net in pm.items():
            if pin in {"Q", "X", "Y", "LO", "HI"} and not net.startswith("1'b"):
                driven.add(net)
    outputs = {"success", "S"} | {f"O[{i}]" for i in range(8)} | {f"O_{i}" for i in range(8)}
    outputs |= {p for p in ports if p in driven or vnet(p) in {vnet(d) for d in driven}}

    wires: set[str] = set()
    for _i, _c, pm in insts:
        for net in pm.values():
            if net.startswith("1'b"):
                continue
            if net not in ports:
                wires.add(net)

    out: list[str] = []
    out.append("// Structural Verilog from Magic gate-level SPICE")
    out.append(f"// Source: {spice.name}")
    out.append(f"// Instances: {len(insts)}")
    out.append("// Simulate with sky130_fd_sc_hd models: iverilog -DFUNCTIONAL ...")
    out.append(f"module {module} (")
    out.append(",\n".join(f"    {vnet(p)}" for p in ports))
    out.append(");")
    out.append("")
    for p in ports:
        pv = vnet(p)
        if p in outputs or pv in {vnet(x) for x in outputs}:
            out.append(f"  output {pv};")
        else:
            out.append(f"  input {pv};")
    out.append("")
    for w in sorted(wires, key=vnet):
        out.append(f"  wire {vnet(w)};")
    out.append("")
    cells_used: dict[str, int] = {}
    for inst, cell, pm in insts:
        cells_used[cell] = cells_used.get(cell, 0) + 1
        parts = []
        for pin, net in pm.items():
            if net.startswith("1'b"):
                parts.append(f".{pin}({net})")
            else:
                parts.append(f".{pin}({vnet(net)})")
        out.append(f"  {cell} {vnet(inst)} ( {', '.join(parts)} );")
    out.append("")
    out.append("endmodule")
    out.append("")
    out_v.parent.mkdir(parents=True, exist_ok=True)
    out_v.write_text("\n".join(out), encoding="utf-8")
    return {"instances": len(insts), "cells": cells_used, "ports": ports}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spice_in", type=Path)
    ap.add_argument("verilog_out", type=Path)
    ap.add_argument("--module", default="puzzle")
    args = ap.parse_args()
    info = convert(args.spice_in, args.verilog_out, args.module)
    print(f"Wrote {args.verilog_out} ({info['instances']} instances, {len(info['cells'])} cell types)")


if __name__ == "__main__":
    main()
