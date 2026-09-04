# Flip-flop initial state — all0

```bash
python3 phase3/and4b/groups/flop_init_all0/run_flop_init.py
```

Icarus structural sim: reset low → release → `enable=1`, **I=0** every cycle.
Sample: after each posedge `#1` (same harness as other phase3 watches).

- Flops probed: **92**
- Q at cycle 0: **88** low, **4** high
- Full trace: [`flop_Q_all0.csv`](flop_Q_all0.csv)
- Figure (first 32 cycles): [`flop_init_timeline.png`](flop_init_timeline.png)

## Cycle-0 (initial after enable)

| Instance | Q net | D | Q@0 | first Δ | #high/121 |
|----------|-------|---|----:|--------:|----------:|
| `dfrtp_2_0` | `nand4_2_0__C` | `o21a_2_4__X` | 0 | None | 0 |
| `dfrtp_2_1` | `inv_2_1__A` | `o21a_2_7__X` | 0 | None | 0 |
| `dfrtp_2_10` | `o21a_2_30__A1` | `nand2b_2_4__Y` | 0 | None | 0 |
| `dfrtp_2_11` | `and2b_2_3__B` | `nand2b_2_2__Y` | 0 | None | 0 |
| `dfrtp_2_12` | `o21a_2_8__A1` | `nand2b_2_3__Y` | 0 | None | 0 |
| `dfrtp_2_13` | `or4_2_2__A` | `a21o_2_1__X` | 0 | None | 0 |
| `dfrtp_2_14` | `o21a_2_4__A1` | `nand2b_2_1__Y` | 0 | None | 0 |
| `dfrtp_2_15` | `xor2_2_0__B` | `o211a_2_7__X` | 0 | 22 | 55 |
| `dfrtp_2_16` | `xor2_2_7__A` | `mux2_1_5__X` | 0 | 11 | 55 |
| `dfrtp_2_17` | `xor2_2_9__A` | `xor2_2_9__X` | 0 | 44 | 44 |
| `dfrtp_2_18` | `xor2_2_4__A` | `o311a_2_1__X` | 0 | 88 | 33 |
| `dfrtp_2_19` | `nor3_2_2__B` | `and2b_2_9__X` | 0 | None | 0 |
| `dfrtp_2_2` | `or4_2_1__A` | `a21o_2_0__X` | 0 | None | 0 |
| `dfrtp_2_20` | `and4_2_3__C` | `xnor2_2_11__Y` | 0 | None | 0 |
| `dfrtp_2_21` | `nor3_2_2__A` | `o21a_2_12__X` | 0 | None | 0 |
| `dfrtp_2_22` | `or3_2_8__C` | `xor2_2_10__X` | 0 | None | 0 |
| `dfrtp_2_23` | `or3_2_8__A` | `nor2_2_30__Y` | 0 | None | 0 |
| `dfrtp_2_24` | `and4_2_3__A` | `a32o_2_2__X` | 0 | None | 0 |
| `dfrtp_2_25` | `and4_2_3__B` | `dfrtp_2_25__D` | 0 | None | 0 |
| `dfrtp_2_26` | `or3_2_8__B` | `o21a_2_11__X` | 0 | None | 0 |
| `dfrtp_2_27` | `or2_2_7__A` | `a22o_2_1__X` | 0 | None | 0 |
| `dfrtp_2_28` | `inv_2_6__A` | `a31o_2_11__X` | 0 | 11 | 110 |
| `dfrtp_2_29` | `inv_2_8__A` | `dfrtp_2_29__D` | 0 | None | 0 |
| `dfrtp_2_3` | `or4_2_3__A` | `a21o_2_2__X` | 0 | None | 0 |
| `dfrtp_2_30` | `mux2_1_8__A1` | `mux2_1_14__X` | 0 | None | 0 |
| `dfrtp_2_31` | `mux2_1_19__A1` | `mux2_1_18__X` | 0 | None | 0 |
| `dfrtp_2_32` | `mux2_1_9__A1` | `mux2_1_17__X` | 0 | None | 0 |
| `dfrtp_2_33` | `mux2_1_12__A1` | `mux2_1_10__X` | 0 | None | 0 |
| `dfrtp_2_34` | `mux2_1_8__A0` | `mux2_1_8__X` | 0 | None | 0 |
| `dfrtp_2_35` | `mux2_1_16__A0` | `mux2_1_16__X` | 0 | None | 0 |
| `dfrtp_2_36` | `mux2_1_12__A0` | `mux2_1_12__X` | 0 | None | 0 |
| `dfrtp_2_37` | `inv_2_11__A` | `a31o_2_12__X` | 0 | None | 0 |
| `dfrtp_2_38` | `a22o_2_2__B2` | `mux2_1_11__X` | 0 | None | 0 |
| `dfrtp_2_39` | `mux2_1_19__A0` | `mux2_1_19__X` | 0 | None | 0 |
| `dfrtp_2_4` | `o21a_2_5__A1` | `dfrtp_2_4__D` | 0 | None | 0 |
| `dfrtp_2_40` | `mux2_1_9__A0` | `mux2_1_9__X` | 0 | None | 0 |
| `dfrtp_2_41` | `a22o_2_2__A2` | `mux2_1_13__X` | 0 | None | 0 |
| `dfrtp_2_42` | `mux2_1_15__A0` | `mux2_1_15__X` | 0 | None | 0 |
| `dfrtp_2_43` | `or4_2_4__B` | `dfrtp_2_43__D` | 0 | 2 | 55 |
| `dfrtp_2_44` | `or4_2_4__A` | `nor2_2_31__Y` | 0 | 1 | 55 |
| `dfrtp_2_45` | `or4_2_4__D` | `dfrtp_2_45__D` | 0 | 8 | 33 |
| `dfrtp_2_46` | `or4_2_4__C` | `xor2_2_11__X` | 0 | 4 | 44 |
| `dfrtp_2_47` | `or2_2_11__A` | `a31o_2_13__X` | 0 | None | 0 |
| `dfrtp_2_48` | `xor2_2_14__B` | `a221o_2_4__X` | 0 | 2 | 63 |
| `dfrtp_2_49` | `a22o_2_4__B2` | `a31o_2_14__X` | 0 | 1 | 62 |
| `dfrtp_2_5` | `nand4_2_2__C` | `o21a_2_8__X` | 0 | None | 0 |
| `dfrtp_2_50` | `xor2_2_19__A` | `o22a_2_3__X` | 0 | 1 | 64 |
| `dfrtp_2_51` | `xor2_2_19__B` | `a221o_2_2__X` | 0 | 1 | 63 |
| `dfrtp_2_52` | `or4_2_5__A` | `a21o_2_13__X` | 0 | None | 0 |
| `dfrtp_2_53` | `nand4_2_5__C` | `o21a_2_30__X` | 0 | None | 0 |
| `dfrtp_2_54` | `inv_2_16__A` | `o21a_2_17__X` | 0 | None | 0 |
| `dfrtp_2_55` | `nand4_2_6__C` | `o21a_2_18__X` | 0 | None | 0 |
| `dfrtp_2_56` | `nand4_2_4__C` | `o21a_2_16__X` | 0 | None | 0 |
| `dfrtp_2_57` | `o21a_2_19__A1` | `dfrtp_2_57__D` | 0 | None | 0 |
| `dfrtp_2_58` | `o21a_2_18__A1` | `dfrtp_2_58__D` | 0 | None | 0 |
| `dfrtp_2_59` | `o21a_2_16__A1` | `dfrtp_2_59__D` | 0 | None | 0 |
| `dfrtp_2_6` | `nand4_2_1__C` | `o21a_2_10__X` | 0 | None | 0 |
| `dfrtp_2_60` | `nand4_2_7__C` | `o21a_2_19__X` | 0 | None | 0 |
| `dfrtp_2_61` | `or4_2_9__A` | `a21o_2_18__X` | 0 | None | 0 |
| `dfrtp_2_62` | `inv_2_18__A` | `o21a_2_20__X` | 0 | None | 0 |
| `dfrtp_2_63` | `o21a_2_23__A1` | `dfrtp_2_63__D` | 0 | None | 0 |
| `dfrtp_2_64` | `o21a_2_28__A1` | `dfrtp_2_64__D` | 0 | None | 0 |
| `dfrtp_2_65` | `inv_2_19__A` | `o21a_2_22__X` | 0 | None | 0 |
| `dfrtp_2_66` | `o21a_2_21__A1` | `dfrtp_2_66__D` | 0 | None | 0 |
| `dfrtp_2_67` | `o21a_2_24__A1` | `dfrtp_2_67__D` | 0 | None | 0 |
| `dfrtp_2_68` | `o21a_2_25__A1` | `dfrtp_2_68__D` | 0 | None | 0 |
| `dfrtp_2_69` | `or4_2_6__A` | `a21o_2_16__X` | 0 | None | 0 |
| `dfrtp_2_7` | `inv_2_2__A` | `o21a_2_9__X` | 0 | None | 0 |
| `dfrtp_2_70` | `o21a_2_27__A1` | `dfrtp_2_70__D` | 0 | None | 0 |
| `dfrtp_2_71` | `nand4_2_8__C` | `o21a_2_23__X` | 0 | None | 0 |
| `dfrtp_2_72` | `inv_2_20__A` | `o21a_2_26__X` | 0 | None | 0 |
| `dfrtp_2_73` | `nand4_2_13__C` | `o21a_2_25__X` | 0 | None | 0 |
| `dfrtp_2_74` | `nand4_2_12__C` | `o21a_2_27__X` | 0 | None | 0 |
| `dfrtp_2_75` | `nand4_2_11__C` | `o21a_2_24__X` | 0 | None | 0 |
| `dfrtp_2_76` | `inv_2_17__A` | `o21a_2_29__X` | 0 | None | 0 |
| `dfrtp_2_77` | `or4_2_7__A` | `a21o_2_14__X` | 0 | None | 0 |
| `dfrtp_2_78` | `nand4_2_10__C` | `o21a_2_28__X` | 0 | None | 0 |
| `dfrtp_2_79` | `or4_2_8__A` | `a21o_2_15__X` | 0 | None | 0 |
| `dfrtp_2_8` | `nand4_2_3__C` | `o21a_2_5__X` | 0 | None | 0 |
| `dfrtp_2_80` | `nand4_2_9__C` | `o21a_2_21__X` | 0 | None | 0 |
| `dfrtp_2_81` | `success` | `a32o_2_4__X` | 0 | None | 0 |
| `dfrtp_2_82` | `a32o_2_3__B1` | `a32o_2_3__X` | 0 | None | 0 |
| `dfrtp_2_83` | `or2_2_11__B` | `or2_2_11__X` | 0 | None | 0 |
| `dfrtp_2_9` | `inv_2_3__A` | `o21a_2_6__X` | 0 | None | 0 |
| `dfstp_2_0` | `xor2_2_17__B` | `dfstp_2_0__D` | 1 | 1 | 63 |
| `dfstp_2_1` | `xor2_2_16__A` | `o221a_2_1__X` | 1 | 1 | 63 |
| `dfstp_2_2` | `xor2_2_20__A` | `dfstp_2_2__D` | 1 | 1 | 63 |
| `dfstp_2_3` | `or2_2_12__A` | `o32a_2_3__X` | 1 | 1 | 64 |
| `dfxtp_2_0` | `or2_2_8__B` | `dfxtp_2_0__D` | 0 | None | 0 |
| `dfxtp_2_1` | `or2_2_9__A` | `dfxtp_2_1__D` | 0 | None | 0 |
| `dfxtp_2_2` | `or3b_2_0__A` | `dfxtp_2_2__D` | 0 | None | 0 |
| `dfxtp_2_3` | `or2_2_9__B` | `dfxtp_2_3__D` | 0 | None | 0 |

## Path-relevant (or4b / and2b→nand2 / FA phase)

| Instance | Q net | Q@0 | first Δ | note |
|----------|-------|----:|--------:|------|
| `dfrtp_2_13` | `or4_2_2__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_2` | `or4_2_1__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_3` | `or4_2_3__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_43` | `or4_2_4__B` | 0 | 2 | FA/or4_2_4 or nand-path |
| `dfrtp_2_44` | `or4_2_4__A` | 0 | 1 | FA/or4_2_4 or nand-path |
| `dfrtp_2_45` | `or4_2_4__D` | 0 | 8 | FA/or4_2_4 or nand-path |
| `dfrtp_2_46` | `or4_2_4__C` | 0 | 4 | FA/or4_2_4 or nand-path |
| `dfrtp_2_47` | `or2_2_11__A` | 0 | None | FA/or4_2_4 or nand-path; and2b_2_11 A_N (FA in) |
| `dfrtp_2_52` | `or4_2_5__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_61` | `or4_2_9__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_69` | `or4_2_6__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_77` | `or4_2_7__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_79` | `or4_2_8__A` | 0 | None | or4 A/B (sticky and2 pin) |
| `dfrtp_2_83` | `or2_2_11__B` | 0 | None | FA/or4_2_4 or nand-path |

## Still 0 forever (all0)

75 flops never go high: `dfrtp_2_0`, `dfrtp_2_1`, `dfrtp_2_10`, `dfrtp_2_11`, `dfrtp_2_12`, `dfrtp_2_13`, `dfrtp_2_14`, `dfrtp_2_19`, `dfrtp_2_2`, `dfrtp_2_20`, `dfrtp_2_21`, `dfrtp_2_22`, `dfrtp_2_23`, `dfrtp_2_24`, `dfrtp_2_25`, `dfrtp_2_26`, `dfrtp_2_27`, `dfrtp_2_29`, `dfrtp_2_3`, `dfrtp_2_30`, `dfrtp_2_31`, `dfrtp_2_32`, `dfrtp_2_33`, `dfrtp_2_34`, `dfrtp_2_35`, `dfrtp_2_36`, `dfrtp_2_37`, `dfrtp_2_38`, `dfrtp_2_39`, `dfrtp_2_4`, `dfrtp_2_40`, `dfrtp_2_41`, `dfrtp_2_42`, `dfrtp_2_47`, `dfrtp_2_5`, `dfrtp_2_52`, `dfrtp_2_53`, `dfrtp_2_54`, `dfrtp_2_55`, `dfrtp_2_56`…
