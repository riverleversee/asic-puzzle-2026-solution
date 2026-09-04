# Phase 3 — watch `nand2b_2_23` / `a32o_2_4__B2`

Pin: **`uut.sky130_fd_sc_hd__a32o_2_4__B2`** (= `nand2b_2_23` Y).
Confirmed independent of `I` (see `nand2b_no_I.md`).

CSV: [`watch_nand2b_B2.csv`](watch_nand2b_B2.csv)  ·  cycles 0..120

## Pattern `all0`

- Cycles with Y=1: **121** / 121
- Runs: `0–120`

First rise at cyc **0** (context ±2):

| cyc | I | Y | A_N | B | a32o_X | success | or4 |
|----:|--:|--:|----:|--:|------:|--------:|-----|
| 0 | 0 | 1 | 0 | 0 | 0 | 0 | `0000` |
| 1 | 0 | 1 | 0 | 0 | 0 | 0 | `1000` |
| 2 | 0 | 1 | 0 | 0 | 0 | 0 | `0100` |

## Pattern `all1`

- Cycles with Y=1: **121** / 121
- Runs: `0–120`

First rise at cyc **0** (context ±2):

| cyc | I | Y | A_N | B | a32o_X | success | or4 |
|----:|--:|--:|----:|--:|------:|--------:|-----|
| 0 | 1 | 1 | 0 | 0 | 0 | 0 | `0000` |
| 1 | 1 | 1 | 0 | 0 | 0 | 0 | `1000` |
| 2 | 1 | 1 | 0 | 0 | 0 | 0 | `0100` |

## Pattern `cpsat`

- Cycles with Y=1: **121** / 121
- Runs: `0–120`

First rise at cyc **0** (context ±2):

| cyc | I | Y | A_N | B | a32o_X | success | or4 |
|----:|--:|--:|----:|--:|------:|--------:|-----|
| 0 | 0 | 1 | 0 | 0 | 0 | 0 | `0000` |
| 1 | 0 | 1 | 0 | 0 | 0 | 0 | `1000` |
| 2 | 0 | 1 | 0 | 0 | 0 | 0 | `0100` |

## I-independence check (sim)

all0 vs all1 `nand2b_Y` timelines identical: **True** (expected — no `I` in fan-in)
