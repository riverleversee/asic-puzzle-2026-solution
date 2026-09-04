# Phase 4 — sim of forced solution

I pattern = `force_1` from [`forced.json`](forced.json) (22 ones); unidentified cycles driven **0**.
Sim length **125** (= 121 + 4 extra).

**I ones:** `[7, 9, 11, 16, 29, 31, 33, 35, 48, 50, 57, 63, 70, 76, 78, 83, 91, 98, 104, 107, 111, 113]`

## Observe

| net | n high | first |
|-----|-------:|------:|
| `success` | 3 | 122 |
| `and2_2_15.X` | 11 | — |
| `inv_2_6.Y` | 125 | — |
| `and4_2_3.X` | 11 | 114 |
| `inv_2_23.A` (SET sticky path) | 125 | — |

Period-11 ones: `[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]`

## Verdict

**`success` rose** under the forced pattern.

JSON: [`sim_solution.json`](sim_solution.json)

```bash
python3 phase4/run_forcer.py
python3 phase4/sim_solution.py
```
