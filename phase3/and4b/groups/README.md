# or4b + and2b→nand2(I) path (t03 / t04)

## Run scripts (this folder)

```bash
python3 phase3/sticky_or_and2/run_opens.py
python3 phase3/sticky_or_and2/run_fa_input.py
python3 phase3/sticky_or_and2/run_flop_init.py
```

Also: [`flop_init_all0/`](flop_init_all0/) — all flop Q @ all0 (used for this FA/nand path).

Timelines separate:
- **or4b → or4.C** (raw C=1)
- **leaf OPEN** windows
- **and2b_2_11 Y** = `inv_2_7__A` → nand2.B
- **and2b_2_11 A_N** = `or2_2_11__A` (FA input, I-independent, 0 on all0/all1)

| # | Folder | Timeline |
|--:|--------|----------|
| 3 | [`t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/) | [`FA_open_timeline.png`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/FA_open_timeline.png) |
| 4 | [`t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/) | [`FA_open_timeline.png`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/FA_open_timeline.png) |

## k-ones flop timelines

Sweep `I=1` on the first k FA-open cycles (k=1..5); watch A_N/B/Y (and2b) or A/B/Y (and2).

```bash
python3 phase3/and4b/groups/run_k_ones.py
python3 phase3/and4b/groups/run_k_ones.py --groups 3 4 --k-max 5
```

- t03: [`t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/k_ones_flops_timeline.png`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/k_ones_flops_timeline.png)
- t04: [`t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/k_ones_flops_timeline.png`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/k_ones_flops_timeline.png)

## Two-ones open-gap sweep (t03/t04)

Exactly two `I=1` on `opens[0]` and `opens[1+g]`; ask if skipped open windows between them block PASS.

```bash
python3 phase3/and4b/groups/run_two_ones_gaps.py --gap-max 4
```

- t03: [`t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/two_ones_gaps.md`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/two_ones_gaps.md) · [`t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/two_ones_gaps_timeline.png`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/two_ones_gaps_timeline.png)
- t04: [`t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/two_ones_gaps.md`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/two_ones_gaps.md) · [`t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/two_ones_gaps_timeline.png`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/two_ones_gaps_timeline.png)

## Three-ones gaps + late two-ones (t03/t04)

- **three**: `opens[0], opens[step], opens[2*step]`, `step=1+g`
- **late two**: `opens[s], opens[s+1+g]` with `s≥1`

```bash
python3 phase3/and4b/groups/run_ones_gap_variants.py --gap-max 4 --start-max 3
```

- t03: [`t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/three_ones_gaps.md`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/three_ones_gaps.md) · [`t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/two_ones_late.md`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/two_ones_late.md)
- t04: [`t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/three_ones_gaps.md`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/three_ones_gaps.md) · [`t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/two_ones_late.md`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/two_ones_late.md)

## Confirmed I-ones rules

Per-leaf hard rule for all hasI groups t01–t05: **exactly two** `I=1` on that leaf’s FA opens.

- Index: [`rules/README.txt`](rules/README.txt)
- set_once t01/t02/t05: [`rules/and2b_set_once_t01_t02_t05.txt`](rules/and2b_set_once_t01_t02_t05.txt)
- sticky_or t03/t04: [`rules/and2_sticky_or_t03_t04.txt`](rules/and2_sticky_or_t03_t04.txt)

