# Type 6 (2× · noI): strong g4 remainder (and2+and2b, size 2)

- Kind: `strong_group_remainder`
- Size: **2**
- I: **noI** — input-independent (no primary **`I`** in fan-in)
- Mean class-Jaccard: **0.971**
- Representative expand-back: `and2_2_1` → `or2_2_1__A`

Expand-back points are the **and2 / and2b outputs** in this type (not join0/join1 banks).

## Members

| Instance | Family | Out net | pin pattern | nodes | ff | figure |
|----------|--------|---------|-------------|------:|---:|--------|
| `and2_2_1` **REP** | `and2` | `or2_2_1__A` | `{"A": "or4_N_N__A", "B": "xor2_N_N__A"}` | 34 | 9 | [`and2_2_1_out_or2_2_1__A_d5.png`](and2_2_1_out_or2_2_1__A_d5.png) |
| `and2b_2_11` | `and2b` | `inv_2_7__A` | `{"A_N": "or2_N_N__A", "B": "enable"}` | 33 | 9 | [`and2b_2_11_out_inv_2_7__A_d5.png`](and2b_2_11_out_inv_2_7__A_d5.png) |
