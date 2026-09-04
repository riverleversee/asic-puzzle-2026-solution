#!/usr/bin/env python3
"""a5A two flops

From rework_coded/:
  python3 phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/a5A/run_two_flops.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_a5A_two_flops_vs_I.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
