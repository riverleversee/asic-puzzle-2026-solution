# `and4_2_3` input timelines (B-arm)

Structural sim. Lanes: A/B/C (flop Qs), D=`nor3_2_2.Y`, X=output.

When **X is high**, all four inputs are high that cycle.

Figure: [`and4_inputs.png`](and4_inputs.png)

CSV: [`and4_inputs.csv`](and4_inputs.csv)

## `all0`

- `and4_A` (and4.A (dfrtp_2_24.Q)) high @ `[]`
- `and4_B` (and4.B (dfrtp_2_25.Q)) high @ `[]`
- `and4_C` (and4.C (dfrtp_2_20.Q)) high @ `[]`
- `and4_D` (and4.D (nor3_2_2.Y)) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, …] (n=121)`
- `and4_X` (and4.X (output)) high @ `[]`

## `one_at_1`

- `and4_A` (and4.A (dfrtp_2_24.Q)) high @ `[]`
- `and4_B` (and4.B (dfrtp_2_25.Q)) high @ `[]`
- `and4_C` (and4.C (dfrtp_2_20.Q)) high @ `[]`
- `and4_D` (and4.D (nor3_2_2.Y)) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, …] (n=120)`
- `and4_X` (and4.X (output)) high @ `[]`

## `one_at_10`

- `and4_A` (and4.A (dfrtp_2_24.Q)) high @ `[]`
- `and4_B` (and4.B (dfrtp_2_25.Q)) high @ `[]`
- `and4_C` (and4.C (dfrtp_2_20.Q)) high @ `[]`
- `and4_D` (and4.D (nor3_2_2.Y)) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, …] (n=111)`
- `and4_X` (and4.X (output)) high @ `[]`

## `ones_1_12`

- `and4_A` (and4.A (dfrtp_2_24.Q)) high @ `[120]`
- `and4_B` (and4.B (dfrtp_2_25.Q)) high @ `[]`
- `and4_C` (and4.C (dfrtp_2_20.Q)) high @ `[]`
- `and4_D` (and4.D (nor3_2_2.Y)) high @ `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, …] (n=110)`
- `and4_X` (and4.X (output)) high @ `[]`

Parent: [`../README.md`](../README.md)

```bash
python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py
```
