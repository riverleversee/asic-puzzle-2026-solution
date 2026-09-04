# Strong-group back-trees (depth ≤ 5)

Source: [`../and2_and2b_similarity.json`](../and2_and2b_similarity.json)
**5** strong groups · fan-in behind each and2/and2b output.

`hasI` = fan-in reaches primary `I`; `noI` = input-independent.

| Group | Size | I | Families | Mean J | Representative | Rep figure | All members |
|------:|-----:|---|----------|-------:|----------------|------------|-------------|
| 1 | 11 | hasI | and2+and2b | 0.952 | `and2b_2_2` | [`g01_rep_and2b_2_2_fanin_depth5.png`](g01_rep_and2b_2_2_fanin_depth5.png) | [`g01_n11_hasI/`](g01_n11_hasI/) |
| 2 | 7 | hasI | and2b | 0.981 | `and2b_2_26` | [`g02_rep_and2b_2_26_fanin_depth5.png`](g02_rep_and2b_2_26_fanin_depth5.png) | [`g02_n7_hasI/`](g02_n7_hasI/) |
| 3 | 4 | hasI | and2 | 1.0 | `and2_2_13` | [`g03_rep_and2_2_13_fanin_depth5.png`](g03_rep_and2_2_13_fanin_depth5.png) | [`g03_n4_hasI/`](g03_n4_hasI/) |
| 4 | 2 | noI | and2+and2b | 0.971 | `and2_2_1` | [`g04_rep_and2_2_1_fanin_depth5.png`](g04_rep_and2_2_1_fanin_depth5.png) | [`g04_n2_noI/`](g04_n2_noI/) |
| 5 | 2 | noI | and2+and2b | 0.927 | `and2_2_0` | [`g05_rep_and2_2_0_fanin_depth5.png`](g05_rep_and2_2_0_fanin_depth5.png) | [`g05_n2_noI/`](g05_n2_noI/) |

Generated with `tools/render_strong_group_backtrees.py --depth 5`.
