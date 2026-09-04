#!/usr/bin/env python3
"""Expand and4_2_3 pin subfolder `nor3_2_2`.

From rework_coded/:
  python3 phase2/and2_2_15/and4_2_3/nor3_2_2/run.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "expand_pin_subs.py"
sys.argv = [str(TOOL), "--only", "nor3_2_2", *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
