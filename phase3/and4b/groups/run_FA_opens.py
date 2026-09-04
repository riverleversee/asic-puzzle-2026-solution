#!/usr/bin/env python3
"""FA open watch t01/t02/t05

From rework_coded/:
  python3 phase3/and4b/groups/run_FA_opens.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_and4_I_group_opens.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
