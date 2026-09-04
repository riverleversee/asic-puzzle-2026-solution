# Fan-in from `a221o_2_1__X`

- Root: `sky130_fd_sc_hd__a221o_2_1__X`
- Visible nodes: **19**
- Edges: **29**
- Truncated at depth cut: **6**
- Stubbed (no I path): **5** — `conb_1_2__HI`, `or4bb_2_0__X`, `buf_2_0__X`, `or4_2_4__X`, `inv_2_7__A`

## Stubbed non-I inputs

Shown once; fan-in behind them does not reach primary `I` (only-I protocol).

| Net | driver | collapsed pins | depth | nodes behind |
|-----|--------|----------------|------:|-------------:|
| `conb_1_2__HI` | `—` | — | 1 | 0 |
| `or4bb_2_0__X` | `or4bb_2_0` | A=or4_2_4__A, B=or4_2_4__C | 1 | 34 |
| `buf_2_0__X` | `buf_2_0` | A=or4_2_4__X | 2 | 35 |
| `or4_2_4__X` | `or4_2_4` | A=or4_2_4__A, B=or4_2_4__B, C=or4_2_4__C | 2 | 34 |
| `inv_2_7__A` | `and2b_2_11` | A_N=or2_2_11__A | 3 | 33 |

## Depth-cut reachability (deeper fan-in)

| Net | →FA | →I | FA hits (sample) | stub? |
|-----|:--:|:--:|------------------|:-----:|
| `conb_1_2__HI` |  |  |  | ⋯ |
| `or4bb_2_0__X` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `buf_2_0__X` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `or4_2_4__X` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `inv_2_7__A` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `mux2_1_8__A1` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |  |

## Behind counts (full fan-in under each visible net)

| Net | depth | nodes behind | flops | leaves | primaries | undriven |
|-----|------:|-------------:|------:|-------:|----------:|---------:|
| `a221o_2_1__X` | 0 | 62 | 21 | 3 | 2 | 1 |
| `a22o_2_2__X` | 1 | 60 | 21 | 2 | 2 | 0 |
| `conb_1_2__HI` | 1 | 0 | 0 | 0 | 0 | 0 |
| `mux2_1_12__A0` | 1 | 55 | 19 | 2 | 2 | 0 |
| `mux2_1_12__A1` | 1 | 53 | 18 | 2 | 2 | 0 |
| `or4bb_2_0__X` | 1 | 34 | 9 | 1 | 1 | 0 |
| `a22o_2_2__A2` | 2 | 35 | 9 | 2 | 2 | 0 |
| `a22o_2_2__B2` | 2 | 57 | 20 | 2 | 2 | 0 |
| `buf_2_0__X` | 2 | 35 | 9 | 1 | 1 | 0 |
| `mux2_1_10__X` | 2 | 53 | 19 | 2 | 2 | 0 |
| `mux2_1_12__X` | 2 | 55 | 20 | 2 | 2 | 0 |
| `or4_2_4__X` | 2 | 34 | 9 | 1 | 1 | 0 |
| `inv_2_7__A` | 3 | 33 | 9 | 1 | 1 | 0 |
| `mux2_1_11__X` | 3 | 57 | 21 | 2 | 2 | 0 |
| `mux2_1_13__X` | 3 | 35 | 10 | 2 | 2 | 0 |
| `mux2_1_8__A0` | 3 | 51 | 17 | 2 | 2 | 0 |
| `I` | 4 | 0 | 0 | 0 | 0 | 0 |
| `mux2_1_8__X` | 4 | 51 | 18 | 2 | 2 | 0 |
| `mux2_1_8__A1` | 5 | 49 | 16 | 2 | 2 | 0 |

## Nodes by depth

- **d=0** (1): `a221o_2_1__X`
- **d=1** (5): `a22o_2_2__X`, `conb_1_2__HI`, `mux2_1_12__A0`, `mux2_1_12__A1`, `or4bb_2_0__X`
- **d=2** (6): `a22o_2_2__A2`, `a22o_2_2__B2`, `buf_2_0__X`, `or4_2_4__X`, `mux2_1_12__X`, `mux2_1_10__X`
- **d=3** (4): `mux2_1_13__X`, `mux2_1_11__X`, `inv_2_7__A`, `mux2_1_8__A0`
- **d=4** (2): `I`, `mux2_1_8__X`
- **d=5** (1): `mux2_1_8__A1`
