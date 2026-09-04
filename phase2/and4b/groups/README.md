# and4b expand-backs by and2 / and2b type

Expand points are the **and2 + and2b instances** grouped earlier in [`../behind/`](../behind/) — strong pin-pattern clusters, then remaining strong-group pairs / outliers.

Not the structural `join0` / `join1` / `and4b_D` banks.

Depth ≤ **5** · source [`and2_and2b_similarity.json`](../behind/and2_and2b_similarity.json)

`hasI` = fan-in reaches primary `I`; `noI` = input-independent.

| # | Size | I | Kind | Mean J | Type | Rep | Folder |
|--:|-----:|---|------|-------:|------|-----|--------|
| 1 | 7 | hasI | pin_pattern | 0.981 | `and2b: nand4_C × o21a_A1  [shallow(~27n)]` | `and2b_2_26` | [`t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/`](t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/) |
| 2 | 6 | hasI | pin_pattern | 0.994 | `and2b: nand4_C × o21a_A1  [deep(~110n)]` | `and2b_2_21` | [`t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/`](t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/) |
| 3 | 4 | hasI | pin_pattern | 1.0 | `and2: or4_A × or4_B  [deep(~110n)]` | `and2_2_4` | [`t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/`](t03_n4_hasI_and2_or4_a_x_or4_b_deep_110n/) |
| 4 | 4 | hasI | pin_pattern | 1.0 | `and2: or4_A × or4_B  [shallow(~27n)]` | `and2_2_13` | [`t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/`](t04_n4_hasI_and2_or4_a_x_or4_b_shallow_27n/) |
| 5 | 1 | hasI | strong_group_remainder | 0.952 | `strong g1 remainder (and2+and2b, size 1)` | `and2b_2_3` | [`t05_n1_hasI_strong_g1_remainder_and2_and2b/`](t05_n1_hasI_strong_g1_remainder_and2_and2b/) |
| 6 | 2 | noI | strong_group_remainder | 0.971 | `strong g4 remainder (and2+and2b, size 2)` | `and2_2_1` | [`t06_n2_noI_strong_g4_remainder_and2_and2b/`](t06_n2_noI_strong_g4_remainder_and2_and2b/) |
| 7 | 2 | noI | strong_group_remainder | 0.927 | `strong g5 remainder (and2+and2b, size 2)` | `and2_2_0` | [`t07_n2_noI_strong_g5_remainder_and2_and2b/`](t07_n2_noI_strong_g5_remainder_and2_and2b/) |
| 8 | 2 | noI | outlier | — | `outliers (not in strong type clusters)` | `and2_2_2` | [`t08_n2_noI_outliers_not_in_strong_type_clusters/`](t08_n2_noI_outliers_not_in_strong_type_clusters/) |

Regenerate:
```bash
python3 tools/expand_and4b_main_groups.py
```
