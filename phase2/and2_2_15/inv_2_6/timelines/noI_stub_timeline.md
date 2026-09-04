# I-independent stub timelines — `inv_2_7` / `inv_2_9` (a31o A-arm)

Structural sim · **all0** (checked identical vs **all1** for stub lanes).

## Primary NO-I nets (required)

| Net | Role | high cycles (all0) |
|-----|------|--------------------|
| `inv_2_7__A` | a31o.A2 = and2b_2_11.Y | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …]  (n=121)` |
| `inv_2_7__Y` | inv of stub A | `[]` |
| `inv_2_9__A` | a31o.A1 = and4bb_2_6.X | `[10, 21, 32, 43, 54, 65, 76, 87, 98, 109, 120]` |
| `inv_2_9__Y` | inv of stub A | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, …]  (n=110)` |

**Stub lanes all0 ≡ all1:** `True`

```text
a31o_2_11:
  A1 = inv_2_9__A  ← and4bb_2_6.X   # NO-I stub (FA)
  A2 = inv_2_7__A  ← and2b_2_11.Y   # NO-I stub (FA)
  A3 = mux2_1_7__X                 # →I
  B1 = inv_2_6__A                  # sticky Q
```

- `a31o_2_11.X` differs all0 vs all1: **False**
- `mux2_1_7.X` differs all0 vs all1: **True**

## Context (FA priors / observe)

- `or2_2_11__A` (and2b.A_N) high @ `[]`
- `or4_2_4__A` high @ `[1, 3, 5, 7, 9, 12, 14, 16, 18, 20, 23, 25, 27, 29, 31, 34, 36, 38, 40, 42, 45, 47, 49, 51, …]  (n=55)`
- `or4_2_4__B` high @ `[2, 3, 6, 7, 10, 13, 14, 17, 18, 21, 24, 25, 28, 29, 32, 35, 36, 39, 40, 43, 46, 47, 50, 51, …]  (n=55)`
- `or4_2_4__C` high @ `[4, 5, 6, 7, 15, 16, 17, 18, 26, 27, 28, 29, 37, 38, 39, 40, 48, 49, 50, 51, 59, 60, 61, 62, …]  (n=44)`
- `or4_2_4__D` high @ `[8, 9, 10, 19, 20, 21, 30, 31, 32, 41, 42, 43, 52, 53, 54, 63, 64, 65, 74, 75, 76, 85, 86, 87, …]  (n=33)`
- `a31o_2_11__X` high @ `[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, …]  (n=111)`

Figure: [`noI_stub_timeline.png`](noI_stub_timeline.png) — top panel = inv_2_7/9 only

CSV: [`noI_stub_timeline_all0.csv`](noI_stub_timeline_all0.csv)

I=1 probes (separate): [`I1_probe_timeline.md`](I1_probe_timeline.md)

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py
```
