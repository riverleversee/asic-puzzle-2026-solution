# Full-adder endpoints (structural)

Source: `netlist/puzzle_structural.v`
Method: xor/xnor paired with AO/OA/maj sharing ≥2 data inputs

- FA-like pairs: **8**
- Sum nets: **8**
- Carry nets: **8**

| # | Sum | Sum cell | Carry | Carry cell | Shared inputs |
|--:|-----|----------|-------|------------|---------------|
| 1 | `and3_2_2__C` | `xnor2_2` | `o211a_2_0__X` | `o211a_2` | `xor2_2_0__B`, `xor2_2_4__A` |
| 2 | `nor2_2_31__B` | `xnor2_2` | `a21oi_2_13__Y` | `a21oi_2` | `inv_2_7__A`, `or4_2_4__A` |
| 3 | `nor2_2_8__A` | `xnor2_2` | `xor2_2_2__A` | `a32o_2` | `or4_2_4__B`, `xor2_2_0__X` |
| 4 | `or4_2_0__A` | `xor2_2` | `xor2_2_6__A` | `a21o_2` | `xor2_2_8__A`, `xor2_2_8__B` |
| 5 | `xnor2_2_26__A` | `xnor2_2` | `a221o_2_4__X` | `a221o_2` | `xor2_2_14__B`, `xor2_2_19__A` |
| 6 | `xnor2_2_28__Y` | `xnor2_2` | `or3_2_17__A` | `a211oi_2` | `or2_2_9__A`, `or3b_2_0__A` |
| 7 | `xor2_2_0__X` | `xor2_2` | `a31o_2_8__X` | `a31o_2` | `xor2_2_0__B`, `xor2_2_7__A` |
| 8 | `xor2_2_9__X` | `xor2_2` | `a21o_2_9__X` | `a21o_2` | `inv_2_5__A`, `xor2_2_9__A` |
