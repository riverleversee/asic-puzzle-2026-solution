# `dfrtp_2_24` — and4_2_3 pin `A`

Parent: [`../README.md`](../README.md).

Pin **A** of `and4_2_3` is `dfrtp_2_24.Q`.
Next-state is `a32o_2_2` (AO32 sticky hold with I-gated set term).

```text
and4_2_3.A  ←  and4_2_3__A
a32o_2_2  =  (A1 ∧ A2 ∧ A3) ∨ (B1 ∧ B2)
sink: dfrtp_2_24.D → and4_2_3.A
```

## Figure

- [`a32o_2_2__X_fanin_depth5.png`](a32o_2_2__X_fanin_depth5.png)

## `a32o_2_2` pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A1` | `I` | primary I | primary | 0 | `I` |
| `A2` | `inv_2_7__A` | inv_2_7.A / and2b_2_11.Y (FA stub) | stub | 33 | `enable` |
| `A3` | `and3_2_10__B` | and3_2_10.B | →I | 41 | `I`, `enable` |
| `B1` | `inv_2_10__Y` | inv_2_10.Y | →I | 38 | `I`, `enable` |
| `B2` | `and4_2_3__A` | sticky Q feedback (and4_2_3.A / dfrtp_2_24.Q) | →I | 41 | `I`, `enable` |

Cone (`a32o_2_2__X`): **41** n / **11** ff · `I, enable`

Behind Q/`and4_2_3__A`: **41** n / **10** ff

## Stub pins (no I)

- `A2` ← `inv_2_7__A`

## Rule

- [`../../../phase3/and2_2_15/rules/and4_2_3_two_per_cycle.txt`](../../../phase3/and2_2_15/rules/and4_2_3_two_per_cycle.txt) — **2 `I=1` per period-11 cycle** satisfies `and4_2_3` (likely a total-ones budget); sim a few cycles past 121.

## Timelines (I-pattern suite)

Same patterns as `inv_2_6` / `o211a_2_8` for pattern ID.

- [`timelines/I1_probe_timeline.md`](timelines/I1_probe_timeline.md)
- [`timelines/I2_I3_spacing.md`](timelines/I2_I3_spacing.md)
- [`timelines/I2_I3_from30.md`](timelines/I2_I3_from30.md)
- [`timelines/I2_I3_from75.md`](timelines/I2_I3_from75.md)
- [`timelines/I4eq_delta.md`](timelines/I4eq_delta.md)
- [`timelines/I2_every_window.md`](timelines/I2_every_window.md)
- [`timelines/Ik_all11.md`](timelines/Ik_all11.md)
- Random-spaced Ik (highlight and4.A): [`timelines/Ik_random_spacing.md`](timelines/Ik_random_spacing.md)
- Active watches (≥7 non-static): [`timelines/active_watches.md`](timelines/active_watches.md)
- I2 every window · random spacing (same offs all windows): [`timelines/I2win_rand_spacing.md`](timelines/I2win_rand_spacing.md)
- I2 every window · **per-window** random offs: [`timelines/I2win_perwindow_rand.md`](timelines/I2win_perwindow_rand.md)
- I2-per-window **pass report** (extended sim): [`reports/I2win_2per_extended.md`](reports/I2win_2per_extended.md)

```bash
python3 phase2/and2_2_15/and4_2_3/dfrtp_2_24/run_I2win_extended_report.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py --pin dfrtp_2_24
```
## Related

- Parent and4 fan-in: [`../and4_2_3__X_fanin_depth5.png`](../and4_2_3__X_fanin_depth5.png)
- Sibling pin folders: [`../dfrtp_2_25/`](../dfrtp_2_25/), [`../dfrtp_2_20/`](../dfrtp_2_20/), [`../nor3_2_2/`](../nor3_2_2/)

```bash
python3 phase2/and2_2_15/and4_2_3/dfrtp_2_24/run.py
```
