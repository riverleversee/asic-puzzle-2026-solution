# `dfrtp_2_20` — I2 every window · **per-window** random start + spacing

and4.C · dfrtp_2_20 · xnor2_2_11

Exactly **2** `I=1` in every period-`11` window, but **each window independently** draws `(off_a, off_b)` ∈ `0..10` (not a repeated pair). Sweep = `16` RNG streams (seed `20260904`).

Contrast: [`I2win_rand_spacing.md`](I2win_rand_spacing.md) uses one offset pair for all windows.

Probed **18** nets; plotted **17** non-static (≥7). Highlight `Q` → **and4.C**.

Figure: [`I2win_perwindow_rand.png`](I2win_perwindow_rand.png)

CSV: [`I2win_perwindow_rand.csv`](I2win_perwindow_rand.csv)

## Per-mode window offset pairs

| mode | #I | per-window offs `(lo,hi)` ×11 | Δ range |
|------|---:|-------------------------------|---------|
| `all0` | 0 | — | — |
| `I2pw_r01_d1-8` | 22 | `[2,10; 0,8; 2,4; 1,2; 5,9; 1,3; 5,9; 3,7; 8,9; 5,10; 1,3]` | `[1,8]` |
| `I2pw_r02_d2-8` | 22 | `[1,7; 2,10; 1,6; 2,9; 5,9; 2,10; 7,9; 0,4; 4,6; 4,9; 4,6]` | `[2,8]` |
| `I2pw_r03_d1-7` | 22 | `[1,7; 1,2; 3,9; 1,8; 6,8; 2,4; 3,6; 7,9; 0,5; 1,8; 7,10]` | `[1,7]` |
| `I2pw_r04_d1-8` | 22 | `[0,4; 6,7; 7,8; 0,6; 2,10; 2,3; 1,8; 1,7; 5,7; 6,9; 2,7]` | `[1,8]` |
| `I2pw_r05_d1-9` | 22 | `[4,9; 9,10; 4,7; 4,8; 0,9; 0,9; 1,5; 2,10; 0,9; 7,8; 1,8]` | `[1,9]` |
| `I2pw_r06_d2-9` | 22 | `[2,5; 8,10; 3,9; 2,8; 7,10; 1,10; 3,10; 4,6; 3,9; 3,7; 0,5]` | `[2,9]` |
| `I2pw_r07_d1-10` | 22 | `[1,6; 5,6; 5,8; 2,4; 7,10; 0,10; 4,5; 2,4; 3,7; 5,6; 1,9]` | `[1,10]` |
| `I2pw_r08_d1-6` | 22 | `[2,4; 2,5; 5,6; 5,7; 5,8; 7,10; 6,7; 0,5; 5,8; 4,10; 0,2]` | `[1,6]` |
| `I2pw_r09_d1-8` | 22 | `[7,8; 2,4; 7,10; 1,7; 0,7; 2,7; 7,9; 2,3; 4,9; 2,10; 2,10]` | `[1,8]` |
| `I2pw_r10_d1-9` | 22 | `[4,8; 5,7; 3,5; 1,10; 6,7; 7,10; 8,9; 3,6; 5,9; 0,3; 9,10]` | `[1,9]` |
| `I2pw_r11_d2-9` | 22 | `[2,4; 4,9; 3,6; 0,8; 1,9; 4,6; 1,6; 0,9; 0,4; 0,8; 3,8]` | `[2,9]` |
| `I2pw_r12_d1-8` | 22 | `[1,8; 0,3; 2,10; 1,3; 2,9; 2,8; 8,10; 0,7; 5,7; 5,9; 4,5]` | `[1,8]` |
| `I2pw_r13_d1-8` | 22 | `[0,7; 0,1; 1,2; 1,4; 3,7; 0,2; 0,3; 6,7; 8,9; 2,6; 0,8]` | `[1,8]` |
| `I2pw_r14_d1-10` | 22 | `[0,4; 3,9; 8,9; 2,5; 0,4; 6,10; 4,8; 0,3; 0,10; 0,1; 4,9]` | `[1,10]` |
| `I2pw_r15_d1-7` | 22 | `[8,9; 5,10; 6,8; 3,8; 0,7; 3,4; 1,8; 2,8; 1,3; 0,5; 3,10]` | `[1,7]` |
| `I2pw_r16_d1-9` | 22 | `[1,7; 4,7; 5,9; 3,9; 0,5; 4,6; 6,8; 1,7; 3,6; 0,9; 2,3]` | `[1,9]` |

## Watch activity

| lab | title | active? | flips | plotted |
|-----|-------|:-------:|------:|:-------:|
| `Q` | ★ Q → and4.C | yes | 31 | ✓ |
| `xnor_Y` | xnor.Y → flop.D | yes | 31 | ✓ |
| `xnor_B` | xnor.B | yes | 32 | ✓ |
| `and4_4D` | and4_2_4__D | yes | 32 | ✓ |
| `inv10_A` | inv_2_10__A | yes | 352 | ✓ |
| `and4_A` | sib and4.A | yes | 183 | ✓ |
| `and4_B` | sib and4.B | yes | 95 | ✓ |
| `and4_D` | sib and4.D | yes | 224 | ✓ |
| `or3_A` | or3_2_8__A | yes | 352 | ✓ |
| `or3_B` | or3_2_8__B | yes | 32 | ✓ |
| `or3_C` | or3_2_8__C | no | 0 |  |
| `or3_X` | or3_2_8__X | yes | 224 | ✓ |
| `o21a` | o21a_2_11__X | yes | 32 | ✓ |
| `a21o` | a21o_2_10__X | yes | 95 | ✓ |
| `and3_11` | and3_2_11__X | yes | 64 | ✓ |
| `nor2_Y` | nor2_2_30__Y | yes | 352 | ✓ |
| `a32o_X` | a32o_2_2__X | yes | 191 | ✓ |
| `and4_X` | and4.X | yes | 23 | ✓ |

## Observe summary

| mode | Q n | first | and4.X n |
|------|--------:|------:|---------:|
| `all0` | 0 | — | 0 |
| `I2pw_r01_d1-8` | 36 | 85 | 7 |
| `I2pw_r02_d2-8` | 39 | 82 | 4 |
| `I2pw_r03_d1-7` | 34 | 87 | 0 |
| `I2pw_r04_d1-8` | 36 | 85 | 3 |
| `I2pw_r05_d1-9` | 33 | 88 | 2 |
| `I2pw_r06_d2-9` | 37 | 84 | 5 |
| `I2pw_r07_d1-10` | 39 | 82 | 1 |
| `I2pw_r08_d1-6` | 38 | 83 | 8 |
| `I2pw_r09_d1-8` | 40 | 81 | 0 |
| `I2pw_r10_d1-9` | 37 | 84 | 0 |
| `I2pw_r11_d2-9` | 34 | 87 | 2 |
| `I2pw_r12_d1-8` | 36 | 85 | 5 |
| `I2pw_r13_d1-8` | 36 | 85 | 2 |
| `I2pw_r14_d1-10` | 40 | 81 | 1 |
| `I2pw_r15_d1-7` | 35 | 86 | 0 |
| `I2pw_r16_d1-9` | 36 | 85 | 7 |

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py --pin dfrtp_2_20
```
