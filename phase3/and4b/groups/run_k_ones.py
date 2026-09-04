#!/usr/bin/env python3
"""k-ones flop timelines

From rework_coded/:
  python3 phase3/and4b/groups/run_k_ones.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "phase3_k_ones_flops_timeline.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
