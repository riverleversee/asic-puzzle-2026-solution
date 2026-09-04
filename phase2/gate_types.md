# Sky130 gate types used in the success cone

Reference for reading the phase-2 logic diagrams. Cell names look like
`sky130_fd_sc_hd__a32o_2` — the useful part is the **family** (`a32o`) and drive
strength (`_2`). Formulas match `tools/pdk_cell_formulas.py` (truth-table checked
against the PDK).

## Naming conventions

| Pattern | Meaning |
|---------|---------|
| `and` / `or` / `nand` / `nor` / `xor` / `xnor` / `inv` / `mux` | Basic Boolean / select |
| trailing `i` | Output is **inverted** (NAND-style) |
| trailing `b` / `bb` on a pin family | One / two inputs are **active-low** (`A_N`) |
| `a…o` | **AND-OR**: AND groups OR’d together (e.g. `a32o`) |
| `o…a` | **OR-AND**: OR groups AND’d together (e.g. `o21a`) |
| `maj3` | Majority of 3 inputs |
| `dfrtp` / `dfxtp` | Flip-flop (sequential) |

Compound digit codes (sky130 style):

- `a32o` → AND3 of `(A1,A2,A3)` **OR** AND2 of `(B1,B2)` → `(A1∧A2∧A3) ∨ (B1∧B2)`
- `o21a` → OR2 of `(A1,A2)` **AND** `B1` → `(A1∨A2) ∧ B1`
- `a21oi` → same as `a21o` then invert the output

## Primaries (ports)

| Name | Role |
|------|------|
| `I` | Serial data input bit |
| `clk` | Clock (not expanded in diagrams) |
| `enable` | Chip enable into control logic |
| `rst_n` | Active-low reset into flops |
| `success` | Latched success flag (flop Q) |

## Sequential

| Family | Operation |
|--------|-----------|
| `dfrtp` | Positive-edge D flip-flop with async active-low reset. On reset: Q←0; else Q←D. |
| `dfxtp` | Positive-edge D flip-flop (no reset pin in the usual form). Q←D. |

## Buffers / inverters

| Family | Pins | Operation |
|--------|------|-----------|
| `inv` | A → Y | Y = ¬A |
| `buf` | A → X | X = A |
| `clkbuf` | A → X | X = A (clock buffer) |

## AND / NAND / OR / NOR

| Family | Operation |
|--------|-----------|
| `and2` | A ∧ B |
| `and3` | A ∧ B ∧ C |
| `and4` | A ∧ B ∧ C ∧ D |
| `and2b` | (¬A_N) ∧ B |
| `and3b` | (¬A_N) ∧ B ∧ C |
| `and4b` | (¬A_N) ∧ B ∧ C ∧ D |
| `and4bb` | (¬A_N) ∧ (¬B_N) ∧ C ∧ D |
| `nand2` | ¬(A ∧ B) |
| `nand3` | ¬(A ∧ B ∧ C) |
| `nand4` | ¬(A ∧ B ∧ C ∧ D) |
| `nand2b` | ¬((¬A_N) ∧ B) |
| `nand3b` | ¬((¬A_N) ∧ B ∧ C) |
| `nand4b` | ¬((¬A_N) ∧ B ∧ C ∧ D) |
| `nand4bb` | ¬((¬A_N) ∧ (¬B_N) ∧ C ∧ D) |
| `or2` | A ∨ B |
| `or3` | A ∨ B ∨ C |
| `or4` | A ∨ B ∨ C ∨ D |
| `or2b` | A ∨ (¬B_N) |
| `or3b` | A ∨ B ∨ (¬C_N) |
| `or4b` | A ∨ B ∨ C ∨ (¬D_N) |
| `or4bb` | A ∨ B ∨ (¬C_N) ∨ (¬D_N) |
| `nor2` | ¬(A ∨ B) |
| `nor3` | ¬(A ∨ B ∨ C) |
| `nor4` | ¬(A ∨ B ∨ C ∨ D) |
| `nor2b` | ¬(A ∨ (¬B_N)) |
| `nor3b` | ¬(A ∨ B ∨ (¬C_N)) |
| `nor4b` | ¬(A ∨ B ∨ C ∨ (¬D_N)) |

## XOR / XNOR / MUX / majority

| Family | Operation |
|--------|-----------|
| `xor2` | A ⊕ B |
| `xnor2` | ¬(A ⊕ B) |
| `xor3` | A ⊕ B ⊕ C |
| `mux2` | S ? A1 : A0 |
| `mux2i` | ¬(S ? A1 : A0) |
| `mux4` | select among A0…A3 with {S1,S0} |
| `maj3` | 1 if at least two of {A,B,C} are 1 |

## AND-OR compounds (`a*o` / `a*oi`)

| Family | Operation |
|--------|-----------|
| `a21o` | (A1 ∧ A2) ∨ B1 |
| `a21oi` | ¬((A1 ∧ A2) ∨ B1) |
| `a22o` | (A1 ∧ A2) ∨ (B1 ∧ B2) |
| `a22oi` | ¬((A1 ∧ A2) ∨ (B1 ∧ B2)) |
| `a31o` | (A1 ∧ A2 ∧ A3) ∨ B1 |
| `a31oi` | ¬((A1 ∧ A2 ∧ A3) ∨ B1) |
| `a32o` | (A1 ∧ A2 ∧ A3) ∨ (B1 ∧ B2) |
| `a41o` | (A1 ∧ A2 ∧ A3 ∧ A4) ∨ B1 |
| `a41oi` | ¬((A1 ∧ A2 ∧ A3 ∧ A4) ∨ B1) |
| `a211o` | (A1 ∧ A2) ∨ B1 ∨ C1 |
| `a211oi` | ¬((A1 ∧ A2) ∨ B1 ∨ C1) |
| `a221o` | (A1 ∧ A2) ∨ (B1 ∧ B2) ∨ C1 |
| `a221oi` | ¬((A1 ∧ A2) ∨ (B1 ∧ B2) ∨ C1) |
| `a222o` | (A1 ∧ A2) ∨ (B1 ∧ B2) ∨ (C1 ∧ C2) |
| `a311o` | (A1 ∧ A2 ∧ A3) ∨ B1 ∨ C1 |
| `a2111o` | (A1 ∧ A2) ∨ B1 ∨ C1 ∨ D1 |
| `a2111oi` | ¬((A1 ∧ A2) ∨ B1 ∨ C1 ∨ D1) |
| `a21bo` | (A1 ∧ A2) ∨ (¬B1_N) |
| `a21boi` | ¬((A1 ∧ A2) ∨ (¬B1_N)) |
| `a2bb2o` | ((¬A1_N) ∧ (¬A2_N)) ∨ (B1 ∧ B2) |

## OR-AND compounds (`o*a` / `o*ai`)

| Family | Operation |
|--------|-----------|
| `o21a` | (A1 ∨ A2) ∧ B1 |
| `o21ai` | ¬((A1 ∨ A2) ∧ B1) |
| `o22a` | (A1 ∨ A2) ∧ (B1 ∨ B2) |
| `o22ai` | ¬((A1 ∨ A2) ∧ (B1 ∨ B2)) |
| `o31a` | (A1 ∨ A2 ∨ A3) ∧ B1 |
| `o31ai` | ¬((A1 ∨ A2 ∨ A3) ∧ B1) |
| `o32a` | (A1 ∨ A2 ∨ A3) ∧ (B1 ∨ B2) |
| `o32ai` | ¬((A1 ∨ A2 ∨ A3) ∧ (B1 ∨ B2)) |
| `o211a` | (A1 ∨ A2) ∧ B1 ∧ C1 |
| `o211ai` | ¬((A1 ∨ A2) ∧ B1 ∧ C1) |
| `o221a` | (A1 ∨ A2) ∧ (B1 ∨ B2) ∧ C1 |
| `o311a` | (A1 ∨ A2 ∨ A3) ∧ B1 ∧ C1 |
| `o2111a` | (A1 ∨ A2) ∧ B1 ∧ C1 ∧ D1 |
| `o21ba` | (A1 ∨ A2) ∧ (¬B1_N) |
| `o21bai` | ¬((A1 ∨ A2) ∧ (¬B1_N)) |
| `o2bb2a` | (¬(A1_N ∧ A2_N)) ∧ (B1 ∨ B2) |
| `o2bb2ai` | ¬((¬(A1_N ∧ A2_N)) ∧ (B1 ∨ B2)) |

## Diagram color classes

Logic diagrams color borders by coarse class (not every family gets its own color):

| Class | Families (examples) |
|-------|---------------------|
| flop | `dfrtp`, `dfxtp` |
| and / nand | `and*`, `nand*` |
| or / nor | `or*`, `nor*` |
| xor / xnor | `xor*`, `xnor*` |
| aoi | `a*o`, `o*a`, `maj3`, and inverted variants |
| mux | `mux2`, `mux2i`, `mux4` |
| inv / buf | `inv`, `buf`, `clkbuf` |
| primary | `I`, `enable`, `success`, … |

## Reading AO/OA and depth cuts

- **AO/OA boxes** show the Boolean formula under the cell family (e.g. `a32o` → `(A1∧A2∧A3)∨(B1∧B2)`).
- **Edges into AO/OA** are labeled with the destination pin (`A1`, `B2`, …) and colored by pin group (A / B / C / D).
- **Depth-cut** boxes (leftmost / truncated) are tagged when their *deeper* fan-in reaches:
  - an identified **FA** sum/carry endpoint (`→FA`), and/or
  - primary **`I`** (`→I`).
- FA endpoints come from `tools/identify_fa_endpoints.py` (XOR/XNOR paired with AO/OA/maj sharing ≥2 inputs). See `fa_endpoints.md`.
- **Layout:** layers are ordered pin-aware from the root, then barycentric + parent-block clustering (gaps between sibling groups) to cut crossings.
- **Back-edges** (a shallower net also drives a deeper-shown gate): dashed crimson arcs labeled `↩ pin`, distinct from solid forward edges.

## Source note

Phase-2 fan-in figures use **`rework/netlist/puzzle_structural.v`**,
built from Magic `puzzle_gates.spice` via `spice_to_structural_verilog.py`.
OG cells are ordinary driven instances — there are no `stub_og_*` placeholders.

Do **not** use `puzzle_core.v` / `puzzle_success_cone.v` (old behavioral path) for rework.
