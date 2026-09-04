# t03 or4b + FA→nand2(I) path

Group: `and2: or4_A × or4_B  [deep(~110n)]`

Each sticky_or and2 sits on `or4.A × or4.B`. The shared `or4` also takes:

- **C** ← **or4b** (plotted as raw `or4.__C`)
- **D** ← **nand2(I, inv_2_7__A)**; `inv_2_7__A` = **and2b_2_11.Y**
- **and2b_2_11**: `A_N=or2_2_11__A` (FA in), `B=enable`, `Y=inv_2_7__A`

Stimulus: **all0**. OPEN = leaf FA-open definition from `opens_exact_shift1`.

| Leaf | and2 | or4 | or4b→C | nand2→D | open def |
|------|------|-----|--------|---------|----------|
| `and3.B` | `and2_2_10` | `or4_2_5` | `or4b_2_3`→`or4_2_5__C` | `nand2_2_34` | `or4_2_5__C`==0 |
| `slot.0.A` | `and2_2_3` | `or4_2_1` | `or4b_2_0`→`or4_2_1__C` | `nand2_2_14` | `or4_2_1__C`==0 |
| `slot.1.B` | `and2_2_4` | `or4_2_2` | `or4b_2_2`→`or4_2_2__C` | `nand2_2_15` | `or4_2_2__C`==0 |
| `slot.0.D` | `and2_2_5` | `or4_2_3` | `or4b_2_1`→`or4_2_3__C` | `nand2_2_13` | `or4_2_3__C`==0 |

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
