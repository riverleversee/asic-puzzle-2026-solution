# I-independent stub timelines (a31o / a221o / a22o)

Structural sim · stimulus **all0** (also checked vs **all1**).

```text
and2b_2_11:
  A_N = or2_2_11__A   ← dfrtp_2_47.Q  (FA-side flop; I-independent)
  B   = enable
  Y   = inv_2_7__A    → a31o_2_12.A2

a221o_2_1.A1  ←  or4bb_2_0__X
a22o_2_2.A1   ←  or4_2_4__X
a22o_2_2.B1   ←  buf_2_0__X   (= or4_2_4__X buffered)
a221o_2_1.C1  ←  a22o_2_2__X
```

Name aliases (same net, different labels elsewhere):

| Canonical net | Also called |
|---------------|-------------|
| `inv_2_7__A` | `and2b_2_11.Y` |
| `or2_2_11__A` | `and2b_2_11.A_N`, `dfrtp_2_47.Q` |
| `or4_2_4__X` | `a22o_2_2.A1`, `buf_2_0.A` |
| `buf_2_0__X` | `a22o_2_2.B1` (= `or4_2_4__X`) |

Fan-in figures stub at `inv_2_7__A` (only-I), so `or2_2_11__A` is **not drawn** there —
it is the collapsed `A_N` under that stub (annotated on the box).

- stub lanes identical all0 vs all1 (and2b.Y/A_N, or4bb, or4.X, buf): **True**
- `or4_2_4.X` == `buf_2_0.X` on all0: **True**
- `a22o_2_2.X` differs all0 vs all1 (I-reaching A2/B2 arms): **True**

Note: under all0, `and2b.A_N` stays 0 so `and2b.Y = enable` (high every cycle after enable).

## Ones (all0)

- `inv_2_7__A` (and2b_2_11.Y) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …]  (n=121)`
- `or2_2_11__A` (and2b_2_11.A_N) high @ `[]`
- `or4bb_2_0__X` high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, …]  (n=110)`
- `or4_2_4__X` (a22o.A1) high @ `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, …]  (n=110)`
- `buf_2_0__X` (a22o.B1) high @ `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, …]  (n=110)`
- `a22o_2_2__X` high @ `[]`

Figure: [`noI_stub_timeline.png`](noI_stub_timeline.png)

CSV: [`noI_stub_timeline_all0.csv`](noI_stub_timeline_all0.csv)

Regenerate:
```bash
python3 phase2/a221o_behind_inv23/run_noI_stub_timeline.py
```
