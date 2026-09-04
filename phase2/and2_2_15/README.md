# Success entry `and2_2_15` — join (phase 2)

Thin AND of two mostly independent arms. Detail lives in the arm folders.

```text
a32o_2_4.A2  =  and2_2_15.X
and2_2_15.X  =  inv_2_6.Y ∧ and4_2_3.X
              └─ A-arm: inv_2_6/ ─┘   └─ B-arm: and4_2_3/ ─┘
```

**Testing → phase 3 later.**

## Arms

| Arm | Folder | Root |
|-----|--------|------|
| A (sticky) | [`inv_2_6/`](inv_2_6/) | `inv_2_6.Y` ← `a31o_2_11` |
| B (and4) | [`and4_2_3/`](and4_2_3/) | `and4_2_3.X` |

## Join figure

- [`and2_2_15__X_fanin_depth4.png`](and2_2_15__X_fanin_depth4.png)

## Join pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A` | `inv_2_6__Y` | inv_2_6.Y ← sticky a31o_2_11 / dfrtp_2_28 | →I | 48 | `I`, `enable` |
| `B` | `and4_2_3__X` | and4_2_3.X | →I | 65 | `I`, `enable` |

Full cone: **81** n / **20** ff · `I, enable`

## Size check (A vs B)

- [`pre_and4_region.md`](pre_and4_region.md)

Sibling: SET path [`../a221o_behind_inv23/`](../a221o_behind_inv23/). `and4b_2_3` not expanded here.

```bash
python3 phase2/and2_2_15/run.py
python3 phase2/and2_2_15/run_count_pre_and4.py
python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_recognize_structures.py
python3 phase2/and2_2_15/inv_2_6/run_recognize_structures.py
```
