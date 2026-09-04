# Type 8 (2× · noI): outliers (not in strong type clusters)

- Kind: `outlier`
- Size: **2**
- I: **noI** — input-independent (no primary **`I`** in fan-in)
- Mean class-Jaccard: **None**
- Representative expand-back: `and2_2_2` → `and2_2_2__X`

Expand-back points are the **and2 / and2b outputs** in this type (not join0/join1 banks).

## Members

| Instance | Family | Out net | pin pattern | nodes | ff | figure |
|----------|--------|---------|-------------|------:|---:|--------|
| `and2_2_2` **REP** | `and2` | `and2_2_2__X` | `{"A": "and2_N_N__A", "B": "and3_N_N__C"}` | 46 | 9 | [`and2_2_2_out_and2_2_2__X_d5.png`](and2_2_2_out_and2_2_2__X_d5.png) |
| `and2b_2_5` | `and2b` | `xor2_2_6__B` | `{"A_N": "and4bb_N_N__X", "B": "o22ai_N_N__Y"}` | 43 | 9 | [`and2b_2_5_out_xor2_2_6__B_d5.png`](and2b_2_5_out_xor2_2_6__B_d5.png) |
