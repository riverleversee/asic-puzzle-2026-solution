# Type 5 (1× · hasI): strong g1 remainder (and2+and2b, size 1)

- Kind: `strong_group_remainder`
- Source figures: [`../../../phase2/figures/and4b_main_groups/t05_n1_hasI_strong_g1_remainder_and2_and2b/`](../../../phase2/figures/and4b_main_groups/t05_n1_hasI_strong_g1_remainder_and2_and2b/)
- Representative: `and2b_2_3`

Each member is an and2/and2b sticky leaf behind and4 / and3. **FA open entry** = phase-decode net that opens the I-compare/arm window.

| Instance | Out pin | Leaf | Kind | Phase | FA open entry |
|----------|---------|------|------|-------|---------------|
| `and2b_2_3` | `and4_2_1__A` | `slot.1.A` | `set_once` | `None` | `nand4_2_1__D`==1 |

## Sim artifacts

- [`open_log.csv`](open_log.csv) — per-cycle FA-open bits (all0)
- [`open_log.md`](open_log.md) — cycles where each leaf's FA entry is open
