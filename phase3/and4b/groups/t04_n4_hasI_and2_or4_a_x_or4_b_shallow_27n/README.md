# t04 or4b + FA→nand2(I) path

Group: `and2: or4_A × or4_B  [shallow(~27n)]`

Each sticky_or and2 sits on `or4.A × or4.B`. The shared `or4` also takes:

- **C** ← **or4b** (plotted as raw `or4.__C`)
- **D** ← **nand2(I, inv_2_7__A)**; `inv_2_7__A` = **and2b_2_11.Y**
- **and2b_2_11**: `A_N=or2_2_11__A` (FA in), `B=enable`, `Y=inv_2_7__A`

Stimulus: **all0**. OPEN = leaf FA-open definition from `opens_exact_shift1`.

| Leaf | and2 | or4 | or4b→C | nand2→D | open def |
|------|------|-----|--------|---------|----------|
| `a6.A` | `and2_2_11` | `or4_2_9` | `or4b_2_4`→`or4_2_9__C` | `nand2_2_33` | `or4_2_4`==`1000` |
| `a6.D` | `and2_2_12` | `or4_2_7` | `or4b_2_6`→`or4_2_7__C` | `nand2_2_36` | `or4_2_4`==`0100` |
| `a5.B` | `and2_2_13` | `or4_2_8` | `or4b_2_5`→`or4_2_8__C` | `nand2_2_37` | `or4_2_4`==`0010` |
| `a12.B` | `and2_2_14` | `or4_2_6` | `or4b_2_7`→`or4_2_6__C` | `nand2_2_35` | `or4_2_4`==`0001` |

## Artifacts

- [`open_log.md`](open_log.md) / [`open_log.csv`](open_log.csv)
- [`FA_open_timeline.png`](FA_open_timeline.png) — or4b C vs OPEN vs and2b
- [`k_ones_flops.md`](k_ones_flops.md) / [`k_ones_flops.csv`](k_ones_flops.csv) /
  [`k_ones_flops_timeline.png`](k_ones_flops_timeline.png) — I=1 on first k=1..5 opens; watch A/B/Y
- [`two_ones_gaps.md`](two_ones_gaps.md) / [`two_ones_gaps_timeline.png`](two_ones_gaps_timeline.png) —
  two I=1s with g=0..4 open windows skipped between them (gaps do **not** matter)
- [`three_ones_gaps.md`](three_ones_gaps.md) / [`three_ones_gaps_timeline.png`](three_ones_gaps_timeline.png) —
  three I=1s with gaps (**always dies**)
- [`two_ones_late.md`](two_ones_late.md) / [`two_ones_late_timeline.png`](two_ones_late_timeline.png) —
  two I=1s starting at opens[s], s≥1 (**still sticks**)
