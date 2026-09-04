# Three-ones open-gap sweep — t03

Group: `and2: or4_A × or4_B  [deep(~110n)]`

Exactly **three** `I=1` pulses on FA opens:
`opens[0]`, `opens[step]`, `opens[2*step]` with `step=1+g`
(g = open windows skipped between consecutive ones; g=0..4).

**Group:** All tested placements **die**.

Figure: [`three_ones_gaps_timeline.png`](three_ones_gaps_timeline.png)

## `and3.B` (`and2_2_10`)

- opens: `[5, 6, 16, 25, 26, 27, 28, 36, 47, 58, 66, 67, 68, 69, 70, 71, 77, 88, 99, 100, 110]`

| g | step | I@ | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|-----:|----|---------:|-------:|----------:|-------:|:-------:|
| 0 | 1 | `[5, 6, 16]` | 7 | 16 | 1/0 | 10 | no |
| 1 | 2 | `[5, 16, 26]` | 17 | 26 | 1/0 | 10 | no |
| 2 | 3 | `[5, 25, 28]` | 26 | 28 | 1/0 | 3 | no |
| 3 | 4 | `[5, 26, 47]` | 27 | 47 | 1/0 | 21 | no |
| 4 | 5 | `[5, 27, 66]` | 28 | 66 | 1/0 | 39 | no |

**Verdict:** dies for all g∈[0, 1, 2, 3, 4]

## `slot.0.A` (`and2_2_3`)

- opens: `[37, 38, 39, 48, 59, 60, 61, 72, 81, 82, 83]`

| g | step | I@ | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|-----:|----|---------:|-------:|----------:|-------:|:-------:|
| 0 | 1 | `[37, 38, 39]` | 39 | 39 | 1/0 | 1 | no |
| 1 | 2 | `[37, 39, 59]` | 40 | 59 | 1/0 | 20 | no |
| 2 | 3 | `[37, 48, 61]` | 49 | 61 | 1/0 | 13 | no |
| 3 | 4 | `[37, 59, 81]` | 60 | 81 | 1/0 | 22 | no |
| 4 | 5 | `[37, 60, 83]` | 61 | 83 | 1/0 | 23 | no |

**Verdict:** dies for all g∈[0, 1, 2, 3, 4]

## `slot.1.B` (`and2_2_4`)

- opens: `[8, 9, 19, 20, 31]`

| g | step | I@ | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|-----:|----|---------:|-------:|----------:|-------:|:-------:|
| 0 | 1 | `[8, 9, 19]` | 10 | 19 | 1/0 | 10 | no |
| 1 | 2 | `[8, 19, 31]` | 20 | 31 | 1/0 | 12 | no |

**Verdict:** dies for all g∈[0, 1]

## `slot.0.D` (`and2_2_5`)

- opens: `[63, 64, 65, 74, 85, 96, 107, 108, 109]`

| g | step | I@ | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|-----:|----|---------:|-------:|----------:|-------:|:-------:|
| 0 | 1 | `[63, 64, 65]` | 65 | 65 | 1/0 | 1 | no |
| 1 | 2 | `[63, 65, 85]` | 66 | 85 | 1/0 | 20 | no |
| 2 | 3 | `[63, 74, 107]` | 75 | 107 | 1/0 | 33 | no |
| 3 | 4 | `[63, 85, 109]` | 86 | 109 | 1/0 | 24 | no |

**Verdict:** dies for all g∈[0, 1, 2, 3]
