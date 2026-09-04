# Fan-in from `xnor2_2_11__Y`

- Root: `sky130_fd_sc_hd__xnor2_2_11__Y`
- Visible nodes: **20**
- Edges: **27**
- Truncated at depth cut: **6**
- Stubbed (no I path): **1** — `inv_2_7__A`

## Stubbed non-I inputs

Shown once; fan-in behind them does not reach primary `I` (only-I protocol).

| Net | driver | collapsed pins | depth | nodes behind |
|-----|--------|----------------|------:|-------------:|
| `inv_2_7__A` | `and2b_2_11` | A_N=or2_2_11__A | 3 | 33 |

## Depth-cut reachability (deeper fan-in)

| Net | →FA | →I | FA hits (sample) | stub? |
|-----|:--:|:--:|------------------|:-----:|
| `inv_2_7__A` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `a21o_2_10__X` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |  |
| `and3_2_10__B` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |  |
| `and3_2_11__X` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |  |
| `inv_2_10__Y` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |  |
| `nor2_2_30__B` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |  |

## Behind counts (full fan-in under each visible net)

| Net | depth | nodes behind | flops | leaves | primaries | undriven |
|-----|------:|-------------:|------:|-------:|----------:|---------:|
| `xnor2_2_11__Y` | 0 | 51 | 14 | 2 | 2 | 0 |
| `and4_2_3__C` | 1 | 51 | 13 | 2 | 2 | 0 |
| `xnor2_2_11__B` | 1 | 49 | 13 | 2 | 2 | 0 |
| `and4_2_4__D` | 2 | 49 | 13 | 2 | 2 | 0 |
| `inv_2_10__A` | 2 | 37 | 10 | 2 | 2 | 0 |
| `I` | 3 | 0 | 0 | 0 | 0 | 0 |
| `and4_2_3__A` | 3 | 41 | 10 | 2 | 2 | 0 |
| `and4_2_3__B` | 3 | 45 | 11 | 2 | 2 | 0 |
| `inv_2_7__A` | 3 | 33 | 9 | 1 | 1 | 0 |
| `or3_2_8__A` | 3 | 37 | 9 | 2 | 2 | 0 |
| `or3_2_8__B` | 3 | 49 | 12 | 2 | 2 | 0 |
| `a32o_2_2__X` | 4 | 41 | 11 | 2 | 2 | 0 |
| `dfrtp_2_25__D` | 4 | 45 | 12 | 2 | 2 | 0 |
| `nor2_2_30__Y` | 4 | 37 | 10 | 2 | 2 | 0 |
| `o21a_2_11__X` | 4 | 49 | 13 | 2 | 2 | 0 |
| `a21o_2_10__X` | 5 | 45 | 12 | 2 | 2 | 0 |
| `and3_2_10__B` | 5 | 41 | 11 | 2 | 2 | 0 |
| `and3_2_11__X` | 5 | 45 | 12 | 2 | 2 | 0 |
| `inv_2_10__Y` | 5 | 38 | 10 | 2 | 2 | 0 |
| `nor2_2_30__B` | 5 | 37 | 10 | 2 | 2 | 0 |

## Nodes by depth

- **d=0** (1): `xnor2_2_11__Y`
- **d=1** (2): `and4_2_3__C`, `xnor2_2_11__B`
- **d=2** (2): `and4_2_4__D`, `inv_2_10__A`
- **d=3** (6): `and4_2_3__A`, `and4_2_3__B`, `or3_2_8__B`, `I`, `inv_2_7__A`, `or3_2_8__A`
- **d=4** (4): `a32o_2_2__X`, `dfrtp_2_25__D`, `o21a_2_11__X`, `nor2_2_30__Y`
- **d=5** (5): `and3_2_10__B`, `inv_2_10__Y`, `a21o_2_10__X`, `and3_2_11__X`, `nor2_2_30__B`
