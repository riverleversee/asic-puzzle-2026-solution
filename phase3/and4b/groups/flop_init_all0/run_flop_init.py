#!/usr/bin/env python3
"""flop Q all0

From rework_coded/:
  python3 phase3/and4b/groups/flop_init_all0/run_flop_init.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_flop_init_all0.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
