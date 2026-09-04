# Block structures — and4_2_3 B-arm

Root: `and4_2_3__X` · cone **68** nets

Greedy coverage: **19** / **68** (27.9%)

Figure: [`block_fanin.png`](block_fanin.png)

## Greedy cover

| pattern | anchor | members | ports |
|---------|--------|--------:|-------|
| `sticky_ao_latch` | `dfrtp_2_45__D` | 2 | Y=dfrtp_2_45__D, Q=or4_2_4__D, feedback_pin=B2, in_C1=a41oi_2_0__Y, in_A2=inv_2_ |
| `sticky_ao_latch` | `a32o_2_2__X` | 2 | Y=a32o_2_2__X, Q=and4_2_3__A, feedback_pin=B2, in_A2=inv_2_7__A, in_A3=and3_2_10 |
| `sticky_ao_latch` | `a31o_2_13__X` | 2 | Y=a31o_2_13__X, Q=or2_2_11__A, feedback_pin=B1, in_A3=inv_2_7__A, in_A1=inv_2_9_ |
| `andN_flopped_inputs` | `and4_2_7__X` | 4 | Y=and4_2_7__X, C=or4_2_4__C, A=or4_2_4__B, B=or4_2_4__A |
| `andN_flopped_inputs` | `inv_2_5__A` | 3 | Y=inv_2_5__A, C=xor2_2_0__B, D=xor2_2_7__A |
| `andN_flopped_inputs` | `and4_2_4__B` | 3 | Y=and4_2_4__B, A=and4_2_3__C, B=nor3_2_2__A |
| `and2b_enable_gate` | `inv_2_7__A` | 1 | A_N=or2_2_11__A, B=enable, Y=inv_2_7__A |
| `fa_prior_stub_driver` | `inv_2_5__Y` | 1 | Y=inv_2_5__Y |
| `fa_prior_stub_driver` | `inv_2_9__A` | 1 | Y=inv_2_9__A |

Raw matches: **17** (coverage 36.8%)

Uncovered (sample): `I`, `a21o_2_10__X`, `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `a31o_2_9__X`, `a41oi_2_0__Y`, `and2b_2_9__B`, `and2b_2_9__X`, `and3_2_10__B`, `and3_2_11__X`, `and3_2_7__C`, `and3_2_7__X`, `and4_2_3__B`, `and4_2_3__X`, `and4_2_4__D`, `and4_2_4__X`, `dfrtp_2_25__D`, `dfrtp_2_43__D`, `enable`, `inv_2_10__A`, `inv_2_10__Y`, `mux2_1_5__A1`, `mux2_1_5__X`, `nand3_2_0__Y`, `nor2_2_29__Y`, `nor2_2_30__B`, `nor2_2_30__Y`, `nor2_2_31__B`, `nor2_2_31__Y`

JSON: [`recognized.json`](recognized.json)
