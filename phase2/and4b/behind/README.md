# and2 + and2b behind `and4b_2_3__X`

**11** `and2` + **17** `and2b` = **28** instances.
Expanded: **`and2b_2_3`** → `and4_2_1__A` ([figure](and2b_2_3_out_and4_2_1__A_fanin_depth5.png)).

## Strong similarity groups

**Number of strong groups: 5**

Criterion: pairwise class-Jaccard ≥ `0.9` and node-ratio ≥ `0.85` (union-find; min size 2).
Covered: **26/28** instances.

| # | Size | I | Families | Mean class J | Mean cell J | Members |
|--:|-----:|---|----------|-------------:|------------:|---------|
| 1 | 11 | hasI | and2+and2b | 0.952 | 0.911 | `and2_2_10`, `and2_2_3`, `and2_2_4`, `and2_2_5`, `and2b_2_1`, `and2b_2_2`, `and2b_2_20`, `and2b_2_21`, `and2b_2_22`, `and2b_2_3`, `and2b_2_4` |
| 2 | 7 | hasI | and2b | 0.981 | 0.934 | `and2b_2_23`, `and2b_2_24`, `and2b_2_25`, `and2b_2_26`, `and2b_2_27`, `and2b_2_28`, `and2b_2_29` |
| 3 | 4 | hasI | and2 | 1.0 | 1.0 | `and2_2_11`, `and2_2_12`, `and2_2_13`, `and2_2_14` |
| 4 | 2 | noI | and2+and2b | 0.971 | 0.786 | `and2_2_1`, `and2b_2_11` |
| 5 | 2 | noI | and2+and2b | 0.927 | 0.848 | `and2_2_0`, `and2b_2_0` |

`hasI` = fan-in reaches primary `I`; `noI` = input-independent.

### Strong group 1 (11× · hasI)

- `and2_2_10` (and2) → `and3_2_5__B` · 109n · 7ff
- `and2_2_3` (and2) → `and4_2_0__A` · 109n · 7ff
- `and2_2_4` (and2) → `and4_2_1__B` · 109n · 7ff
- `and2_2_5` (and2) → `and4_2_0__D` · 109n · 7ff
- `and2b_2_1` (and2b) → `and4_2_0__B` · 112n · 11ff
- `and2b_2_2` (and2b) → `and4_2_0__C` · 112n · 11ff
- `and2b_2_20` (and2b) → `and4_2_1__C` · 112n · 11ff
- `and2b_2_21` (and2b) → `and3_2_5__C` · 112n · 11ff
- `and2b_2_22` (and2b) → `and3_2_5__A` · 112n · 11ff
- `and2b_2_3` (and2b) → `and4_2_1__A` · 112n · 11ff
- `and2b_2_4` (and2b) → `and4_2_1__D` · 112n · 11ff

### Strong group 2 (7× · hasI)

- `and2b_2_23` (and2b) → `and4_2_6__B` · 27n · 8ff
- `and2b_2_24` (and2b) → `and4_2_6__C` · 27n · 8ff
- `and2b_2_25` (and2b) → `and4_2_5__A` · 27n · 8ff
- `and2b_2_26` (and2b) → `and4_2_5__D` · 27n · 8ff
- `and2b_2_27` (and2b) → `and3_2_12__C` · 27n · 8ff
- `and2b_2_28` (and2b) → `and4_2_5__C` · 27n · 8ff
- `and2b_2_29` (and2b) → `and3_2_12__A` · 27n · 8ff

### Strong group 3 (4× · hasI)

- `and2_2_11` (and2) → `and4_2_6__A` · 27n · 7ff
- `and2_2_12` (and2) → `and4_2_6__D` · 27n · 7ff
- `and2_2_13` (and2) → `and4_2_5__B` · 27n · 7ff
- `and2_2_14` (and2) → `and3_2_12__B` · 27n · 7ff

### Strong group 4 (2× · noI)

- `and2_2_1` (and2) → `or2_2_1__A` · 34n · 9ff
- `and2b_2_11` (and2b) → `inv_2_7__A` · 33n · 9ff

### Strong group 5 (2× · noI)

- `and2_2_0` (and2) → `and3_2_0__C` · 40n · 9ff
- `and2b_2_0` (and2b) → `or2_2_0__B` · 37n · 9ff

## Strong pin-pattern clusters (4)

Pin-template clusters whose *within* mean class-Jaccard also clears the strong threshold:

| # | Size | Mean J | Label | Members |
|--:|-----:|-------:|-------|---------|
| 1 | 7 | 0.981 | `and2b: nand4_C × o21a_A1  [shallow(~27n)]` | `and2b_2_23`, `and2b_2_24`, `and2b_2_25`, `and2b_2_26`, `and2b_2_27`, `and2b_2_28`, `and2b_2_29` |
| 2 | 6 | 0.994 | `and2b: nand4_C × o21a_A1  [deep(~110n)]` | `and2b_2_1`, `and2b_2_2`, `and2b_2_20`, `and2b_2_21`, `and2b_2_22`, `and2b_2_4` |
| 3 | 4 | 1.0 | `and2: or4_A × or4_B  [deep(~110n)]` | `and2_2_10`, `and2_2_3`, `and2_2_4`, `and2_2_5` |
| 4 | 4 | 1.0 | `and2: or4_A × or4_B  [shallow(~27n)]` | `and2_2_11`, `and2_2_12`, `and2_2_13`, `and2_2_14` |

## All instances

| Family | Instance | Out net | pin0 | pin1 | nodes | ff |
|--------|----------|---------|------|------|------:|---:|
| `and2` | `and2_2_0` | `and3_2_0__C` | `or2_2_1__X` | `or2_2_0__B` | 40 | 9 |
| `and2` | `and2_2_1` | `or2_2_1__A` | `or4_2_4__A` | `xor2_2_7__A` | 34 | 9 |
| `and2` | `and2_2_10` | `and3_2_5__B` | `or4_2_5__A` | `or4_2_5__B` | 109 | 7 |
| `and2` | `and2_2_11` | `and4_2_6__A` | `or4_2_9__A` | `or4_2_9__B` | 27 | 7 |
| `and2` | `and2_2_12` | `and4_2_6__D` | `or4_2_7__A` | `or4_2_7__B` | 27 | 7 |
| `and2` | `and2_2_13` | `and4_2_5__B` | `or4_2_8__A` | `or4_2_8__B` | 27 | 7 |
| `and2` | `and2_2_14` | `and3_2_12__B` | `or4_2_6__A` | `or4_2_6__B` | 27 | 7 |
| `and2` | `and2_2_2` | `and2_2_2__X` | `and2_2_2__A` | `and3_2_1__C` | 46 | 9 |
| `and2` | `and2_2_3` | `and4_2_0__A` | `or4_2_1__A` | `or4_2_1__B` | 109 | 7 |
| `and2` | `and2_2_4` | `and4_2_1__B` | `or4_2_2__A` | `or4_2_2__B` | 109 | 7 |
| `and2` | `and2_2_5` | `and4_2_0__D` | `or4_2_3__A` | `or4_2_3__B` | 109 | 7 |
| `and2b` | `and2b_2_0` | `or2_2_0__B` | `xor2_2_3__B` | `nor2_2_9__B` | 37 | 9 |
| `and2b` | `and2b_2_1` | `and4_2_0__B` | `nand4_2_0__C` | `o21a_2_4__A1` | 112 | 11 |
| `and2b` | `and2b_2_11` | `inv_2_7__A` | `or2_2_11__A` | `enable` | 33 | 9 |
| `and2b` | `and2b_2_2` | `and4_2_0__C` | `nand4_2_3__C` | `o21a_2_5__A1` | 112 | 11 |
| `and2b` | `and2b_2_20` | `and4_2_1__C` | `nand4_2_5__C` | `o21a_2_30__A1` | 112 | 11 |
| `and2b` | `and2b_2_21` | `and3_2_5__C` | `nand4_2_6__C` | `o21a_2_18__A1` | 112 | 11 |
| `and2b` | `and2b_2_22` | `and3_2_5__A` | `nand4_2_4__C` | `o21a_2_16__A1` | 112 | 11 |
| `and2b` | `and2b_2_23` | `and4_2_6__B` | `nand4_2_7__C` | `o21a_2_19__A1` | 27 | 8 |
| `and2b` | `and2b_2_24` | `and4_2_6__C` | `nand4_2_8__C` | `o21a_2_23__A1` | 27 | 8 |
| `and2b` | `and2b_2_25` | `and4_2_5__A` | `nand4_2_9__C` | `o21a_2_21__A1` | 27 | 8 |
| `and2b` | `and2b_2_26` | `and4_2_5__D` | `nand4_2_10__C` | `o21a_2_28__A1` | 27 | 8 |
| `and2b` | `and2b_2_27` | `and3_2_12__C` | `nand4_2_13__C` | `o21a_2_25__A1` | 27 | 8 |
| `and2b` | `and2b_2_28` | `and4_2_5__C` | `nand4_2_11__C` | `o21a_2_24__A1` | 27 | 8 |
| `and2b` | `and2b_2_29` | `and3_2_12__A` | `nand4_2_12__C` | `o21a_2_27__A1` | 27 | 8 |
| `and2b` | `and2b_2_3` | `and4_2_1__A` | `nand4_2_1__C` | `and2b_2_3__B` | 112 | 11 |
| `and2b` | `and2b_2_4` | `and4_2_1__D` | `nand4_2_2__C` | `o21a_2_8__A1` | 112 | 11 |
| `and2b` | `and2b_2_5` | `xor2_2_6__B` | `and4bb_2_0__X` | `o22ai_2_0__Y` | 43 | 9 |

## All pin-pattern clusters (incl. weak)

### 1. 7× `and2b: nand4_C × o21a_A1  [shallow(~27n)]` **STRONG**

`and2b_2_23`, `and2b_2_24`, `and2b_2_25`, `and2b_2_26`, `and2b_2_27`, `and2b_2_28`, `and2b_2_29`

### 2. 6× `and2b: nand4_C × o21a_A1  [deep(~110n)]` **STRONG**

`and2b_2_1`, `and2b_2_2`, `and2b_2_20`, `and2b_2_21`, `and2b_2_22`, `and2b_2_4`

### 3. 4× `and2: or4_A × or4_B  [deep(~110n)]` **STRONG**

`and2_2_10`, `and2_2_3`, `and2_2_4`, `and2_2_5`

### 4. 4× `and2: or4_A × or4_B  [shallow(~27n)]` **STRONG**

`and2_2_11`, `and2_2_12`, `and2_2_13`, `and2_2_14`

### 5. 1× `and2: {"A": "or2_N_N__X", "B": "or2_N_N__B"}`

`and2_2_0`

### 6. 1× `and2: {"A": "or4_N_N__A", "B": "xor2_N_N__A"}`

`and2_2_1`

### 7. 1× `and2: {"A": "and2_N_N__A", "B": "and3_N_N__C"}`

`and2_2_2`

### 8. 1× `and2b: {"A_N": "xor2_N_N__B", "B": "nor2_N_N__B"}`

`and2b_2_0`

### 9. 1× `and2b: * × enable  [mid(~40n)]`

`and2b_2_11`

### 10. 1× `and2b: nand4_C × flop_B  [deep(~110n)]`

`and2b_2_3`

### 11. 1× `and2b: {"A_N": "and4bb_N_N__X", "B": "o22ai_N_N__Y"}`

`and2b_2_5`

## and2 vs and2b (best cross-family)

| and2 | and2b | class Jaccard | cell Jaccard | node ratio |
|------|-------|-------------:|-------------:|-----------:|
| `and2_2_1` | `and2b_2_11` | 0.971 | 0.786 | 0.971 |
| `and2_2_0` | `and2b_2_0` | 0.927 | 0.848 | 0.925 |
| `and2_2_10` | `and2b_2_1` | 0.923 | 0.825 | 0.973 |
| `and2_2_3` | `and2b_2_1` | 0.923 | 0.825 | 0.973 |
| `and2_2_4` | `and2b_2_1` | 0.923 | 0.825 | 0.973 |
| `and2_2_5` | `and2b_2_1` | 0.923 | 0.825 | 0.973 |
| `and2_2_10` | `and2b_2_2` | 0.907 | 0.825 | 0.973 |
| `and2_2_10` | `and2b_2_20` | 0.907 | 0.825 | 0.973 |

## Summary counts

- **Strong similarity groups: 5**
- Strong pin-pattern clusters: **4**
- Instances in strong groups: **26/28**
- Mean class-Jaccard (all pairs): **0.552**
- Mean class-Jaccard (and2 ↔ and2b): **0.538**
