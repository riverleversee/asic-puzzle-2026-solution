# Fan-in from `dfrtp_2_25__D`

- Root: `sky130_fd_sc_hd__dfrtp_2_25__D`
- Visible nodes: **14**
- Edges: **24**
- Truncated at depth cut: **2**
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
| `nor2_2_30__B` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |  |

## Behind counts (full fan-in under each visible net)

| Net | depth | nodes behind | flops | leaves | primaries | undriven |
|-----|------:|-------------:|------:|-------:|----------:|---------:|
| `dfrtp_2_25__D` | 0 | 45 | 12 | 2 | 2 | 0 |
| `a21o_2_10__X` | 1 | 45 | 12 | 2 | 2 | 0 |
| `and3_2_11__X` | 1 | 45 | 12 | 2 | 2 | 0 |
| `and4_2_3__A` | 2 | 41 | 10 | 2 | 2 | 0 |
| `and4_2_3__B` | 2 | 45 | 11 | 2 | 2 | 0 |
| `inv_2_10__A` | 2 | 37 | 10 | 2 | 2 | 0 |
| `I` | 3 | 0 | 0 | 0 | 0 | 0 |
| `a32o_2_2__X` | 3 | 41 | 11 | 2 | 2 | 0 |
| `inv_2_7__A` | 3 | 33 | 9 | 1 | 1 | 0 |
| `or3_2_8__A` | 3 | 37 | 9 | 2 | 2 | 0 |
| `and3_2_10__B` | 4 | 41 | 11 | 2 | 2 | 0 |
| `inv_2_10__Y` | 4 | 38 | 10 | 2 | 2 | 0 |
| `nor2_2_30__Y` | 4 | 37 | 10 | 2 | 2 | 0 |
| `nor2_2_30__B` | 5 | 37 | 10 | 2 | 2 | 0 |

## Nodes by depth

- **d=0** (1): `dfrtp_2_25__D`
- **d=1** (2): `a21o_2_10__X`, `and3_2_11__X`
- **d=2** (3): `and4_2_3__A`, `and4_2_3__B`, `inv_2_10__A`
- **d=3** (4): `a32o_2_2__X`, `I`, `inv_2_7__A`, `or3_2_8__A`
- **d=4** (3): `and3_2_10__B`, `inv_2_10__Y`, `nor2_2_30__Y`
- **d=5** (1): `nor2_2_30__B`
