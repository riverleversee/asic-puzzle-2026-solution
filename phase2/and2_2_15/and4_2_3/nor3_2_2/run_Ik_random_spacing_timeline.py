#!/usr/bin/env python3
"""nor3_2_2 Ik random-spacing — delegates to shared all-pins runner."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "run_Ik_random_spacing_all_pins.py"
sys.argv = [str(TOOL), "--pin", "nor3_2_2", *sys.argv[1:]]
runpy.run_path(str(TOOL), run_name="__main__")
