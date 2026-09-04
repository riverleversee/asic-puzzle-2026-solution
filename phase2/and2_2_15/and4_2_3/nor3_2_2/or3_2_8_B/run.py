#!/usr/bin/env python3
"""Expand or3_2_8_B under nor3_2_2.

From rework_coded/:
  python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "expand_or3_2_8_B.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
