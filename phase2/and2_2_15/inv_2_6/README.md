# A-arm `inv_2_6` / sticky `a31o_2_11` (phase 2)

Join: [`../README.md`](../README.md) — `and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X`.

```text
inv_2_6.A    ←  dfrtp_2_28.Q
dfrtp_2_28.D ←  a31o_2_11.X
a31o_2_11.X  =  (A1 ∧ A2 ∧ A3) ∨ B1
```

## Figure

- [`a31o_2_11__X_fanin_depth5.png`](a31o_2_11__X_fanin_depth5.png) — mux edges labeled `S`/`A0`/`A1`; box shows `X=S?A1:A0`
- Mux → a31o dependence (inhibit): [`mux2_1_7_a31o_dependence.png`](mux2_1_7_a31o_dependence.png)
  (also [`../../../phase3/and2_2_15/`](../../../phase3/and2_2_15/))

## Phase 3 note

Fail latch trips at end of each 11-bit FA cycle (I-independent stubs). Hold `mux2_1_7.X=0` to block the trip:
[`../../../phase3/and2_2_15/rules/a31o_2_11_fail_trip_mux_gate.txt`](../../../phase3/and2_2_15/rules/a31o_2_11_fail_trip_mux_gate.txt)

## a31o_2_11 pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A1` | `inv_2_9__A` | inv_2_9.A (FA-side) | stub | 33 | `enable` |
| `A2` | `inv_2_7__A` | inv_2_7.A / and2b.Y (FA-side) | stub | 33 | `enable` |
| `A3` | `mux2_1_7__X` | mux2_1_7.X | →I | 45 | `I`, `enable` |
| `B1` | `inv_2_6__A` | sticky feedback (inv_2_6.A / dfrtp_2_28.Q) | →I | 47 | `I`, `enable` |

- `a31o_2_11.X`: **47** n / **12** ff
- `inv_2_6.A`: **47** n / **11** ff
- `inv_2_6.Y`: **48** n / **12** ff

## Stub pins (no I)

- `A1` ← `inv_2_9__A`
- `A2` ← `inv_2_7__A`

## Sub-expand

- [`o211a_2_8/`](o211a_2_8/) — depth-5 cut (`a22o_2_1.B1`); shares mux/or2/inv_2_8 neighborhood

## Timelines / structures

- I-indep stubs: [`timelines/noI_stub_timeline.md`](timelines/noI_stub_timeline.md)
- I=1 probes: [`timelines/I1_probe_timeline.md`](timelines/I1_probe_timeline.md)
- 2-I / 3-I spacing (first 14 cyc): [`timelines/I2_I3_spacing.md`](timelines/I2_I3_spacing.md)
- 2-I / 3-I from cyc 30: [`timelines/I2_I3_from30.md`](timelines/I2_I3_from30.md)
- 2-I / 3-I from cyc 75: [`timelines/I2_I3_from75.md`](timelines/I2_I3_from75.md)
- mux S/A0/A1/X · 1/2/3 I from cyc 2: [`timelines/mux_pins_I123_from2.md`](timelines/mux_pins_I123_from2.md)
- 4 equal-spaced I · Δ=1..11: [`timelines/I4eq_delta.md`](timelines/I4eq_delta.md)
- Exactly 2 I per period-11 window: [`timelines/I2_every_window.md`](timelines/I2_every_window.md)
- k=2..5 + all11 (first 11 cyc): [`timelines/Ik_all11.md`](timelines/Ik_all11.md)
- Block structures: [`structures/`](structures/)

```bash
python3 phase2/and2_2_15/run.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run.py
python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I2_I3_spacing_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I2_I3_from30_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I2_I3_from75_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_mux_pins_I123_from2_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I4eq_delta_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I2_every_window_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I4eq_delta_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_every_window_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_Ik_all11_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_I3_spacing_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_I3_from30_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_I2_I3_from75_timeline.py
python3 phase2/and2_2_15/inv_2_6/o211a_2_8/run_Ik_all11_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_recognize_structures.py
```
