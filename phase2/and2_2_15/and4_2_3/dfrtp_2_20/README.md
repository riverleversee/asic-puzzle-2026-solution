# `dfrtp_2_20` — and4_2_3 pin `C`

Parent: [`../README.md`](../README.md).

Pin **C** of `and4_2_3` is `dfrtp_2_20.Q`.
Next-state is `xnor2_2_11` (compare / hold vs `nand2` side).

```text
and4_2_3.C  ←  and4_2_3__C
xnor2_2_11  =  ¬(A ⊕ B)
sink: dfrtp_2_20.D → and4_2_3.C
```

## Figure

- [`xnor2_2_11__Y_fanin_depth5.png`](xnor2_2_11__Y_fanin_depth5.png)

## `xnor2_2_11` pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A` | `and4_2_3__C` | Q feedback (and4_2_3.C / dfrtp_2_20.Q) | →I | 51 | `I`, `enable` |
| `B` | `xnor2_2_11__B` | xnor2_2_11.B ← nand2_2_24.Y | →I | 49 | `I`, `enable` |

Cone (`xnor2_2_11__Y`): **51** n / **14** ff · `I, enable`

Behind Q/`and4_2_3__C`: **51** n / **13** ff

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
- Random-spaced Ik (highlight and4.C): [`timelines/Ik_random_spacing.md`](timelines/Ik_random_spacing.md)
- Active watches (≥7 non-static): [`timelines/active_watches.md`](timelines/active_watches.md)
- I2 every window · random spacing (same offs all windows): [`timelines/I2win_rand_spacing.md`](timelines/I2win_rand_spacing.md)
- I2 every window · **per-window** random offs: [`timelines/I2win_perwindow_rand.md`](timelines/I2win_perwindow_rand.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_I2win_perwindow_rand_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_I2win_rand_spacing_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_active_watches_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_Ik_random_spacing_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py --pin dfrtp_2_20
```
## Related

- Parent and4 fan-in: [`../and4_2_3__X_fanin_depth5.png`](../and4_2_3__X_fanin_depth5.png)
- Sibling pin folders: [`../dfrtp_2_24/`](../dfrtp_2_24/), [`../dfrtp_2_25/`](../dfrtp_2_25/), [`../nor3_2_2/`](../nor3_2_2/)

```bash
python3 phase2/and2_2_15/and4_2_3/dfrtp_2_20/run.py
```
