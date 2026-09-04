#!/usr/bin/env python3
"""Compare inv11-safe later-cycles vs SET FA gate windows (or4 phase schedule)."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "netlist" / "structural" / "probe_all22_opens.csv"


def main() -> None:
    rows: list[tuple[int, str]] = []
    with CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["mode"]) != 0 or int(row["cyc"]) >= 121:
                continue
            s = "".join(row[f"sky130_fd_sc_hd__or4_2_4__{b}"] for b in "ABCD")
            rows.append((int(row["cyc"]), s))

    by_phase: dict[int, Counter] = {}
    for c, s in rows:
        by_phase.setdefault(c % 11, Counter())[s] += 1
    print("or4 ABCD by phase mod11:")
    for p in range(11):
        print(f"  {p}: {dict(by_phase[p])}")

    print("SET or4.X holes @ phase 0 (cyc 0,11,22,...)")
    print("SET or4bb holes @ phase 10 (cyc 10,21,32,...)")

    for d, need in [(1, "0000"), (10, "0101"), (11, None), (12, "0000")]:
        if need is None:
            print(f"inv11 Δ={d}: NEVER safe")
            continue
        safe = [c for c, s in rows if s == need]
        phases = sorted({c % 11 for c in safe})
        print(
            f"inv11 Δ={d} need or4={need!r} n={len(safe)} "
            f"phases={phases} sample={safe[:14]}"
        )


if __name__ == "__main__":
    main()
