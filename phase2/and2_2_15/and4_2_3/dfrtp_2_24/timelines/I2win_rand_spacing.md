# `dfrtp_2_24` — I2 every window · random spacing sweep

and4.A · dfrtp_2_24 · a32o_2_2

Exactly **2** `I=1` in every period-`11` window. Each of **16** modes draws a random offset pair `(off_a, off_b)` ∈ `0..10` (seed `20260904`) and repeats it in every window.

Probed **17** nets; plotted **16** non-static (≥7). Highlight `Q` → **and4.A**.

Figure: [`I2win_rand_spacing.png`](I2win_rand_spacing.png)

CSV: [`I2win_rand_spacing.csv`](I2win_rand_spacing.csv)

## Sweep pairs

| mode | offs | Δ | #I |
|------|------|--:|---:|
| `all0` | — | — | 0 |
| `I2win_r01_off1,3_d2` | `1,3` | 2 | 22 |
| `I2win_r02_off4,6_d2` | `4,6` | 2 | 22 |
| `I2win_r03_off3,8_d5` | `3,8` | 5 | 22 |
| `I2win_r04_off3,7_d4` | `3,7` | 4 | 22 |
| `I2win_r05_off0,2_d2` | `0,2` | 2 | 22 |
| `I2win_r06_off4,5_d1` | `4,5` | 1 | 22 |
| `I2win_r07_off7,8_d1` | `7,8` | 1 | 22 |
| `I2win_r08_off3,4_d1` | `3,4` | 1 | 22 |
| `I2win_r09_off4,8_d4` | `4,8` | 4 | 22 |
| `I2win_r10_off1,5_d4` | `1,5` | 4 | 22 |
| `I2win_r11_off4,7_d3` | `4,7` | 3 | 22 |
| `I2win_r12_off0,10_d10` | `0,10` | 10 | 22 |
| `I2win_r13_off3,6_d3` | `3,6` | 3 | 22 |
| `I2win_r14_off0,4_d4` | `0,4` | 4 | 22 |
| `I2win_r15_off2,9_d7` | `2,9` | 7 | 22 |
| `I2win_r16_off4,10_d6` | `4,10` | 6 | 22 |

## Watch activity

| lab | title | active? | flips | plotted |
|-----|-------|:-------:|------:|:-------:|
| `Q` | ★ Q → and4.A | yes | 188 | ✓ |
| `a32o_X` | a32o.X → flop.D | yes | 191 | ✓ |
| `A3` | A3  and3_2_10__B | yes | 191 | ✓ |
| `B1` | B1  inv_2_10__Y | yes | 351 | ✓ |
| `inv10_A` | inv_2_10__A | yes | 351 | ✓ |
| `or3_A` | or3_2_8__A | yes | 351 | ✓ |
| `or3_B` | or3_2_8__B | yes | 32 | ✓ |
| `or3_X` | or3_2_8__X | yes | 223 | ✓ |
| `nor2_Y` | nor2_2_30__Y | yes | 352 | ✓ |
| `nor2_B` | nor2_2_30__B | yes | 331 | ✓ |
| `inv7_A` | stub inv_2_7__A | no | 0 |  |
| `and4_B` | sib and4.B | yes | 95 | ✓ |
| `and4_C` | sib and4.C | yes | 31 | ✓ |
| `and4_D` | sib and4.D | yes | 223 | ✓ |
| `a21o` | a21o_2_10__X | yes | 95 | ✓ |
| `and3_11` | and3_2_11__X | yes | 64 | ✓ |
| `and4_X` | and4.X | yes | 28 | ✓ |

## Observe summary

| mode | offs | Q n | first | and4.X n |
|------|------|--------:|------:|---------:|
| `all0` | `—` | 0 | — | 0 |
| `I2win_r01_off1,3_d2` | `1,3` | 62 | 4 | 7 |
| `I2win_r02_off4,6_d2` | `4,6` | 59 | 7 | 4 |
| `I2win_r03_off3,8_d5` | `3,8` | 57 | 9 | 2 |
| `I2win_r04_off3,7_d4` | `3,7` | 58 | 8 | 3 |
| `I2win_r05_off0,2_d2` | `0,2` | 63 | 3 | 8 |
| `I2win_r06_off4,5_d1` | `4,5` | 60 | 6 | 5 |
| `I2win_r07_off7,8_d1` | `7,8` | 57 | 9 | 2 |
| `I2win_r08_off3,4_d1` | `3,4` | 61 | 5 | 6 |
| `I2win_r09_off4,8_d4` | `4,8` | 57 | 9 | 2 |
| `I2win_r10_off1,5_d4` | `1,5` | 60 | 6 | 5 |
| `I2win_r11_off4,7_d3` | `4,7` | 58 | 8 | 3 |
| `I2win_r12_off0,10_d10` | `0,10` | 55 | 11 | 0 |
| `I2win_r13_off3,6_d3` | `3,6` | 59 | 7 | 4 |
| `I2win_r14_off0,4_d4` | `0,4` | 61 | 5 | 6 |
| `I2win_r15_off2,9_d7` | `2,9` | 56 | 10 | 1 |
| `I2win_r16_off4,10_d6` | `4,10` | 55 | 11 | 0 |

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py --pin dfrtp_2_24
```
