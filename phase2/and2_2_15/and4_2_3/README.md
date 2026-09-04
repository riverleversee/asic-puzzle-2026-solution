# B-arm `and4_2_3` (phase 2)

Join: [`../README.md`](../README.md) — `and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X`.

## Figure

- [`and4_2_3__X_fanin_depth5.png`](and4_2_3__X_fanin_depth5.png)

## Pins

| Pin | Net | Role | kind | nodes | primaries | folder |
|-----|-----|------|:----:|------:|-----------|--------|
| `A` | `and4_2_3__A` | dfrtp_2_24.Q | →I | 41 | `I`, `enable` | [`dfrtp_2_24/`](dfrtp_2_24/) |
| `B` | `and4_2_3__B` | dfrtp_2_25.Q | →I | 45 | `I`, `enable` | [`dfrtp_2_25/`](dfrtp_2_25/) |
| `C` | `and4_2_3__C` | dfrtp_2_20.Q | →I | 51 | `I`, `enable` | [`dfrtp_2_20/`](dfrtp_2_20/) |
| `D` | `nor3_2_2__Y` | nor3_2_2.Y | →I | 64 | `I`, `enable` | [`nor3_2_2/`](nor3_2_2/) |

Cone: **65** n / **17** ff · `I, enable`

## Sub-expand (one folder per and4 input)

Each input figured separately — same only-I depth-5 expansion as `inv_2_6/o211a_2_8/`.

| Pin | Folder | Expand root | n / ff |
|-----|--------|-------------|-------:|
| `A` | [`dfrtp_2_24/`](dfrtp_2_24/) | `a32o_2_2` | 41 / 11 |
| `B` | [`dfrtp_2_25/`](dfrtp_2_25/) | `and2b_2_10` | 45 / 12 |
| `C` | [`dfrtp_2_20/`](dfrtp_2_20/) | `xnor2_2_11` | 51 / 14 |
| `D` | [`nor3_2_2/`](nor3_2_2/) | `nor3_2_2` | 64 / 17 |

## Timelines / structures

- Inputs timeline: [`timelines/and4_inputs.md`](timelines/and4_inputs.md)
- I-pattern suites (per pin): `dfrtp_2_24|25|20|nor3_2_2/timelines/` (I1, I2_I3 spacing/from30/from75, I4eq, I2win, Ik_all11)
- Block structures: [`structures/`](structures/)

```bash
python3 phase2/and2_2_15/run.py
python3 phase2/and2_2_15/and4_2_3/expand_pin_subs.py
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_recognize_structures.py
```
