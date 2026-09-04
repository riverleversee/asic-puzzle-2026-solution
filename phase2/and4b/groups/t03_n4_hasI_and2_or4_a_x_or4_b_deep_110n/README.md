# Type 3 (4× · hasI): and2: or4_A × or4_B  [deep(~110n)]

- Kind: `pin_pattern`
- Size: **4**
- I: **hasI** — fan-in reaches primary **`I`**
- Mean class-Jaccard: **1.0**
- Representative expand-back: `and2_2_4` → `and4_2_1__B`

Expand-back points are the **and2 / and2b outputs** in this type (not join0/join1 banks).

## Members

| Instance | Family | Out net | pin pattern | nodes | ff | figure |
|----------|--------|---------|-------------|------:|---:|--------|
| `and2_2_10` | `and2` | `and3_2_5__B` | `{"A": "or4_N_N__A", "B": "or4_N_N__B"}` | 109 | 7 | [`and2_2_10_out_and3_2_5__B_d5.png`](and2_2_10_out_and3_2_5__B_d5.png) |
| `and2_2_3` | `and2` | `and4_2_0__A` | `{"A": "or4_N_N__A", "B": "or4_N_N__B"}` | 109 | 7 | [`and2_2_3_out_and4_2_0__A_d5.png`](and2_2_3_out_and4_2_0__A_d5.png) |
| `and2_2_4` **REP** | `and2` | `and4_2_1__B` | `{"A": "or4_N_N__A", "B": "or4_N_N__B"}` | 109 | 7 | [`and2_2_4_out_and4_2_1__B_d5.png`](and2_2_4_out_and4_2_1__B_d5.png) |
| `and2_2_5` | `and2` | `and4_2_0__D` | `{"A": "or4_N_N__A", "B": "or4_N_N__B"}` | 109 | 7 | [`and2_2_5_out_and4_2_0__D_d5.png`](and2_2_5_out_and4_2_0__D_d5.png) |
