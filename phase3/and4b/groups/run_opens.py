#!/usr/bin/env python3
"""t03/t04 or4b opens

From rework_coded/:
  python3 phase3/and4b/groups/run_opens.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_or4b_nand2_I_opens.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
