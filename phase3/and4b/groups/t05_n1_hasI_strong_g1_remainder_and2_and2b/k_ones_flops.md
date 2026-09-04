# k-ones flop watch — t05

Group: `strong g1 remainder (and2+and2b, size 1)`

For each leaf, place `I=1` on the first **k** FA-open cycles (k=1..6). Watch **A_N**, **B**, **Y** (`Y = (¬A_N) ∧ B`).

Figure: [`k_ones_flops_timeline.png`](k_ones_flops_timeline.png)

## `slot.1.A` (`and2b_2_3`)

- A_N ← `nand4_2_1__C`
- B ← `and2b_2_3__B`
- Y → `and4_2_1__A`
- opens: `[7, 17, 18, 29, 30, 41, 42]`

| k | I@opens | Y first↑ | Y last | AN final | B final | Y high cycles |
|--:|---------|---------:|-------:|---------:|--------:|--------------:|
| 1 | `[7]` | None | None | 1 | 0 | 0 |
| 2 | `[7, 17]` | 18 | 120 | 0 | 1 | 103 |
| 3 | `[7, 17, 18]` | 18 | 18 | 1 | 1 | 1 |
| 4 | `[7, 17, 18, 29]` | 18 | 18 | 1 | 1 | 1 |
| 5 | `[7, 17, 18, 29, 30]` | 18 | 18 | 1 | 1 | 1 |
| 6 | `[7, 17, 18, 29, 30, 41]` | 18 | 18 | 1 | 1 | 1 |
