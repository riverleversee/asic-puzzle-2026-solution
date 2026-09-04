# I-vs-I comparison tracer

Count gates along each pin’s fan-in that **compare / select between**
two values that both trace to primary `I`.

**Counted**

- `mux2` where **both** `A0` and `A1` reach `I` (S may be enable/FA)
- `xor` / `xnor` where **all** data inputs reach `I`

```text
a221o_2_1.A2 ← mux2_1_12__A1
a221o_2_1.B2 ← mux2_1_12__A0
a221o_2_1.C1 ← a22o_2_2__X

a22o_2_2.A2  ← a22o_2_2__A2   (flop; D ← mux2_1_13)
a22o_2_2.B2  ← a22o_2_2__B2   (flop; D ← mux2_1_11)
a22o_2_2.A1/B1 = or4.X / buf  (stubs — not traced here)
```

## Summary

| Path | cone | mux I-vs-I | xor I-vs-I | total |
|------|-----:|----------:|----------:|------:|
| `a221o.A2` ← `mux2_1_12__A1` | 56 | 10 | 0 | 10 |
| `a221o.B2` ← `mux2_1_12__A0` | 58 | 11 | 0 | 11 |
| `a221o.C1` ← `a22o_2_2__X` | 63 | 12 | 0 | 12 |
| `a221o` ← `a221o_2_1__X` | 66 | 12 | 0 | 12 |
| `a22o.A2` ← `a22o_2_2__A2` | 38 | 1 | 0 | 1 |
| `a22o.B2` ← `a22o_2_2__B2` | 60 | 12 | 0 | 12 |
| `a22o` ← `a22o_2_2__X` | 63 | 12 | 0 | 12 |

# a221o pins

## Path `a221o.A2` ← `mux2_1_12__A1`

Total I-vs-I sites: **10** (10 mux + 0 xor).

### mux2 (A0 & A1 both → I)

| depth | instance | net | A0 | A1 | S | S→I? |
|------:|----------|-----|----|----|---|:----:|
| 1 | `mux2_1_10` | `mux2_1_10__X` | `mux2_1_12__A1` | `mux2_1_8__A0` | `inv_2_7__A` |  |
| 3 | `mux2_1_8` | `mux2_1_8__X` | `mux2_1_8__A0` | `mux2_1_8__A1` | `inv_2_7__A` |  |
| 5 | `mux2_1_14` | `mux2_1_14__X` | `mux2_1_8__A1` | `mux2_1_15__A0` | `inv_2_7__A` |  |
| 7 | `mux2_1_15` | `mux2_1_15__X` | `mux2_1_15__A0` | `mux2_1_16__A0` | `inv_2_7__A` |  |
| 9 | `mux2_1_16` | `mux2_1_16__X` | `mux2_1_16__A0` | `mux2_1_9__A0` | `inv_2_7__A` |  |
| 11 | `mux2_1_9` | `mux2_1_9__X` | `mux2_1_9__A0` | `mux2_1_9__A1` | `inv_2_7__A` |  |
| 13 | `mux2_1_17` | `mux2_1_17__X` | `mux2_1_9__A1` | `mux2_1_19__A0` | `inv_2_7__A` |  |
| 15 | `mux2_1_19` | `mux2_1_19__X` | `mux2_1_19__A0` | `mux2_1_19__A1` | `inv_2_7__A` |  |
| 17 | `mux2_1_18` | `mux2_1_18__X` | `mux2_1_19__A1` | `a22o_2_2__A2` | `inv_2_7__A` |  |
| 19 | `mux2_1_13` | `mux2_1_13__X` | `a22o_2_2__A2` | `I` | `inv_2_7__A` |  |

_(no xor/xnor I-vs-I sites)_

## Path `a221o.B2` ← `mux2_1_12__A0`

Total I-vs-I sites: **11** (11 mux + 0 xor).

### mux2 (A0 & A1 both → I)

| depth | instance | net | A0 | A1 | S | S→I? |
|------:|----------|-----|----|----|---|:----:|
| 1 | `mux2_1_12` | `mux2_1_12__X` | `mux2_1_12__A0` | `mux2_1_12__A1` | `inv_2_7__A` |  |
| 3 | `mux2_1_10` | `mux2_1_10__X` | `mux2_1_12__A1` | `mux2_1_8__A0` | `inv_2_7__A` |  |
| 5 | `mux2_1_8` | `mux2_1_8__X` | `mux2_1_8__A0` | `mux2_1_8__A1` | `inv_2_7__A` |  |
| 7 | `mux2_1_14` | `mux2_1_14__X` | `mux2_1_8__A1` | `mux2_1_15__A0` | `inv_2_7__A` |  |
| 9 | `mux2_1_15` | `mux2_1_15__X` | `mux2_1_15__A0` | `mux2_1_16__A0` | `inv_2_7__A` |  |
| 11 | `mux2_1_16` | `mux2_1_16__X` | `mux2_1_16__A0` | `mux2_1_9__A0` | `inv_2_7__A` |  |
| 13 | `mux2_1_9` | `mux2_1_9__X` | `mux2_1_9__A0` | `mux2_1_9__A1` | `inv_2_7__A` |  |
| 15 | `mux2_1_17` | `mux2_1_17__X` | `mux2_1_9__A1` | `mux2_1_19__A0` | `inv_2_7__A` |  |
| 17 | `mux2_1_19` | `mux2_1_19__X` | `mux2_1_19__A0` | `mux2_1_19__A1` | `inv_2_7__A` |  |
| 19 | `mux2_1_18` | `mux2_1_18__X` | `mux2_1_19__A1` | `a22o_2_2__A2` | `inv_2_7__A` |  |
| 21 | `mux2_1_13` | `mux2_1_13__X` | `a22o_2_2__A2` | `I` | `inv_2_7__A` |  |

_(no xor/xnor I-vs-I sites)_

## Path `a221o.C1` ← `a22o_2_2__X`

Total I-vs-I sites: **12** (12 mux + 0 xor).

### mux2 (A0 & A1 both → I)

| depth | instance | net | A0 | A1 | S | S→I? |
|------:|----------|-----|----|----|---|:----:|
| 2 | `mux2_1_11` | `mux2_1_11__X` | `a22o_2_2__B2` | `mux2_1_12__A0` | `inv_2_7__A` |  |
| 2 | `mux2_1_13` | `mux2_1_13__X` | `a22o_2_2__A2` | `I` | `inv_2_7__A` |  |
| 4 | `mux2_1_12` | `mux2_1_12__X` | `mux2_1_12__A0` | `mux2_1_12__A1` | `inv_2_7__A` |  |
| 6 | `mux2_1_10` | `mux2_1_10__X` | `mux2_1_12__A1` | `mux2_1_8__A0` | `inv_2_7__A` |  |
| 8 | `mux2_1_8` | `mux2_1_8__X` | `mux2_1_8__A0` | `mux2_1_8__A1` | `inv_2_7__A` |  |
| 10 | `mux2_1_14` | `mux2_1_14__X` | `mux2_1_8__A1` | `mux2_1_15__A0` | `inv_2_7__A` |  |
| 12 | `mux2_1_15` | `mux2_1_15__X` | `mux2_1_15__A0` | `mux2_1_16__A0` | `inv_2_7__A` |  |
| 14 | `mux2_1_16` | `mux2_1_16__X` | `mux2_1_16__A0` | `mux2_1_9__A0` | `inv_2_7__A` |  |
| 16 | `mux2_1_9` | `mux2_1_9__X` | `mux2_1_9__A0` | `mux2_1_9__A1` | `inv_2_7__A` |  |
| 18 | `mux2_1_17` | `mux2_1_17__X` | `mux2_1_9__A1` | `mux2_1_19__A0` | `inv_2_7__A` |  |
| 20 | `mux2_1_19` | `mux2_1_19__X` | `mux2_1_19__A0` | `mux2_1_19__A1` | `inv_2_7__A` |  |
| 22 | `mux2_1_18` | `mux2_1_18__X` | `mux2_1_19__A1` | `a22o_2_2__A2` | `inv_2_7__A` |  |

_(no xor/xnor I-vs-I sites)_


# a22o_2_2 pins (A2 / B2)

## Path `a22o.A2` ← `a22o_2_2__A2`

Total I-vs-I sites: **1** (1 mux + 0 xor).

### mux2 (A0 & A1 both → I)

| depth | instance | net | A0 | A1 | S | S→I? |
|------:|----------|-----|----|----|---|:----:|
| 1 | `mux2_1_13` | `mux2_1_13__X` | `a22o_2_2__A2` | `I` | `inv_2_7__A` |  |

_(no xor/xnor I-vs-I sites)_

## Path `a22o.B2` ← `a22o_2_2__B2`

Total I-vs-I sites: **12** (12 mux + 0 xor).

### mux2 (A0 & A1 both → I)

| depth | instance | net | A0 | A1 | S | S→I? |
|------:|----------|-----|----|----|---|:----:|
| 1 | `mux2_1_11` | `mux2_1_11__X` | `a22o_2_2__B2` | `mux2_1_12__A0` | `inv_2_7__A` |  |
| 3 | `mux2_1_12` | `mux2_1_12__X` | `mux2_1_12__A0` | `mux2_1_12__A1` | `inv_2_7__A` |  |
| 5 | `mux2_1_10` | `mux2_1_10__X` | `mux2_1_12__A1` | `mux2_1_8__A0` | `inv_2_7__A` |  |
| 7 | `mux2_1_8` | `mux2_1_8__X` | `mux2_1_8__A0` | `mux2_1_8__A1` | `inv_2_7__A` |  |
| 9 | `mux2_1_14` | `mux2_1_14__X` | `mux2_1_8__A1` | `mux2_1_15__A0` | `inv_2_7__A` |  |
| 11 | `mux2_1_15` | `mux2_1_15__X` | `mux2_1_15__A0` | `mux2_1_16__A0` | `inv_2_7__A` |  |
| 13 | `mux2_1_16` | `mux2_1_16__X` | `mux2_1_16__A0` | `mux2_1_9__A0` | `inv_2_7__A` |  |
| 15 | `mux2_1_9` | `mux2_1_9__X` | `mux2_1_9__A0` | `mux2_1_9__A1` | `inv_2_7__A` |  |
| 17 | `mux2_1_17` | `mux2_1_17__X` | `mux2_1_9__A1` | `mux2_1_19__A0` | `inv_2_7__A` |  |
| 19 | `mux2_1_19` | `mux2_1_19__X` | `mux2_1_19__A0` | `mux2_1_19__A1` | `inv_2_7__A` |  |
| 21 | `mux2_1_18` | `mux2_1_18__X` | `mux2_1_19__A1` | `a22o_2_2__A2` | `inv_2_7__A` |  |
| 23 | `mux2_1_13` | `mux2_1_13__X` | `a22o_2_2__A2` | `I` | `inv_2_7__A` |  |

_(no xor/xnor I-vs-I sites)_

## JSON

[`I_comparisons.json`](I_comparisons.json)

Regenerate:
```bash
python3 phase3/a221o_set/trace_I_comparisons.py
```
