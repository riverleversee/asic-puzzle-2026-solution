#!/usr/bin/env python3
"""strong group backtrees

From rework_coded/:
  python3 phase2/and4b/behind/run_backtrees.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "render_strong_group_backtrees.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
