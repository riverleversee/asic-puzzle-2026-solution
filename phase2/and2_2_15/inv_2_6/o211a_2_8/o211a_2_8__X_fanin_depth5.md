# Fan-in from `o211a_2_8__X`

- Root: `sky130_fd_sc_hd__o211a_2_8__X`
- Visible nodes: **14**
- Edges: **21**
- Truncated at depth cut: **4**
- Stubbed (no I path): **4** — `inv_2_7__A`, `inv_2_7__Y`, `inv_2_9__A`, `inv_2_9__Y`

## Stubbed non-I inputs

Shown once; fan-in behind them does not reach primary `I` (only-I protocol).

| Net | driver | collapsed pins | depth | nodes behind |
|-----|--------|----------------|------:|-------------:|
| `inv_2_7__A` | `and2b_2_11` | A_N=or2_2_11__A | 1 | 33 |
| `inv_2_7__Y` | `inv_2_7` | A=inv_2_7__A | 4 | 34 |
| `inv_2_9__A` | `and4bb_2_6` | A_N=or4_2_4__A, C=or4_2_4__D, D=or4_2_4__B | 4 | 33 |
| `inv_2_9__Y` | `inv_2_9` | A=inv_2_9__A | 4 | 34 |

## Depth-cut reachability (deeper fan-in)

| Net | →FA | →I | FA hits (sample) | stub? |
|-----|:--:|:--:|------------------|:-----:|
| `inv_2_7__A` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `inv_2_7__Y` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `inv_2_9__A` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |
| `inv_2_9__Y` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … | ⋯ |

## Behind counts (full fan-in under each visible net)

| Net | depth | nodes behind | flops | leaves | primaries | undriven |
|-----|------:|-------------:|------:|-------:|----------:|---------:|
| `o211a_2_8__X` | 0 | 44 | 11 | 2 | 2 | 0 |
| `inv_2_7__A` | 1 | 33 | 9 | 1 | 1 | 0 |
| `inv_2_8__A` | 1 | 44 | 10 | 2 | 2 | 0 |
| `mux2_1_7__A0` | 1 | 44 | 11 | 2 | 2 | 0 |
| `or2_2_7__X` | 1 | 44 | 11 | 2 | 2 | 0 |
| `I` | 2 | 0 | 0 | 0 | 0 | 0 |
| `dfrtp_2_29__D` | 2 | 44 | 11 | 2 | 2 | 0 |
| `or2_2_7__A` | 2 | 44 | 10 | 2 | 2 | 0 |
| `a22o_2_1__X` | 3 | 44 | 11 | 2 | 2 | 0 |
| `inv_2_8__Y` | 3 | 44 | 11 | 2 | 2 | 0 |
| `mux2_1_6__X` | 3 | 44 | 11 | 2 | 2 | 0 |
| `inv_2_7__Y` | 4 | 34 | 9 | 1 | 1 | 0 |
| `inv_2_9__A` | 4 | 33 | 9 | 1 | 1 | 0 |
| `inv_2_9__Y` | 4 | 34 | 9 | 1 | 1 | 0 |

## Nodes by depth

- **d=0** (1): `o211a_2_8__X`
- **d=1** (4): `inv_2_7__A`, `inv_2_8__A`, `mux2_1_7__A0`, `or2_2_7__X`
- **d=2** (3): `dfrtp_2_29__D`, `I`, `or2_2_7__A`
- **d=3** (3): `inv_2_8__Y`, `mux2_1_6__X`, `a22o_2_1__X`
- **d=4** (3): `inv_2_7__Y`, `inv_2_9__A`, `inv_2_9__Y`
