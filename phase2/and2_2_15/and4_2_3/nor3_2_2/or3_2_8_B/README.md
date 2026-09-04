# `or3_2_8_B` — under `nor3_2_2` (and4.D)

Parent: [`../README.md`](../README.md).

Pin **B** of `or3_2_8` feeds `nor3_2_2.C` (and4.D path).
It is `dfrtp_2_26.Q`; next-state is `o21a_2_11`.

```text
nor3_2_2.Y  =  ¬(A ∨ B ∨ C)
C           ←  or3_2_8.X
or3_2_8.B   ←  dfrtp_2_26.Q
dfrtp_2_26.D ←  o21a_2_11.X = (A1 ∨ A2) ∧ B1
```

## Figure

- [`o21a_2_11__X_fanin_depth5.png`](o21a_2_11__X_fanin_depth5.png)

## `o21a_2_11` pins

| Pin | Net | Role | kind | nodes | primaries |
|-----|-----|------|:----:|------:|-----------|
| `A1` | `or3_2_8__B` | o21a.A1 | →I | 49 | `I`, `enable` |
| `B1` | `xnor2_2_11__B` | o21a.B1 ← xnor2_2_11.B | →I | 49 | `I`, `enable` |
| `A2` | `and3_2_11__X` | o21a.A2 ← and3_2_11.X | →I | 45 | `I`, `enable` |

Cone (`o21a_2_11__X`): **49** n / **13** ff · `I, enable`

Behind Q/`or3_2_8__B`: **49** n / **12** ff

## Pin watch rule (1-hop to I)

No watches more than **1 node back** from something that reaches `I`.
If a net does **not** reach I, it may only be pinned when the gate it
**feeds into** (toward the root) **does** reach I.

Shared helper: [`../../pin_i_hop_rule.py`](../../pin_i_hop_rule.py)

Allowed watches (**18**):

| net | why | parent |
|-----|-----|--------|
| `I` | reaches_I | `inv_2_10__A` |
| `a21o_2_10__X` | reaches_I | `dfrtp_2_25__D` |
| `a32o_2_2__X` | reaches_I | `and4_2_3__A` |
| `and3_2_10__B` | reaches_I | `a32o_2_2__X` |
| `and3_2_11__X` | reaches_I | `o21a_2_11__X` |
| `and4_2_3__A` | reaches_I | `and3_2_11__X` |
| `and4_2_3__B` | reaches_I | `and3_2_11__X` |
| `and4_2_4__D` | reaches_I | `xnor2_2_11__B` |
| `dfrtp_2_25__D` | reaches_I | `and4_2_3__B` |
| `inv_2_10__A` | reaches_I | `xnor2_2_11__B` |
| `inv_2_10__Y` | reaches_I | `a32o_2_2__X` |
| `inv_2_7__A` | feeds_I_parent | `inv_2_10__A` |
| `nor2_2_30__B` | reaches_I | `nor2_2_30__Y` |
| `nor2_2_30__Y` | reaches_I | `or3_2_8__A` |
| `o21a_2_11__X` | reaches_I | — |
| `or3_2_8__A` | reaches_I | `inv_2_10__A` |
| `or3_2_8__B` | reaches_I | `o21a_2_11__X` |
| `xnor2_2_11__B` | reaches_I | `o21a_2_11__X` |

Rejected (**3**):

| net | why | parent |
|-----|-----|--------|
| `a31o_2_13__X` | deeper_non_I | `or2_2_11__A` |
| `enable` | deeper_non_I | `inv_2_7__A` |
| `or2_2_11__A` | deeper_non_I | `inv_2_7__A` |

## Stub pins (gate pins, no I)

- (none)

## Timelines

- [`timelines/`](timelines/) — I tests using **allowed** watches only

## Related

- Parent nor3 fan-in: [`../nor3_2_2__Y_fanin_depth5.png`](../nor3_2_2__Y_fanin_depth5.png)

```bash
python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run.py
python3 phase2/and2_2_15/and4_2_3/nor3_2_2/or3_2_8_B/run_i_tests.py
```
