# `dfrtp_2_25` — `I1_probe_timeline`

and4.B · dfrtp_2_25 · and2b_2_10

**Highlighted lane:** `Q` → **and4.B** (yellow band + ★).

Figure: [`I1_probe_timeline.png`](I1_probe_timeline.png)

CSV: [`I1_probe_timeline.csv`](I1_probe_timeline.csv)

## Observe summary

| mode | #I | Q n | first | and4.X n |
|------|---:|--------:|------:|---------:|
| `all0` | 0 | 0 | — | 0 |
| `all1` | 121 | 60 | 4 | 1 |
| `I1_cyc1` | 1 | 0 | — | 0 |
| `I1_cyc10` | 1 | 0 | — | 0 |
| `I1_cyc1_12` | 2 | 0 | — | 0 |

## Per-mode lanes

### `all0`  I=`[]`

- `A_N` (A_N  and3_2_11__X) high @ `[]`
- `B` (B  a21o_2_10__X) high @ `[]`
- `D` (D  and2b_2_10.X) high @ `[]`
- `Q` (★ Q → and4.B) **← and4.B** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

### `all1`  I=`[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, …] (n=121)`

- `A_N` (A_N  and3_2_11__X) high @ `[7, 15, 23, 31, 39, 47, 55, 63, 71, 79, 87, 95, 103, 111, 119]`
- `B` (B  a21o_2_10__X) high @ `[3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23, 27, 28, 29, 30, 31, 35, 36, 37, 38, …] (n=75)`
- `D` (D  and2b_2_10.X) high @ `[3, 4, 5, 6, 11, 12, 13, 14, 19, 20, 21, 22, 27, 28, 29, 30, 35, 36, 37, 38, 43, 44, 45, 46, …] (n=60)`
- `Q` (★ Q → and4.B) **← and4.B** high @ `[4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23, 28, 29, 30, 31, 36, 37, 38, 39, 44, 45, 46, 47, …] (n=60)`
- `and4_X` (and4.X) high @ `[22]`

### `I1_cyc1`  I=`[1]`

- `A_N` (A_N  and3_2_11__X) high @ `[]`
- `B` (B  a21o_2_10__X) high @ `[]`
- `D` (D  and2b_2_10.X) high @ `[]`
- `Q` (★ Q → and4.B) **← and4.B** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

### `I1_cyc10`  I=`[10]`

- `A_N` (A_N  and3_2_11__X) high @ `[]`
- `B` (B  a21o_2_10__X) high @ `[]`
- `D` (D  and2b_2_10.X) high @ `[]`
- `Q` (★ Q → and4.B) **← and4.B** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

### `I1_cyc1_12`  I=`[1, 12]`

- `A_N` (A_N  and3_2_11__X) high @ `[]`
- `B` (B  a21o_2_10__X) high @ `[]`
- `D` (D  and2b_2_10.X) high @ `[]`
- `Q` (★ Q → and4.B) **← and4.B** high @ `[]`
- `and4_X` (and4.X) high @ `[]`

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py
```
