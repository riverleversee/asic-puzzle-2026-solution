# Complex operator matching (success groupings)

Database: `complex_operators_db.json` · Results: `operator_matches.json`

Source: `rework/netlist/puzzle_structural.v` (from trusted `puzzle_gates.spice`). OG cells are expanded.

## Ranking

| Score | Group | Nodes | Best operator | Width / components |
|---:|---|---:|---|---|
| 1.000 | `G_hold_B2` | 37 | Serial bit gather + parallel check | arith ~2-bit via fa_pairs (FA=2, xor=2, xnor=1, carry_len=2) |
| 0.985 | `G_set_inv` | 66 | Shift register / serial-in parallel-out | arith ~2-bit via fa_pairs (FA=2, xor=2, xnor=1, carry_len=3) |
| 0.959 | `G_status_A` | 34 | LFSR / CRC / linear feedback | arith ~2-bit via fa_pairs (FA=2, xor=2, xnor=1, carry_len=2) |
| 0.942 | `G_status_B` | 36 | LFSR / CRC / linear feedback | arith ~2-bit via fa_pairs (FA=2, xor=2, xnor=1, carry_len=2) |
| 0.942 | `C_status_A_plus_B` | 36 | LFSR / CRC / linear feedback | arith ~2-bit via fa_pairs (FA=2, xor=2, xnor=1, carry_len=2) |
| 0.937 | `G_set_and2` | 82 | Serial bit gather + parallel check | arith ~2-bit via fa_pairs (FA=2, xor=3, xnor=2, carry_len=2); AND-reduce width≈5 (flops=4, stubs=0) |
| 0.876 | `G_main_check` | 281 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=11, xnor=11, carry_len=5); AND-reduce width≈22 (flops=22, stubs=0) |
| 0.876 | `C_and4b_all_inputs` | 283 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=11, xnor=11, carry_len=5); AND-reduce width≈22 (flops=22, stubs=0) |
| 0.876 | `C_main_plus_statusA` | 281 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=11, xnor=11, carry_len=5); AND-reduce width≈22 (flops=22, stubs=0) |
| 0.842 | `G_and4b_join` | 384 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=11, xnor=11, carry_len=5); AND-reduce width≈46 (flops=46, stubs=0) |
| 0.834 | `G_success_glue` | 466 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=12, xnor=12, carry_len=5); AND-reduce width≈53 (flops=51, stubs=0) |
| 0.834 | `C_full_set_path` | 464 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=12, xnor=12, carry_len=5); AND-reduce width≈46 (flops=46, stubs=0) |
| 0.834 | `C_set_plus_hold` | 465 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=12, xnor=12, carry_len=5); AND-reduce width≈46 (flops=46, stubs=0) |
| 0.834 | `C_entire_a32o` | 466 | Binary adder (ripple / FA chain) | arith ~7-bit via fa_pairs (FA=7, xor=12, xnor=12, carry_len=5); AND-reduce width≈53 (flops=51, stubs=0) |

## Granular structure (strong matches)

### `G_hold_B2` → Serial bit gather + parallel check (1.000)

- **Cell mix:** `{'flop': 10, 'mux': 1, 'xor': 2, 'xnor': 1, 'aoi': 9, 'and_nand': 10}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~2-bit** (`fa_pairs`); FA-like pairs=2, xor=2, xnor=1, aoi=9, carry-AOI chain=2
- **AND-reduce:** 2 leaves (2 flops, 0 stubs)

### `G_set_inv` → Shift register / serial-in parallel-out (0.985)

- **Cell mix:** `{'flop': 22, 'mux': 13, 'xor': 2, 'xnor': 1, 'aoi': 12, 'and_nand': 9}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~2-bit** (`fa_pairs`); FA-like pairs=2, xor=2, xnor=1, aoi=12, carry-AOI chain=3
- **AND-reduce:** 1 leaves (1 flops, 0 stubs)

### `G_status_A` → LFSR / CRC / linear feedback (0.959)

- **Cell mix:** `{'flop': 9, 'mux': 1, 'xor': 2, 'xnor': 1, 'aoi': 9, 'and_nand': 9}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~2-bit** (`fa_pairs`); FA-like pairs=2, xor=2, xnor=1, aoi=9, carry-AOI chain=2
- **AND-reduce:** 1 leaves (0 flops, 0 stubs)

### `G_status_B` → LFSR / CRC / linear feedback (0.942)

- **Cell mix:** `{'flop': 10, 'mux': 1, 'xor': 2, 'xnor': 1, 'aoi': 9, 'and_nand': 9}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~2-bit** (`fa_pairs`); FA-like pairs=2, xor=2, xnor=1, aoi=9, carry-AOI chain=2
- **AND-reduce:** 1 leaves (0 flops, 0 stubs)

### `C_status_A_plus_B` → LFSR / CRC / linear feedback (0.942)

- **Cell mix:** `{'flop': 10, 'mux': 1, 'xor': 2, 'xnor': 1, 'aoi': 9, 'and_nand': 9}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~2-bit** (`fa_pairs`); FA-like pairs=2, xor=2, xnor=1, aoi=9, carry-AOI chain=2
- **AND-reduce:** 1 leaves (0 flops, 0 stubs)

### `G_set_and2` → Serial bit gather + parallel check (0.937)

- **Cell mix:** `{'flop': 20, 'mux': 3, 'xor': 3, 'xnor': 2, 'aoi': 20, 'and_nand': 22}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~2-bit** (`fa_pairs`); FA-like pairs=2, xor=3, xnor=2, aoi=20, carry-AOI chain=2
- **AND-reduce:** 5 leaves (4 flops, 0 stubs)

### `G_main_check` → Binary adder (ripple / FA chain) (0.876)

- **Cell mix:** `{'flop': 31, 'mux': 6, 'xor': 11, 'xnor': 11, 'aoi': 82, 'and_nand': 79}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=11, xnor=11, aoi=82, carry-AOI chain=5
- **AND-reduce:** 22 leaves (22 flops, 0 stubs)

### `C_and4b_all_inputs` → Binary adder (ripple / FA chain) (0.876)

- **Cell mix:** `{'flop': 32, 'mux': 6, 'xor': 11, 'xnor': 11, 'aoi': 82, 'and_nand': 79}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=11, xnor=11, aoi=82, carry-AOI chain=5
- **AND-reduce:** 22 leaves (22 flops, 0 stubs)

### `C_main_plus_statusA` → Binary adder (ripple / FA chain) (0.876)

- **Cell mix:** `{'flop': 31, 'mux': 6, 'xor': 11, 'xnor': 11, 'aoi': 82, 'and_nand': 79}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=11, xnor=11, aoi=82, carry-AOI chain=5
- **AND-reduce:** 22 leaves (22 flops, 0 stubs)

### `G_and4b_join` → Binary adder (ripple / FA chain) (0.842)

- **Cell mix:** `{'flop': 54, 'mux': 6, 'xor': 11, 'xnor': 11, 'aoi': 104, 'and_nand': 119}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=11, xnor=11, aoi=104, carry-AOI chain=5
- **AND-reduce:** 46 leaves (46 flops, 0 stubs)

### `G_success_glue` → Binary adder (ripple / FA chain) (0.834)

- **Cell mix:** `{'flop': 78, 'mux': 20, 'xor': 12, 'xnor': 12, 'aoi': 119, 'and_nand': 133}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=12, xnor=12, aoi=119, carry-AOI chain=5
- **AND-reduce:** 53 leaves (51 flops, 0 stubs)

### `C_full_set_path` → Binary adder (ripple / FA chain) (0.834)

- **Cell mix:** `{'flop': 78, 'mux': 20, 'xor': 12, 'xnor': 12, 'aoi': 118, 'and_nand': 132}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=12, xnor=12, aoi=118, carry-AOI chain=5
- **AND-reduce:** 46 leaves (46 flops, 0 stubs)

### `C_set_plus_hold` → Binary adder (ripple / FA chain) (0.834)

- **Cell mix:** `{'flop': 78, 'mux': 20, 'xor': 12, 'xnor': 12, 'aoi': 118, 'and_nand': 133}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=12, xnor=12, aoi=118, carry-AOI chain=5
- **AND-reduce:** 46 leaves (46 flops, 0 stubs)

### `C_entire_a32o` → Binary adder (ripple / FA chain) (0.834)

- **Cell mix:** `{'flop': 78, 'mux': 20, 'xor': 12, 'xnor': 12, 'aoi': 119, 'and_nand': 133}`
- **Shifter:** no mux-hold bank detected
- **Adder/compare:** est **~7-bit** (`fa_pairs`); FA-like pairs=7, xor=12, xnor=12, aoi=119, carry-AOI chain=5
- **AND-reduce:** 53 leaves (51 flops, 0 stubs)

## Operators in the database

- **Equality / constant comparator** (`equality_comparator`): Bitwise XNOR (or EQ) feeding a wide AND-reduce to 1 bit.
- **Binary adder (ripple / FA chain)** (`ripple_adder`): Per-bit XOR for sum + majority/AOI for carry (a21o/o21a/maj).
- **Parity / XOR-tree** (`parity_xor_tree`): Mostly XOR/XNOR cascaded to one bit.
- **Shift register / serial-in parallel-out** (`shift_register`): Flop chain with mux or enable; serial bit + enable.
- **LFSR / CRC / linear feedback** (`lfsr_crc`): Shift flops with XOR feedback taps.
- **Sticky set / SR-style status** (`sticky_sr_latch`): Flop with OR-self hold (set-and-stay) or A|B delayed sticky.
- **Wide AND-reduce / all-ones check** (`wide_and_reduce`): Tree of AND/NAND reducing many bits to one.
- **Wide OR-reduce / any-ones check** (`wide_or_reduce`): 
- **MUX tree / datapath select** (`mux_tree`): 
- **One-hot / priority / thermometer decode** (`onehot_priority`): NOR/NAND chains with mutual exclusion flavor.
- **Population count / adder tree of bits** (`popcount`): 
- **FSM / control decode** (`fsm_control`): Mixed AOI with modest flops; not XOR-heavy.
- **Serial bit gather + parallel check** (`serial_deserializer`): Shift/flops gathering I, then AND/XNOR check — warmup shape.

## How to read scores

- **≥ 0.70** — strong structural match
- **0.55–0.70** — plausible
- **0.45–0.55** — weak / partial
- **< 0.45** — unlikely

## Width heuristics

- **Shifter bits:** length of mux-hold flop chain (hold=`Q`, shift=`prev`), plus a no-mux head flop when its Q is the bank serial_in.
- **Adder bits:** count of XOR↔AOI pairs sharing ≥2 inputs (FA-like); fallback to xor/xnor counts when FA pairing is sparse.
- **AND-reduce width:** leaf fan-in of the group root through AND/NAND/INV only.
