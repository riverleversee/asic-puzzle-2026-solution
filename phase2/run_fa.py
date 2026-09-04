#!/usr/bin/env python3
"""FA endpoints

From rework_coded/:
  python3 phase2/run_fa.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "identify_fa_endpoints.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
