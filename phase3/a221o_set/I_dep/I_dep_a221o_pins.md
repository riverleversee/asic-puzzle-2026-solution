# I-dependence — a221o A2 / B2 / C1

Structural sim. Baseline **all0**; then **k=1** (single `I=1`) and **k=2**
(two consecutive ones), start cycle `s=0..10`.

Diff scoring uses cycles `0..119` only (drops final cycle `120` — end-of-window noise).

```text
a221o.A2 ← mux2_1_12__A1
a221o.B2 ← mux2_1_12__A0
a221o.C1 ← a22o_2_2__X
```

## Figures

- [`I_dep_k1_k2_heatmap.png`](I_dep_k1_k2_heatmap.png) — which pins move for each start
- Per-pin response stacks (I=1 marked, ≠all0 bars): [`timelines/I_dep_response_timelines.md`](timelines/I_dep_response_timelines.md)

## k=1 vs all0 (diff cycle counts)

| start | A2 | B2 | C1 | a221o |
|------:|---:|---:|---:|------:|
| 0 | 1 | 1 | 2 | 3 |
| 1 | 1 | 1 | 2 | 4 |
| 2 | 1 | 1 | 2 | 4 |
| 3 | 1 | 1 | 2 | 4 |
| 4 | 1 | 1 | 2 | 4 |
| 5 | 1 | 1 | 2 | 4 |
| 6 | 1 | 1 | 2 | 4 |
| 7 | 1 | 1 | 2 | 4 |
| 8 | 1 | 1 | 2 | 4 |
| 9 | 1 | 1 | 2 | 4 |
| 10 | 1 | 1 | 0 | 2 |

## k=2 vs all0 (diff cycle counts)

| start | A2 | B2 | C1 | a221o |
|------:|---:|---:|---:|------:|
| 0 | 2 | 2 | 4 | 5 |
| 1 | 2 | 2 | 4 | 6 |
| 2 | 2 | 2 | 4 | 6 |
| 3 | 2 | 2 | 4 | 6 |
| 4 | 2 | 2 | 4 | 6 |
| 5 | 2 | 2 | 4 | 6 |
| 6 | 2 | 2 | 4 | 6 |
| 7 | 2 | 2 | 4 | 6 |
| 8 | 2 | 2 | 4 | 6 |
| 9 | 2 | 2 | 2 | 4 |
| 10 | 2 | 2 | 2 | 5 |

## Detail — k1_s0 / k2_s0 first diffs

### `k1_s0`

- `A2`: n=1 first@10 [10]
- `B2`: n=1 first@11 [11]
- `C1`: n=2 first@1 [1, 12]
- `a221o`: n=3 first@1 [1, 11, 12]

### `k2_s0`

- `A2`: n=2 first@10 [10, 11]
- `B2`: n=2 first@11 [11, 12]
- `C1`: n=4 first@1 [1, 2, 12, 13]
- `a221o`: n=5 first@1 [1, 2, 11, 12, 13]

## Notes

- On all0, `inv_2_7__A` (mux S / and2b.Y) is high **121/121** cycles — muxes pass A1, so a lone `I=1` can enter the A2 path via `mux2_1_13`.
See also: [`I_comparisons.md`](I_comparisons.md) — structural I-vs-I compare count.

Regenerate:
```bash
python3 phase3/a221o_set/run_I_dep_a221o_pins.py
python3 phase3/a221o_set/run_I_dep_response_timelines.py
python3 phase3/a221o_set/trace_I_comparisons.py
```
