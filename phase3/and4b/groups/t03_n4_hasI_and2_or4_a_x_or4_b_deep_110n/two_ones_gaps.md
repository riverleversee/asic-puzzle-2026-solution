# Two-ones open-gap sweep — t03

Group: `and2: or4_A × or4_B  [deep(~110n)]`

Exactly **two** `I=1` pulses on FA opens: `opens[0]` and `opens[1+g]`.
`g` = number of open windows skipped between them (g=0..4).

Question: does a gap (or multiple gaps) between the first and second 1 prevent Y from sticking?
**No — gaps do not matter.** Every leaf sticks for every tested g (including multi-open gaps between the two ones).


Figure: [`two_ones_gaps_timeline.png`](two_ones_gaps_timeline.png)

## `and3.B` (`and2_2_10`)

- open: `or4_2_5__C`
- opens: `[5, 6, 16, 25, 26, 27, 28, 36, 47, 58, 66, 67, 68, 69, 70, 71, 77, 88, 99, 100, 110]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{5,6}` | 1 | `—` | 7 | 120 | 1/1 | 114 | YES |
| 1 | `{5,16}` | 11 | `[6]` | 17 | 120 | 1/1 | 104 | YES |
| 2 | `{5,25}` | 20 | `[6, 16]` | 26 | 120 | 1/1 | 95 | YES |
| 3 | `{5,26}` | 21 | `[6, 16, 25]` | 27 | 120 | 1/1 | 94 | YES |
| 4 | `{5,27}` | 22 | `[6, 16, 25, 26]` | 28 | 120 | 1/1 | 93 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3, 4] — gaps do **not** matter.

## `slot.0.A` (`and2_2_3`)

- open: `or4_2_1__C`
- opens: `[37, 38, 39, 48, 59, 60, 61, 72, 81, 82, 83]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{37,38}` | 1 | `—` | 39 | 120 | 1/1 | 82 | YES |
| 1 | `{37,39}` | 2 | `[38]` | 40 | 120 | 1/1 | 81 | YES |
| 2 | `{37,48}` | 11 | `[38, 39]` | 49 | 120 | 1/1 | 72 | YES |
| 3 | `{37,59}` | 22 | `[38, 39, 48]` | 60 | 120 | 1/1 | 61 | YES |
| 4 | `{37,60}` | 23 | `[38, 39, 48, 59]` | 61 | 120 | 1/1 | 60 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3, 4] — gaps do **not** matter.

## `slot.1.B` (`and2_2_4`)

- open: `or4_2_2__C`
- opens: `[8, 9, 19, 20, 31]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{8,9}` | 1 | `—` | 10 | 120 | 1/1 | 111 | YES |
| 1 | `{8,19}` | 11 | `[9]` | 20 | 120 | 1/1 | 101 | YES |
| 2 | `{8,20}` | 12 | `[9, 19]` | 21 | 120 | 1/1 | 100 | YES |
| 3 | `{8,31}` | 23 | `[9, 19, 20]` | 32 | 120 | 1/1 | 89 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3] — gaps do **not** matter.

## `slot.0.D` (`and2_2_5`)

- open: `or4_2_3__C`
- opens: `[63, 64, 65, 74, 85, 96, 107, 108, 109]`

| g | I@ | Δcyc | skipped opens | Y first↑ | Y last | A/B final | Y high | sticks? |
|--:|----|-----:|---------------|---------:|-------:|----------:|-------:|:-------:|
| 0 | `{63,64}` | 1 | `—` | 65 | 120 | 1/1 | 56 | YES |
| 1 | `{63,65}` | 2 | `[64]` | 66 | 120 | 1/1 | 55 | YES |
| 2 | `{63,74}` | 11 | `[64, 65]` | 75 | 120 | 1/1 | 46 | YES |
| 3 | `{63,85}` | 22 | `[64, 65, 74]` | 86 | 120 | 1/1 | 35 | YES |
| 4 | `{63,96}` | 33 | `[64, 65, 74, 85]` | 97 | 120 | 1/1 | 24 | YES |

**Verdict:** Y sticks for **all** tested gaps g∈[0, 1, 2, 3, 4] — gaps do **not** matter.
