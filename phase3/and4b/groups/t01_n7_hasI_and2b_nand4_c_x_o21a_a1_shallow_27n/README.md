# Type 1 (7× · hasI): and2b: nand4_C × o21a_A1  [shallow(~27n)]

- Kind: `pin_pattern`
- Source figures: [`../../../phase2/figures/and4b_main_groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/`](../../../phase2/figures/and4b_main_groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/)
- Representative: `and2b_2_26`

Each member is an and2/and2b sticky leaf behind and4 / and3. **FA open entry** = phase-decode net that opens the I-compare/arm window.

| Instance | Out pin | Leaf | Kind | Phase | FA open entry |
|----------|---------|------|------|-------|---------------|
| `and2b_2_23` | `and4_2_6__B` | `a6.B` | `set_once` | `0000` | `nor4_2_1__Y`==1 |
| `and2b_2_24` | `and4_2_6__C` | `a6.C` | `set_once` | `1100` | `nand4_2_8__D`==1 |
| `and2b_2_25` | `and4_2_5__A` | `a5.A` | `set_once` | `1010` | `nand4_2_9__D`==1 |
| `and2b_2_26` | `and4_2_5__D` | `a5.D` | `set_once` | `0110` | `nand4_2_10__D`==1 |
| `and2b_2_27` | `and3_2_12__C` | `a12.C` | `set_once` | `0101` | `nand4_2_13__D`==1 |
| `and2b_2_28` | `and4_2_5__C` | `a5.C` | `set_once` | `1110` | `and4b_2_2__X`==1 |
| `and2b_2_29` | `and3_2_12__A` | `a12.A` | `set_once` | `1001` | `nand4_2_12__D`==1 |

## Sim artifacts

- [`open_log.csv`](open_log.csv) — per-cycle FA-open bits (all0)
- [`open_log.md`](open_log.md) — cycles where each leaf's FA entry is open
