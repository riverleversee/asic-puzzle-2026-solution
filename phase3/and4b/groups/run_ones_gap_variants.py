#!/usr/bin/env python3
"""Three-ones gaps + late two-ones (t03/t04)

From rework_coded/:
  python3 phase3/and4b/groups/run_ones_gap_variants.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_ones_gap_variants.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
