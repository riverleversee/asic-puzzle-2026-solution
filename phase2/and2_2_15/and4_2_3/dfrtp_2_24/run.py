#!/usr/bin/env python3
"""Expand and4_2_3 pin subfolder `dfrtp_2_24`.

From rework_coded/:
  python3 phase2/and2_2_15/and4_2_3/dfrtp_2_24/run.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "expand_pin_subs.py"
sys.argv = [str(TOOL), "--only", "dfrtp_2_24", *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
