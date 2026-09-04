#!/usr/bin/env python3
"""expand and4b type groups

From rework_coded/:
  python3 phase2/and4b/groups/run_expand.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "expand_and4b_main_groups.py"
sys.argv = [str(TOOL), *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
