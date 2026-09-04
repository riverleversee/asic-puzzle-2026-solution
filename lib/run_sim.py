#!/usr/bin/env python3
"""Icarus driver — LEGACY entrypoint disabled.

Behavioral puzzle_full.v was removed (buggy spice_to_verilog).
For structural sims use:
  tools/run_puzzle_structural_all01.py
  tools/sim_leaf_pass_structural.py
  see sim/README.md

`find_iverilog()` remains for other tools that import it.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def find_iverilog() -> tuple[Path, Path]:
    candidates = [
        Path.home() / "tools" / "oss-cad-suite" / "bin",
        Path.home() / "oss-cad-suite" / "bin",
        Path("/opt/oss-cad-suite/bin"),
    ]
    for d in candidates:
        iv, vvp = d / "iverilog", d / "vvp"
        if iv.exists() and vvp.exists():
            return iv, vvp
    iv = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    if iv and vvp:
        return Path(iv), Path(vvp)
    raise SystemExit("iverilog/vvp not found — install oss-cad-suite or apt iverilog")


def main() -> None:
    raise SystemExit(
        "run_sim.py disabled with puzzle_full.v.\n"
        "Use: python3 tools/run_puzzle_structural_all01.py\n"
        "     python3 tools/sim_leaf_pass_structural.py\n"
        "See sim/README.md"
    )


if __name__ == "__main__":
    main()
