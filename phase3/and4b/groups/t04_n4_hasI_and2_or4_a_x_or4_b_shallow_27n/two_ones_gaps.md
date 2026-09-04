# Two-ones open-gap sweep — t04

Group: `and2: or4_A × or4_B  [shallow(~27n)]`

Exactly **two** `I=1` pulses on FA opens: `opens[0]` and `opens[1+g]`.
`g` = number of open windows skipped between them (g=0..4).

Question: does a gap (or multiple gaps) between the first and second 1 prevent Y from sticking?
**No — gaps do not matter.** Every leaf sticks for every tested g (including multi-open gaps between the two ones).


Figure: [`two_ones_gaps_timeline.png`](two_ones_gaps_timeline.png)

## `a6.A` (`and2_2_11`)

- open: `or4_2_4==1000`
- opens: `[1, 12, 23, 34, 45, 56, 67, 78, 89, 100, 111]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{1,12}` | 11 | `—` | 13 | 120 | 1/1 | 108 | YES |
| 1 | `{1,23}` | 22 | `[12]` | 24 | 120 | 1/1 | 97 | YES |
| 2 | `{1,34}` | 33 | `[12, 23]` | 35 | 120 | 1/1 | 86 | YES |
| 3 | `{1,45}` | 44 | `[12, 23, 34]` | 46 | 120 | 1/1 | 75 | YES |
| 4 | `{1,56}` | 55 | `[12, 23, 34, 45]` | 57 | 120 | 1/1 | 64 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3, 4] — gaps do **not** matter.

## `a6.D` (`and2_2_12`)

- open: `or4_2_4==0100`
- opens: `[2, 13, 24, 35, 46, 57, 68, 79, 90, 101, 112]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{2,13}` | 11 | `—` | 14 | 120 | 1/1 | 107 | YES |
| 1 | `{2,24}` | 22 | `[13]` | 25 | 120 | 1/1 | 96 | YES |
| 2 | `{2,35}` | 33 | `[13, 24]` | 36 | 120 | 1/1 | 85 | YES |
| 3 | `{2,46}` | 44 | `[13, 24, 35]` | 47 | 120 | 1/1 | 74 | YES |
| 4 | `{2,57}` | 55 | `[13, 24, 35, 46]` | 58 | 120 | 1/1 | 63 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3, 4] — gaps do **not** matter.

## `a5.B` (`and2_2_13`)

- open: `or4_2_4==0010`
- opens: `[4, 15, 26, 37, 48, 59, 70, 81, 92, 103, 114]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{4,15}` | 11 | `—` | 16 | 120 | 1/1 | 105 | YES |
| 1 | `{4,26}` | 22 | `[15]` | 27 | 120 | 1/1 | 94 | YES |
| 2 | `{4,37}` | 33 | `[15, 26]` | 38 | 120 | 1/1 | 83 | YES |
| 3 | `{4,48}` | 44 | `[15, 26, 37]` | 49 | 120 | 1/1 | 72 | YES |
| 4 | `{4,59}` | 55 | `[15, 26, 37, 48]` | 60 | 120 | 1/1 | 61 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3, 4] — gaps do **not** matter.

## `a12.B` (`and2_2_14`)

- open: `or4_2_4==0001`
- opens: `[8, 19, 30, 41, 52, 63, 74, 85, 96, 107, 118]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{8,19}` | 11 | `—` | 20 | 120 | 1/1 | 101 | YES |
| 1 | `{8,30}` | 22 | `[19]` | 31 | 120 | 1/1 | 90 | YES |
| 2 | `{8,41}` | 33 | `[19, 30]` | 42 | 120 | 1/1 | 79 | YES |
| 3 | `{8,52}` | 44 | `[19, 30, 41]` | 53 | 120 | 1/1 | 68 | YES |
| 4 | `{8,63}` | 55 | `[19, 30, 41, 52]` | 64 | 120 | 1/1 | 57 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3, 4] — gaps do **not** matter.
