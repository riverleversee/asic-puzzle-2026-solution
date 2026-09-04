# Type 7 (2× · noI): strong g5 remainder (and2+and2b, size 2)

- Kind: `strong_group_remainder`
- Size: **2**
- I: **noI** — input-independent (no primary **`I`** in fan-in)
- Mean class-Jaccard: **0.927**
- Representative expand-back: `and2_2_0` → `and3_2_0__C`

Expand-back points are the **and2 / and2b outputs** in this type (not join0/join1 banks).

## Members

| Instance | Family | Out net | pin pattern | nodes | ff | figure |
|----------|--------|---------|-------------|------:|---:|--------|
| `and2_2_0` **REP** | `and2` | `and3_2_0__C` | `{"A": "or2_N_N__X", "B": "or2_N_N__B"}` | 40 | 9 | [`and2_2_0_out_and3_2_0__C_d5.png`](and2_2_0_out_and3_2_0__C_d5.png) |
| `and2b_2_0` | `and2b` | `or2_2_0__B` | `{"A_N": "xor2_N_N__B", "B": "nor2_N_N__B"}` | 37 | 9 | [`and2b_2_0_out_or2_2_0__B_d5.png`](and2b_2_0_out_or2_2_0__B_d5.png) |
