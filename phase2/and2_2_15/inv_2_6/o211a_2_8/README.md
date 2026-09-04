# `o211a_2_8` (under A-arm `inv_2_6`)

Parent: [`../README.md`](../README.md) — depth-5 cut on `a31o_2_11` fan-in; drives `a22o_2_1.B1`.

```text
a22o_2_1.B1  ←  o211a_2_8.X
o211a_2_8.X  =  (A1 ∨ A2) ∧ B1 ∧ C1

A1 = inv_2_8__A          # = mux2_1_7.S
A2 = mux2_1_7__A0        # = ¬(or2_2_7__A ∧ I)
B1 = or2_2_7__X          # = or2_2_7__A ∨ I  (= mux.A1)
C1 = inv_2_7__A          # FA stub (and2b.Y)
```

Shares the mux / or2 / inv_2_8 neighborhood with the fail-trip inhibit path (`mux2_1_7` → a31o.A3).

## Figure

- [`o211a_2_8__X_fanin_depth5.png`](o211a_2_8__X_fanin_depth5.png)

## Timelines

- Pins + NO-I stubs: [`timelines/o211a_pins.md`](timelines/o211a_pins.md)
- 2-I / 3-I spacing (first 14 cyc): [`timelines/I2_I3_spacing.md`](timelines/I2_I3_spacing.md)
- 2-I / 3-I from cyc 30: [`timelines/I2_I3_from30.md`](timelines/I2_I3_from30.md)
- 2-I / 3-I from cyc 75: [`timelines/I2_I3_from75.md`](timelines/I2_I3_from75.md)
- 4 equal-spaced I · Δ=1..11: [`timelines/I4eq_delta.md`](timelines/I4eq_delta.md)
- Exactly 2 I per period-11 window: [`timelines/I2_every_window.md`](timelines/I2_every_window.md)
- k=2..5 + all11 (first 11 cyc): [`timelines/Ik_all11.md`](timelines/Ik_all11.md)

## Pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A1` | `inv_2_8__A` | inv_2_8.A / dfrtp_2_29.Q (= mux2_1_7.S) | →I | 44 | `I`, `enable` |
| `A2` | `mux2_1_7__A0` | mux2_1_7.A0 = nand2_2_25.Y = ¬(or2_2_7__A ∧ I) | →I | 44 | `I`, `enable` |
| `B1` | `or2_2_7__X` | or2_2_7.X = or2_2_7__A ∨ I (= mux2_1_7.A1) | →I | 44 | `I`, `enable` |
| `C1` | `inv_2_7__A` | inv_2_7.A / and2b_2_11.Y (FA stub) | stub | 33 | `enable` |

Cone: **44** n / **11** ff · `I, enable`

## Stub pins (no I)

- `C1` ← `inv_2_7__A`

## Related

- Parent a31o fan-in: [`../a31o_2_11__X_fanin_depth5.png`](../a31o_2_11__X_fanin_depth5.png)
- Mux dependence: [`../mux2_1_7_a31o_dependence.png`](../mux2_1_7_a31o_dependence.png)
- Phase-3 fail-trip rule: [`../../../../phase3/and2_2_15/rules/a31o_2_11_fail_trip_mux_gate.txt`](../../../../phase3/and2_2_15/rules/a31o_2_11_fail_trip_mux_gate.txt)

```bash
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_I3_spacing_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_I3_from30_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_I3_from75_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I4eq_delta_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_every_window_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_Ik_all11_timeline.py
```
