# `dfrtp_2_24` — I2-per-cycle pass report (extended sim)

and4.A · `dfrtp_2_24` · `a32o_2_2`

Rule: [`../../../../phase3/and2_2_15/rules/and4_2_3_two_per_cycle.txt`](../../../../phase3/and2_2_15/rules/and4_2_3_two_per_cycle.txt) — **2 `I=1` per period-11 cycle** satisfies `and4_2_3` (likely total ones); always sim a few cycles past 121.

## Setup

- Cycles from **entry 0**: `C_k = [11k .. 11k+10]`, `k=0..10` (121 I cycles).
- Exactly **2** `I=1` per cycle.
- Sim length **125** = `121` + **4** extra (`I=0`).

Pass = `and4.X` high on at least one cycle.

**Result: 213/213 pass** — all pass.

CSV: [`I2win_2per_extended.csv`](I2win_2per_extended.csv)

Seed `20260904`.

## Exhaustive fixed pairs `C(11,2)=55` · same offs every window

Modes **55** · pass **55** · fail **0** (100.0%).

| has I@120? | n | pass | fail |
|------------|--:|-----:|-----:|
| yes | 10 | 10 | 0 |
| no | 45 | 45 | 0 |

**All passed.** `and4.X` n ∈ [`4`, `13`].

## Per-window random ×48

Modes **48** · pass **48** · fail **0** (100.0%).

| has I@120? | n | pass | fail |
|------------|--:|-----:|-----:|
| yes | 4 | 4 | 0 |
| no | 44 | 44 | 0 |

**All passed.** `and4.X` n ∈ [`4`, `13`].

## Entry 0 on first+last windows only · mid `(1,3)` · sf/sl `1..10`

Modes **100** · pass **100** · fail **0** (100.0%).

| has I@120? | n | pass | fail |
|------------|--:|-----:|-----:|
| yes | 10 | 10 | 0 |
| no | 90 | 90 | 0 |

**All passed.** `and4.X` n ∈ [`4`, `13`].

## Force bit 10 every window (incl. last / cyc 120)

Modes **10** · pass **10** · fail **0** (100.0%).

| has I@120? | n | pass | fail |
|------------|--:|-----:|-----:|
| yes | 10 | 10 | 0 |
| no | 0 | 0 | 0 |

**All passed.** `and4.X` n ∈ [`4`, `4`].

| mode | offs | and4.X n | and4.X first | and4.X last | pass |
|------|------|---------:|-------------:|------------:|:----:|
| `force10_c0` | `0,10` | 4 | 121 | 124 | ✓ |
| `force10_c1` | `1,10` | 4 | 121 | 124 | ✓ |
| `force10_c2` | `2,10` | 4 | 121 | 124 | ✓ |
| `force10_c3` | `3,10` | 4 | 121 | 124 | ✓ |
| `force10_c4` | `4,10` | 4 | 121 | 124 | ✓ |
| `force10_c5` | `5,10` | 4 | 121 | 124 | ✓ |
| `force10_c6` | `6,10` | 4 | 121 | 124 | ✓ |
| `force10_c7` | `7,10` | 4 | 121 | 124 | ✓ |
| `force10_c8` | `8,10` | 4 | 121 | 124 | ✓ |
| `force10_c9` | `9,10` | 4 | 121 | 124 | ✓ |

## Notes

- Standard timeline plots under `timelines/` were **not** regenerated.
- Rule file: two-per-cycle is sufficient; placement (incl. bit 10 / `I@120`) OK once horizon includes a few extra cycles.

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/dfrtp_2_24/run_I2win_extended_report.py
```
