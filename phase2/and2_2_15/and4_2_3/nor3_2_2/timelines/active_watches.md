# `nor3_2_2` — active watches (Ik random spacing)

and4.D · nor3_2_2

Probed **15** nets; plotted **7** that are non-static (target ≥7). Highlight `Y` → **and4.D** always kept.

Figure: [`active_watches.png`](active_watches.png)

CSV (all watches): [`active_watches.csv`](active_watches.csv)

## Watch activity

| lab | title | active? | flips | plotted |
|-----|-------|:-------:|------:|:-------:|
| `Y` | ★ Y → and4.D | yes | 71 | ✓ |
| `A` | A  dfrtp_2_21.Q | no | 0 | ✓ |
| `B` | B  dfrtp_2_19.Q | no | 0 | ✓ |
| `C` | C  or3_2_8__X | yes | 71 | ✓ |
| `and2b9` | and2b_2_9__X | no | 0 |  |
| `o21a12` | o21a_2_12__X | no | 0 |  |
| `or3_A` | or3_2_8__A | yes | 84 | ✓ |
| `or3_B` | or3_2_8__B | yes | 9 | ✓ |
| `or3_C` | or3_2_8__C | no | 0 |  |
| `a31o9` | a31o_2_9__X | no | 0 |  |
| `and4_4X` | and4_2_4__X | no | 0 |  |
| `xor10` | xor2_2_10__X | no | 0 |  |
| `xnor_B` | xnor2_2_11__B | no | 0 | ✓ |
| `and4_C` | sib and4.C | no | 0 |  |
| `and4_X` | and4.X | no | 0 |  |

## Observe summary (highlight)

| mode | #I | Y n | first |
|------|---:|--------:|------:|
| `all0` | 0 | 121 | 0 |
| `Ik01_n1_g—` | 1 | 16 | 0 |
| `Ik02_n2_g7` | 2 | 114 | 0 |
| `Ik03_n3_g9,4` | 3 | 40 | 0 |
| `Ik04_n4_g5,11,6` | 4 | 110 | 0 |
| `Ik05_n5_g5,1,11,3` | 5 | 73 | 0 |
| `Ik06_n6_g6,5,8,11,1` | 6 | 106 | 0 |
| `Ik07_n7_g7,5,1,3,10,11` | 7 | 45 | 0 |
| `Ik08_n8_g5,2,2,7,9,8,1` | 8 | 78 | 0 |
| `Ik09_n9_g11,3,7,7,5,1,5,3` | 9 | 34 | 0 |
| `Ik10_n10_g8,5,9,6,6,8,9,9,1` | 10 | 32 | 0 |
| `Ik11_n11_g3,4,7,8,6,10,4,5,9,4` | 11 | 66 | 0 |
| `Ik12_n12_g2,10,2,3,5,7,8,1,4,11,11` | 12 | 72 | 0 |

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py --pin nor3_2_2
```
