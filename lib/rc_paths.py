#!/usr/bin/env python3
"""Locate rework_coded root and shared lib on sys.path."""
from __future__ import annotations

import sys
from pathlib import Path


def coded_root(start: Path | None = None) -> Path:
    p = (start or Path(__file__)).resolve()
    for c in [p.parent if p.is_file() else p, *p.parents]:
        if (c / "lib").is_dir() and (c / "netlist").is_dir() and (c / "phase1").is_dir():
            return c
    raise SystemExit(f"could not find rework_coded above {start}")


def ensure_lib(start: Path | None = None) -> Path:
    root = coded_root(start)
    lib = str(root / "lib")
    if lib not in sys.path:
        sys.path.insert(0, lib)
    return root
