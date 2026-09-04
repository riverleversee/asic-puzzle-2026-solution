# `dfrtp_2_25` — and4_2_3 pin `B`

Parent: [`../README.md`](../README.md).

Pin **B** of `and4_2_3` is `dfrtp_2_25.Q`.
Next-state net `dfrtp_2_25__D` is driven by `and2b_2_10`.

```text
and4_2_3.B  ←  and4_2_3__B
and2b_2_10  =  ¬A_N ∧ B
sink: dfrtp_2_25.D → and4_2_3.B
```

## Figure

- [`and2b_2_10__X_fanin_depth5.png`](and2b_2_10__X_fanin_depth5.png)

## `and2b_2_10` pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A_N` | `and3_2_11__X` | and3_2_11.X (active-low AND input) | →I | 45 | `I`, `enable` |
| `B` | `a21o_2_10__X` | a21o_2_10.X | →I | 45 | `I`, `enable` |

Cone (`dfrtp_2_25__D`): **45** n / **12** ff · `I, enable`

Behind Q/`and4_2_3__B`: **45** n / **11** ff

## Stub pins (no I)

- (none)

## Timelines (I-pattern suite)

Same patterns as `inv_2_6` / `o211a_2_8` for pattern ID.

- [`timelines/I1_probe_timeline.md`](timelines/I1_probe_timeline.md)
- [`timelines/I2_I3_spacing.md`](timelines/I2_I3_spacing.md)
- [`timelines/I2_I3_from30.md`](timelines/I2_I3_from30.md)
- [`timelines/I2_I3_from75.md`](timelines/I2_I3_from75.md)
- [`timelines/I4eq_delta.md`](timelines/I4eq_delta.md)
- [`timelines/I2_every_window.md`](timelines/I2_every_window.md)
- [`timelines/Ik_all11.md`](timelines/Ik_all11.md)
- Random-spaced Ik (highlight and4.B): [`timelines/Ik_random_spacing.md`](timelines/Ik_random_spacing.md)
- Active watches (≥7 non-static): [`timelines/active_watches.md`](timelines/active_watches.md)
- I2 every window · random spacing (same offs all windows): [`timelines/I2win_rand_spacing.md`](timelines/I2win_rand_spacing.md)
- I2 every window · **per-window** random offs: [`timelines/I2win_perwindow_rand.md`](timelines/I2win_perwindow_rand.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py --pin dfrtp_2_25
```
## Related

- Parent and4 fan-in: [`../and4_2_3__X_fanin_depth5.png`](../and4_2_3__X_fanin_depth5.png)
- Sibling pin folders: [`../dfrtp_2_24/`](../dfrtp_2_24/), [`../dfrtp_2_20/`](../dfrtp_2_20/), [`../nor3_2_2/`](../nor3_2_2/)

```bash
python3 phase2/and2_2_15/and4_2_3/dfrtp_2_25/run.py
```
