#!/usr/bin/env python3
"""SET-path expand behind inv_2_23 (flat).

From rework_coded/:
  python3 phase2/a221o_behind_inv23/run.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "expand_inv23.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
