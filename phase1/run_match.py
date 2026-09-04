#!/usr/bin/env python3
"""Phase1 operator match

From rework_coded/:
  python3 phase1/run_match.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "match_complex_operators.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
