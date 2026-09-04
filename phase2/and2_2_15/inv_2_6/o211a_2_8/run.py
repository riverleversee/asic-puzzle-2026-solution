#!/usr/bin/env python3
"""Expand o211a_2_8 under inv_2_6.

From rework_coded/:
  python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "expand_o211a.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
