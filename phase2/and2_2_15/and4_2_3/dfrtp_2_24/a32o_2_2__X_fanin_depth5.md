# Fan-in from `a32o_2_2__X`

- Root: `sky130_fd_sc_hd__a32o_2_2__X`
- Visible nodes: **10**
- Edges: **18**
- Truncated at depth cut: **1**
- Stubbed (no I path): **1** — `inv_2_7__A`

## Stubbed non-I inputs

Shown once; fan-in behind them does not reach primary `I` (only-I protocol).

| Net | driver | collapsed pins | depth | nodes behind |
|-----|--------|----------------|------:|-------------:|
| `inv_2_7__A` | `and2b_2_11` | A_N=or2_2_11__A | 1 | 33 |

## Depth-cut reachability (deeper fan-in)

| Net | →FA | →I | FA hits (sample) | stub? |
|-----|:--:|:--:|------------------|:-----:|
| `inv_2_7__A` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |

## Behind counts (full fan-in under each visible net)

| Net | depth | nodes behind | flops | leaves | primaries | undriven |
|-----|------:|-------------:|------:|-------:|----------:|---------:|
| `a32o_2_2__X` | 0 | 41 | 11 | 2 | 2 | 0 |
| `I` | 1 | 0 | 0 | 0 | 0 | 0 |
| `and3_2_10__B` | 1 | 41 | 11 | 2 | 2 | 0 |
| `and4_2_3__A` | 1 | 41 | 10 | 2 | 2 | 0 |
| `inv_2_10__Y` | 1 | 38 | 10 | 2 | 2 | 0 |
| `inv_2_7__A` | 1 | 33 | 9 | 1 | 1 | 0 |
| `inv_2_10__A` | 2 | 37 | 10 | 2 | 2 | 0 |
| `or3_2_8__A` | 2 | 37 | 9 | 2 | 2 | 0 |
| `nor2_2_30__Y` | 3 | 37 | 10 | 2 | 2 | 0 |
| `nor2_2_30__B` | 4 | 37 | 10 | 2 | 2 | 0 |

## Nodes by depth

- **d=0** (1): `a32o_2_2__X`
- **d=1** (5): `I`, `and3_2_10__B`, `and4_2_3__A`, `inv_2_10__Y`, `inv_2_7__A`
- **d=2** (2): `or3_2_8__A`, `inv_2_10__A`
- **d=3** (1): `nor2_2_30__Y`
- **d=4** (1): `nor2_2_30__B`
