# Phase 3 — nand2b no-`I` check

Target: **`nand2b_2_23`** → out net `a32o_2_4__B2` (feeds final `a32o` pin **B2** on the success path).

## Result: PASS — does **not** reach `I`

- Cell: `nand2b_2`
- Pins: `A_N=sky130_fd_sc_hd__or2_2_11__B, B=sky130_fd_sc_hd__or2_2_11__A`
- Boolean: `Y = ¬((¬A_N) ∧ B) = A_N ∨ ¬B   →  Y=1 when A_N=1 or B=0`
- Fan-in primaries: `enable`
- Reaches `I`: **False**
- Reaches `enable`: **True**
- FA endpoints in fan-in: **5** (`a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `nor2_2_31__B`, `xor2_2_9__X`)

## Implication for sim watching

Because this nand2b does **not** depend on serial `I`, its output is a pure function of FA / enable-side state. Watching `a32o_2_4__B2` (= nand2b Y) going **high (T/1)** tells us when the FA-side condition is satisfied — independent of the bit stream.

Next: `python3 tools/phase3_watch_nand2b.py`
