#!/usr/bin/env python3
"""FA input to nand2

From rework_coded/:
  python3 phase3/and4b/groups/run_fa_input.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_fa_input_to_nand2.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
