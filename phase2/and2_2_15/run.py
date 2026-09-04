#!/usr/bin/env python3
"""Success-entry expand behind and2_2_15 (flat).

From rework_coded/:
  python3 phase2/and2_2_15/run.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "expand_and2_15.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
