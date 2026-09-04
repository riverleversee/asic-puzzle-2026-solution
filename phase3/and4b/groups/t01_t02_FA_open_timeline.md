# FA open timeline — t01 + t02

Image: [`t01_t02_FA_open_timeline.png`](t01_t02_FA_open_timeline.png)

Watches the **FA phase-decode open entry** for each sticky leaf in the first two I-dependent and2b groups (when that gate is open for an `I` compare/arm).

- Sim vs `opens_exact_shift1.json` all0: **PASS**
- Group folders: [`and4_I_groups/`](and4_I_groups/)

| Group | Leaf | Instance | FA open entry | #opens |
|------:|------|----------|---------------|-------:|
| t01 | `a6.B` | `and2b_2_23` | `nor4_2_1__Y` | 11 |
| t01 | `a6.C` | `and2b_2_24` | `nand4_2_8__D` | 11 |
| t01 | `a5.A` | `and2b_2_25` | `nand4_2_9__D` | 11 |
| t01 | `a5.D` | `and2b_2_26` | `nand4_2_10__D` | 11 |
| t01 | `a12.C` | `and2b_2_27` | `nand4_2_13__D` | 11 |
| t01 | `a5.C` | `and2b_2_28` | `and4b_2_2__X` | 11 |
| t01 | `a12.A` | `and2b_2_29` | `nand4_2_12__D` | 11 |
| t02 | `slot.0.B` | `and2b_2_1` | `nor4_2_0__Y` | 8 |
| t02 | `slot.0.C` | `and2b_2_2` | `nand4_2_3__D` | 4 |
| t02 | `slot.1.C` | `and2b_2_20` | `nand4_2_5__D` | 8 |
| t02 | `and3.C` | `and2b_2_21` | `nand4_2_6__D` | 6 |
| t02 | `and3.A` | `and2b_2_22` | `nand4_2_4__D` | 28 |
| t02 | `slot.1.D` | `and2b_2_4` | `nand4_2_2__D` | 14 |
