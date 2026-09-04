# `dfrtp_2_20` — `I1_probe_timeline`

and4.C · dfrtp_2_20 · xnor2_2_11

**Highlighted lane:** `Q` → **and4.C** (yellow band + ★).

Figure: [`I1_probe_timeline.png`](I1_probe_timeline.png)

CSV: [`I1_probe_timeline.csv`](I1_probe_timeline.csv)

## Observe summary

| mode | #I | Q n | first | and4.X n |
|------|---:|--------:|------:|---------:|
| `all0` | 0 | 0 | — | 0 |
| `all1` | 121 | 57 | 16 | 1 |
| `I1_cyc1` | 1 | 0 | — | 0 |
| `I1_cyc10` | 1 | 0 | — | 0 |
| `I1_cyc1_12` | 2 | 0 | — | 0 |

## Per-mode lanes

### `all0`  I=`[]`

- `xnor_B` (B  xnor2_2_11__B) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …] (n=121)`
- `xnor_Y` (Y  xnor → flop.D) high @ `[]`
- `Q` (★ Q → and4.C) **← and4.C** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

### `all1`  I=`[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …] (n=121)`

- `xnor_B` (B  xnor2_2_11__B) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, …] (n=114)`
- `xnor_Y` (Y  xnor → flop.D) high @ `[15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 47, 48, 49, 50, 51, 52, 53, 54, …] (n=58)`
- `Q` (★ Q → and4.C) **← and4.C** high @ `[16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 48, 49, 50, 51, 52, 53, 54, 55, …] (n=57)`
- `and4_X` (and4.X) high @ `[22]`

### `I1_cyc1`  I=`[1]`

- `xnor_B` (B  xnor2_2_11__B) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …] (n=121)`
- `xnor_Y` (Y  xnor → flop.D) high @ `[]`
- `Q` (★ Q → and4.C) **← and4.C** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

### `I1_cyc10`  I=`[10]`

- `xnor_B` (B  xnor2_2_11__B) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …] (n=121)`
- `xnor_Y` (Y  xnor → flop.D) high @ `[]`
- `Q` (★ Q → and4.C) **← and4.C** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

### `I1_cyc1_12`  I=`[1, 12]`

- `xnor_B` (B  xnor2_2_11__B) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …] (n=121)`
- `xnor_Y` (Y  xnor → flop.D) high @ `[]`
- `Q` (★ Q → and4.C) **← and4.C** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
```
