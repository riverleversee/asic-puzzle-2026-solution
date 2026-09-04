#!/usr/bin/env python3
"""Success fan-in depth bundle

From rework_coded/:
  python3 phase2/success/run_bundle.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "render_success_logic_depth.py"
extra = sys.argv[1:]
if "--bundle" not in extra and not any(a.startswith("-") for a in extra):
    extra = ["--bundle", *extra]
sys.argv = [str(TOOL), *extra]
runpy.run_path(str(TOOL), run_name="__main__")
