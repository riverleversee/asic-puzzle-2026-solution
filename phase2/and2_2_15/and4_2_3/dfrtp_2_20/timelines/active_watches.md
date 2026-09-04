# `dfrtp_2_20` — active watches (Ik random spacing)

and4.C · dfrtp_2_20 · xnor2_2_11

Probed **14** nets; plotted **10** that are non-static (target ≥7). Highlight `Q` → **and4.C** always kept.

Figure: [`active_watches.png`](active_watches.png)

CSV (all watches): [`active_watches.csv`](active_watches.csv)

## Watch activity

| lab | title | active? | flips | plotted |
|-----|-------|:-------:|------:|:-------:|
| `Q` | ★ Q → and4.C | no | 0 | ✓ |
| `xnor_Y` | xnor.Y → flop.D | no | 0 |  |
| `xnor_B` | xnor.B | no | 0 |  |
| `and4_4D` | and4_2_4__D | no | 0 |  |
| `inv10_A` | inv_2_10__A | yes | 72 | ✓ |
| `and4_A` | sib and4.A | yes | 42 | ✓ |
| `and4_B` | sib and4.B | yes | 19 | ✓ |
| `or3_A` | or3_2_8__A | yes | 84 | ✓ |
| `or3_B` | or3_2_8__B | yes | 9 | ✓ |
| `o21a` | o21a_2_11__X | yes | 9 | ✓ |
| `a21o` | a21o_2_10__X | yes | 19 | ✓ |
| `and3_11` | and3_2_11__X | yes | 10 | ✓ |
| `nor2_Y` | nor2_2_30__Y | yes | 84 | ✓ |
| `and4_X` | and4.X | no | 0 |  |

## Observe summary (highlight)

| mode | #I | Q n | first |
|------|---:|--------:|------:|
| `all0` | 0 | 0 | — |
| `Ik01_n1_g—` | 1 | 0 | — |
| `Ik02_n2_g7` | 2 | 0 | — |
| `Ik03_n3_g9,4` | 3 | 0 | — |
| `Ik04_n4_g5,11,6` | 4 | 0 | — |
| `Ik05_n5_g5,1,11,3` | 5 | 0 | — |
| `Ik06_n6_g6,5,8,11,1` | 6 | 0 | — |
| `Ik07_n7_g7,5,1,3,10,11` | 7 | 0 | — |
| `Ik08_n8_g5,2,2,7,9,8,1` | 8 | 0 | — |
| `Ik09_n9_g11,3,7,7,5,1,5,3` | 9 | 0 | — |
| `Ik10_n10_g8,5,9,6,6,8,9,9,1` | 10 | 0 | — |
| `Ik11_n11_g3,4,7,8,6,10,4,5,9,4` | 11 | 0 | — |
| `Ik12_n12_g2,10,2,3,5,7,8,1,4,11,11` | 12 | 0 | — |

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py --pin dfrtp_2_20
```
