# Pre-`and4_2_3` region size (`and2_2_15`)

Fan-in set diffs on structural netlist (no simulation).

## Verdict: `LARGE_PRE_AND4=no`

- A-exclusive nodes: **15** (17.9% of full cone 84)
- Thresholds: ≥20 nodes **or** ≥25% of full

## Counts

| Region | nodes | flops | primaries |
|--------|------:|------:|-----------|
| Full `and2_2_15.X` | **84** | **20** | `I`, `enable` |
| A-arm `inv_2_6.Y` | **51** | **12** | `I`, `enable` |
| B-arm `and4_2_3.X` | **68** | **17** | `I`, `enable` |
| A exclusive (A−B) | **15** | **3** | — |
| B exclusive (B−A) | **32** | **8** | — |
| Shared (A∩B) | **36** | **9** | `I`, `enable` |

## A-exclusive class histogram

| class | n |
|-------|--:|
| `aoi` | 4 |
| `inv` | 4 |
| `flop` | 3 |
| `mux` | 2 |
| `or` | 1 |
| `nand` | 1 |

## A-exclusive leaves (sample)

—

JSON: [`pre_and4_region.json`](pre_and4_region.json)

```bash
python3 phase2/and2_2_15/run_count_pre_and4.py
```
