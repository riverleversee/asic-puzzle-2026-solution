# Fan-in from `inv_2_23__A`

- Root: `sky130_fd_sc_hd__inv_2_23__A`
- Visible nodes: **13**
- Edges: **13**
- Truncated at depth cut: **5**

## Depth-cut reachability (deeper fan-in)

| Net | →FA | →I | FA hits (sample) |
|-----|:--:|:--:|------------------|
| `a22o_2_2__X` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |
| `mux2_1_12__A0` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |
| `mux2_1_12__A1` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |
| `or2_2_11__A` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |
| `or4bb_2_0__X` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |

## Behind counts (full fan-in under each visible net)

| Net | depth | nodes behind | flops | leaves | primaries | undriven |
|-----|------:|-------------:|------:|-------:|----------:|---------:|
| `inv_2_23__A` | 0 | 65 | 22 | 3 | 2 | 1 |
| `inv_2_11__A` | 1 | 64 | 21 | 3 | 2 | 1 |
| `a31o_2_12__X` | 2 | 64 | 22 | 3 | 2 | 1 |
| `I` | 3 | 0 | 0 | 0 | 0 | 0 |
| `a221o_2_1__X` | 3 | 62 | 21 | 3 | 2 | 1 |
| `inv_2_7__A` | 3 | 33 | 9 | 1 | 1 | 0 |
| `enable` | 4 | 0 | 0 | 0 | 0 | 0 |
| `a22o_2_2__X` | 4 | 60 | 21 | 2 | 2 | 0 |
| `conb_1_2__HI` | 4 | 0 | 0 | 0 | 0 | 0 |
| `mux2_1_12__A0` | 4 | 55 | 19 | 2 | 2 | 0 |
| `mux2_1_12__A1` | 4 | 53 | 18 | 2 | 2 | 0 |
| `or2_2_11__A` | 4 | 33 | 8 | 1 | 1 | 0 |
| `or4bb_2_0__X` | 4 | 34 | 9 | 1 | 1 | 0 |

## Nodes by depth

- **d=0** (1): `inv_2_23__A`
- **d=1** (1): `inv_2_11__A`
- **d=2** (1): `a31o_2_12__X`
- **d=3** (3): `I`, `a221o_2_1__X`, `inv_2_7__A`
- **d=4** (7): `a22o_2_2__X`, `conb_1_2__HI`, `mux2_1_12__A0`, `mux2_1_12__A1`, `or4bb_2_0__X`, `enable`, `or2_2_11__A`
