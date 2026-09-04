#!/usr/bin/env python3
"""watch nand2b

From rework_coded/:
  python3 phase3/nand2b_B2/run_watch.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_watch_nand2b.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
