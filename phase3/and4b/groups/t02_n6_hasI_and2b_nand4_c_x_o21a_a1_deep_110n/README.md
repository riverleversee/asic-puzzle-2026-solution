# Type 2 (6× · hasI): and2b: nand4_C × o21a_A1  [deep(~110n)]

- Kind: `pin_pattern`
- Source figures: [`../../../phase2/figures/and4b_main_groups/t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/`](../../../phase2/figures/and4b_main_groups/t02_n6_hasI_and2b_nand4_c_x_o21a_a1_deep_110n/)
- Representative: `and2b_2_21`

Each member is an and2/and2b sticky leaf behind and4 / and3. **FA open entry** = phase-decode net that opens the I-compare/arm window.

| Instance | Out pin | Leaf | Kind | Phase | FA open entry |
|----------|---------|------|------|-------|---------------|
| `and2b_2_1` | `and4_2_0__B` | `slot.0.B` | `set_once` | `None` | `nor4_2_0__Y`==1 |
| `and2b_2_2` | `and4_2_0__C` | `slot.0.C` | `set_once` | `None` | `nand4_2_3__D`==1 |
| `and2b_2_20` | `and4_2_1__C` | `slot.1.C` | `set_once` | `None` | `nand4_2_5__D`==1 |
| `and2b_2_21` | `and3_2_5__C` | `and3.C` | `set_once` | `None` | `nand4_2_6__D`==1 |
| `and2b_2_22` | `and3_2_5__A` | `and3.A` | `set_once` | `None` | `nand4_2_4__D`==1 |
| `and2b_2_4` | `and4_2_1__D` | `slot.1.D` | `set_once` | `None` | `nand4_2_2__D`==1 |

## Sim artifacts

- [`open_log.csv`](open_log.csv) — per-cycle FA-open bits (all0)
- [`open_log.md`](open_log.md) — cycles where each leaf's FA entry is open
