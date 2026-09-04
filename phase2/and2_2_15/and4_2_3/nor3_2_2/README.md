# `nor3_2_2` — and4_2_3 pin `D`

Parent: [`../README.md`](../README.md).

Pin **D** of `and4_2_3` is `nor3_2_2.Y` (combinational; not a single flop).
A/B are themselves flop Qs (`dfrtp_2_21`, `dfrtp_2_19`); C is `or3_2_8`.

```text
and4_2_3.D  ←  nor3_2_2__Y
nor3_2_2  =  ¬(A ∨ B ∨ C)
sink: and4_2_3.D
```

## Figure

- [`nor3_2_2__Y_fanin_depth5.png`](nor3_2_2__Y_fanin_depth5.png)

## `nor3_2_2` pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A` | `nor3_2_2__A` | nor3_2_2.A ← dfrtp_2_21.Q | →I | 55 | `I`, `enable` |
| `B` | `nor3_2_2__B` | nor3_2_2.B ← dfrtp_2_19.Q | →I | 60 | `I`, `enable` |
| `C` | `or3_2_8__X` | or3_2_8.X | →I | 63 | `I`, `enable` |

Cone (`nor3_2_2__Y`): **64** n / **17** ff · `I, enable`

Behind Q/`nor3_2_2__Y`: **64** n / **17** ff

## Sub-expand

- [`or3_2_8_B/`](or3_2_8_B/) — `or3_2_8.B` = `dfrtp_2_26.Q` (D ← `o21a_2_11`); watches use **1-hop-to-I** pin rule

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
- Random-spaced Ik (highlight and4.D): [`timelines/Ik_random_spacing.md`](timelines/Ik_random_spacing.md)
- Active watches (≥7 non-static): [`timelines/active_watches.md`](timelines/active_watches.md)
- I2 every window · random spacing (same offs all windows): [`timelines/I2win_rand_spacing.md`](timelines/I2win_rand_spacing.md)
- I2 every window · **per-window** random offs: [`timelines/I2win_perwindow_rand.md`](timelines/I2win_perwindow_rand.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py --pin nor3_2_2
```
## Related

- Parent and4 fan-in: [`../and4_2_3__X_fanin_depth5.png`](../and4_2_3__X_fanin_depth5.png)
- Sibling pin folders: [`../dfrtp_2_24/`](../dfrtp_2_24/), [`../dfrtp_2_25/`](../dfrtp_2_25/), [`../dfrtp_2_20/`](../dfrtp_2_20/)

```bash
python3 phase2/and2_2_15/and4_2_3/nor3_2_2/run.py
```
