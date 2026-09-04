# `dfrtp_2_24` — active watches (Ik random spacing)

and4.A · dfrtp_2_24 · a32o_2_2

Probed **13** nets; plotted **10** that are non-static (target ≥7). Highlight `Q` → **and4.A** always kept.

Figure: [`active_watches.png`](active_watches.png)

CSV (all watches): [`active_watches.csv`](active_watches.csv)

## Watch activity

| lab | title | active? | flips | plotted |
|-----|-------|:-------:|------:|:-------:|
| `Q` | ★ Q → and4.A | yes | 42 | ✓ |
| `a32o_X` | a32o.X → flop.D | yes | 42 | ✓ |
| `A3` | A3  and3_2_10__B | yes | 48 | ✓ |
| `B1` | B1  inv_2_10__Y | yes | 72 | ✓ |
| `inv10_A` | inv_2_10__A | yes | 72 | ✓ |
| `or3_A` | or3_2_8__A | yes | 84 | ✓ |
| `nor2_Y` | nor2_2_30__Y | yes | 84 | ✓ |
| `nor2_B` | nor2_2_30__B | yes | 78 | ✓ |
| `inv7_A` | stub inv_2_7__A | no | 0 |  |
| `and4_B` | sib and4.B | yes | 19 | ✓ |
| `and4_C` | sib and4.C | no | 0 |  |
| `and4_D` | sib and4.D | yes | 71 | ✓ |
| `and4_X` | and4.X | no | 0 |  |

## Observe summary (highlight)

| mode | #I | Q n | first |
|------|---:|--------:|------:|
| `all0` | 0 | 0 | — |
| `Ik01_n1_g—` | 1 | 0 | — |
| `Ik02_n2_g7` | 2 | 88 | 33 |
| `Ik03_n3_g9,4` | 3 | 76 | 45 |
| `Ik04_n4_g5,11,6` | 4 | 17 | 7 |
| `Ik05_n5_g5,1,11,3` | 5 | 12 | 74 |
| `Ik06_n6_g6,5,8,11,1` | 6 | 91 | 18 |
| `Ik07_n7_g7,5,1,3,10,11` | 7 | 75 | 33 |
| `Ik08_n8_g5,2,2,7,9,8,1` | 8 | 13 | 66 |
| `Ik09_n9_g11,3,7,7,5,1,5,3` | 9 | 16 | 34 |
| `Ik10_n10_g8,5,9,6,6,8,9,9,1` | 10 | 78 | 21 |
| `Ik11_n11_g3,4,7,8,6,10,4,5,9,4` | 11 | 46 | 47 |
| `Ik12_n12_g2,10,2,3,5,7,8,1,4,11,11` | 12 | 49 | 54 |

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py --pin dfrtp_2_24
```
