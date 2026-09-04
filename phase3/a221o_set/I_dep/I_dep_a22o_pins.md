# I-dependence — a22o_2_2 A2 / B2

Structural sim. Baseline **all0**; then **k=1** (single `I=1`) and **k=2**
(two consecutive ones), start cycle `s=0..10`.

Diff scoring uses cycles `0..119` only (drops final cycle `120` — end-of-window noise).

```text
a22o_2_2.A2 ← a22o_2_2__A2 = dfrtp_2_41.Q ← mux2_1_13.X  (A1=I when S=1)
a22o_2_2.B2 ← a22o_2_2__B2 = dfrtp_2_38.Q ← mux2_1_11.X
a22o_2_2.A1/B1 = or4_2_4__X / buf_2_0__X   # stubs (no I)
a22o_2_2.X  = (A1∧A2) ∨ (B1∧B2)
```

## Figures

- [`I_dep_a22o_k1_k2_heatmap.png`](I_dep_a22o_k1_k2_heatmap.png)
- Per-pin response stacks: [`timelines/I_dep_response_timelines.md`](timelines/I_dep_response_timelines.md)

## k=1 vs all0 (diff cycle counts)

| start | A2 | B2 | a22o.X | D_A2 (mux13) | D_B2 (mux11) |
|------:|---:|---:|-------:|-------------:|-------------:|
| 0 | 1 | 1 | 2 | 1 | 1 |
| 1 | 1 | 1 | 2 | 1 | 1 |
| 2 | 1 | 1 | 2 | 1 | 1 |
| 3 | 1 | 1 | 2 | 1 | 1 |
| 4 | 1 | 1 | 2 | 1 | 1 |
| 5 | 1 | 1 | 2 | 1 | 1 |
| 6 | 1 | 1 | 2 | 1 | 1 |
| 7 | 1 | 1 | 2 | 1 | 1 |
| 8 | 1 | 1 | 2 | 1 | 1 |
| 9 | 1 | 1 | 2 | 1 | 1 |
| 10 | 1 | 1 | 0 | 1 | 1 |

## k=2 vs all0 (diff cycle counts)

| start | A2 | B2 | a22o.X | D_A2 (mux13) | D_B2 (mux11) |
|------:|---:|---:|-------:|-------------:|-------------:|
| 0 | 2 | 2 | 4 | 2 | 2 |
| 1 | 2 | 2 | 4 | 2 | 2 |
| 2 | 2 | 2 | 4 | 2 | 2 |
| 3 | 2 | 2 | 4 | 2 | 2 |
| 4 | 2 | 2 | 4 | 2 | 2 |
| 5 | 2 | 2 | 4 | 2 | 2 |
| 6 | 2 | 2 | 4 | 2 | 2 |
| 7 | 2 | 2 | 4 | 2 | 2 |
| 8 | 2 | 2 | 4 | 2 | 2 |
| 9 | 2 | 2 | 2 | 2 | 2 |
| 10 | 2 | 2 | 2 | 2 | 2 |

## Detail — k1_s0 / k2_s0

### `k1_s0`

- `A2`: n=1 first@1 [1]
- `B2`: n=1 first@12 [12]
- `a22o`: n=2 first@1 [1, 12]
- `D_A2` diffs: n=1 first@0
- `D_B2` diffs: n=1 first@11

### `k2_s0`

- `A2`: n=2 first@1 [1, 2]
- `B2`: n=2 first@12 [12, 13]
- `a22o`: n=4 first@1 [1, 2, 12, 13]
- `D_A2` diffs: n=2 first@0
- `D_B2` diffs: n=2 first@11

## Notes

- On all0, mux S `inv_2_7__A` is high **121/121** cycles → `mux2_1_13` passes **I** onto A2’s flop D.
- `D_A2` / `D_B2` columns show the mux outputs feeding the A2/B2 flops (combinational I effect before the Q sample).

See also: [`I_comparisons.md`](I_comparisons.md) · [`I_dep_a221o_pins.md`](I_dep_a221o_pins.md).

Regenerate:
```bash
python3 phase3/a221o_set/run_I_dep_a22o_pins.py
python3 phase3/a221o_set/run_I_dep_response_timelines.py
python3 phase3/a221o_set/trace_I_comparisons.py
```
