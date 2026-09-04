#!/usr/bin/env python3
"""Regenerate puzzle_structural.v from spice

From rework_coded/:
  python3 netlist/run_generate.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "spice_to_structural_verilog.py"
if len(sys.argv) == 1:
    sys.argv = [
        str(TOOL),
        str(HERE / "puzzle_gates.spice"),
        str(HERE / "puzzle_structural.v"),
    ]
else:
    sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
