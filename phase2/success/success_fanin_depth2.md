# Fan-in from `success`

- Root: `success`
- Visible nodes: **6**
- Edges: **6**
- Truncated at depth cut: **4**

## Depth-cut reachability (deeper fan-in)

| Net | →FA | →I | FA hits (sample) |
|-----|:--:|:--:|------------------|
| `a32o_2_4__B2` | yes |  | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |
| `and2_2_15__X` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |
| `and4b_2_3__X` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `and3_2_2__C`, … |
| `inv_2_23__A` | yes | yes | `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, … |

## Behind counts (full fan-in under each visible net)

| Net | depth | nodes behind | flops | leaves | primaries | undriven |
|-----|------:|-------------:|------:|-------:|----------:|---------:|
| `success` | 0 | 466 | 78 | 3 | 2 | 1 |
| `a32o_2_4__X` | 1 | 466 | 79 | 3 | 2 | 1 |
| `a32o_2_4__B2` | 2 | 36 | 10 | 1 | 1 | 0 |
| `and2_2_15__X` | 2 | 81 | 20 | 2 | 2 | 0 |
| `and4b_2_3__X` | 2 | 383 | 54 | 2 | 2 | 0 |
| `inv_2_23__A` | 2 | 65 | 22 | 3 | 2 | 1 |

## Nodes by depth

- **d=0** (1): `success`
- **d=1** (1): `a32o_2_4__X`
- **d=2** (4): `a32o_2_4__B2`, `and2_2_15__X`, `and4b_2_3__X`, `inv_2_23__A`
