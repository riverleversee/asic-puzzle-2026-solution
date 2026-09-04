#!/usr/bin/env python3
"""and2/and2b behind and4b compare

From rework_coded/:
  python3 phase2/and4b/behind/run_compare.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "compare_and2b_behind_and4b.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
