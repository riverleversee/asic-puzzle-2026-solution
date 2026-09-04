# `nor3_2_2` — I2 every window · random spacing sweep

and4.D · nor3_2_2

Exactly **2** `I=1` in every period-`11` window. Each of **16** modes draws a random offset pair `(off_a, off_b)` ∈ `0..10` (seed `20260904`) and repeats it in every window.

Probed **24** nets; plotted **13** non-static (≥7). Highlight `Y` → **and4.D**.

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
| `Y` | ★ Y → and4.D | yes | 223 | ✓ |
| `A` | A  dfrtp_2_21.Q | no | 0 |  |
| `B` | B  dfrtp_2_19.Q | no | 0 |  |
| `C` | C  or3_2_8__X | yes | 223 | ✓ |
| `and2b9` | and2b_2_9__X | no | 0 |  |
| `and2b9B` | and2b_2_9__B | no | 0 |  |
| `o21a12` | o21a_2_12__X | no | 0 |  |
| `o21a12A` | o21a_2_12__A1 | no | 0 |  |
| `or3_A` | or3_2_8__A | yes | 351 | ✓ |
| `or3_B` | or3_2_8__B | yes | 32 | ✓ |
| `or3_C` | or3_2_8__C | no | 0 |  |
| `a31o9` | a31o_2_9__X | no | 0 |  |
| `and4_4X` | and4_2_4__X | no | 0 |  |
| `and4_4B` | and4_2_4__B | no | 0 |  |
| `and4_4D` | and4_2_4__D | yes | 32 | ✓ |
| `xor10` | xor2_2_10__X | no | 0 |  |
| `xnor_B` | xnor2_2_11__B | yes | 32 | ✓ |
| `xnor_Y` | xnor2_2_11__Y | yes | 31 | ✓ |
| `o21a11` | o21a_2_11__X | yes | 32 | ✓ |
| `nor2_Y` | nor2_2_30__Y | yes | 352 | ✓ |
| `and4_A` | sib and4.A | yes | 188 | ✓ |
| `and4_B` | sib and4.B | yes | 95 | ✓ |
| `and4_C` | sib and4.C | yes | 31 | ✓ |
| `and4_X` | and4.X | yes | 28 | ✓ |

## Observe summary

| mode | offs | Y n | first | and4.X n |
|------|------|--------:|------:|---------:|
| `all0` | `—` | 121 | 0 | 0 |
| `I2win_r01_off1,3_d2` | `1,3` | 63 | 0 | 7 |
| `I2win_r02_off4,6_d2` | `4,6` | 63 | 0 | 4 |
| `I2win_r03_off3,8_d5` | `3,8` | 42 | 0 | 2 |
| `I2win_r04_off3,7_d4` | `3,7` | 49 | 0 | 3 |
| `I2win_r05_off0,2_d2` | `0,2` | 63 | 0 | 8 |
| `I2win_r06_off4,5_d1` | `4,5` | 70 | 0 | 5 |
| `I2win_r07_off7,8_d1` | `7,8` | 70 | 0 | 2 |
| `I2win_r08_off3,4_d1` | `3,4` | 70 | 0 | 6 |
| `I2win_r09_off4,8_d4` | `4,8` | 49 | 0 | 2 |
| `I2win_r10_off1,5_d4` | `1,5` | 49 | 0 | 5 |
| `I2win_r11_off4,7_d3` | `4,7` | 56 | 0 | 3 |
| `I2win_r12_off0,10_d10` | `0,10` | 7 | 0 | 0 |
| `I2win_r13_off3,6_d3` | `3,6` | 56 | 0 | 4 |
| `I2win_r14_off0,4_d4` | `0,4` | 49 | 0 | 6 |
| `I2win_r15_off2,9_d7` | `2,9` | 28 | 0 | 1 |
| `I2win_r16_off4,10_d6` | `4,10` | 35 | 0 | 0 |

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py --pin nor3_2_2
```
