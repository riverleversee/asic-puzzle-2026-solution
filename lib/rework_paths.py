#!/usr/bin/env python3
"""Shared helpers for phase3 / tools scripts."""
from __future__ import annotations

from pathlib import Path


def find_rework(start: Path | None = None) -> Path:
    p = (start or Path(__file__)).resolve()
    if p.is_file():
        p = p.parent
    for cand in [p, *p.parents]:
        if (cand / "netlist" / "puzzle_structural.v").is_file() and (
            cand / "phase3"
        ).is_dir():
            return cand
    raise SystemExit(f"cannot find rework/ root walking from {start}")


def savefig_locked(fig, out_png: Path) -> Path:
    """Write PNG via temp name; if Windows locks the target, write *_updated.png."""
    import matplotlib.pyplot as plt

    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_png.with_name(out_png.stem + ".__write__.png")
    fig.savefig(tmp)
    plt.close(fig)
    try:
        tmp.replace(out_png)
        return out_png
    except OSError:
        alt = out_png.with_name(out_png.stem + "_updated.png")
        try:
            if alt.exists():
                alt.unlink()
        except OSError:
            pass
        tmp.replace(alt)
        print(f"locked {out_png.name} → wrote {alt.name}")
        return alt
