# Block structures — inv_2_6 / a31o A-arm

Root: `a31o_2_11__X` · cone **50** nets

Greedy coverage: **23** / **50** (46.0%)

Figure: [`block_fanin.png`](block_fanin.png)

## Greedy cover

| pattern | anchor | members | ports |
|---------|--------|--------:|-------|
| `sticky_ao_latch` | `dfrtp_2_45__D` | 2 | Y=dfrtp_2_45__D, Q=or4_2_4__D, feedback_pin=B2, in_C1=a41oi_2_0__Y, in_A2=inv_2_ |
| `sticky_ao_latch` | `a22o_2_1__X` | 2 | Y=a22o_2_1__X, Q=or2_2_7__A, feedback_pin=A2, in_A1=inv_2_7__Y, in_B2=inv_2_9__Y |
| `sticky_ao_latch` | `a31o_2_11__X` | 2 | Y=a31o_2_11__X, Q=inv_2_6__A, feedback_pin=B1, in_A3=mux2_1_7__X, in_A1=inv_2_9_ |
| `sticky_ao_latch` | `a31o_2_13__X` | 2 | Y=a31o_2_13__X, Q=or2_2_11__A, feedback_pin=B1, in_A3=inv_2_7__A, in_A1=inv_2_9_ |
| `andN_flopped_inputs` | `and4_2_7__X` | 4 | Y=and4_2_7__X, C=or4_2_4__C, A=or4_2_4__B, B=or4_2_4__A |
| `andN_flopped_inputs` | `inv_2_5__A` | 3 | Y=inv_2_5__A, C=xor2_2_0__B, D=xor2_2_7__A |
| `and2b_enable_gate` | `inv_2_7__A` | 1 | A_N=or2_2_11__A, B=enable, Y=inv_2_7__A |
| `inv_on_flop_Q` | `inv_2_8__Y` | 2 | A=inv_2_8__A, Y=inv_2_8__Y |
| `nand2_I_gate` | `mux2_1_7__A0` | 1 | I=I, other=or2_2_7__A, Y=mux2_1_7__A0 |
| `fa_prior_stub_driver` | `inv_2_5__Y` | 1 | Y=inv_2_5__Y |
| `fa_prior_stub_driver` | `inv_2_7__Y` | 1 | Y=inv_2_7__Y |
| `fa_prior_stub_driver` | `inv_2_9__Y` | 1 | Y=inv_2_9__Y |
| `fa_prior_stub_driver` | `inv_2_9__A` | 1 | Y=inv_2_9__A |

Raw matches: **19** (coverage 48.0%)

Uncovered (sample): `I`, `a21o_2_9__X`, `a21oi_2_13__Y`, `a31o_2_8__X`, `a41oi_2_0__Y`, `and3_2_7__C`, `and3_2_7__X`, `dfrtp_2_29__D`, `dfrtp_2_43__D`, `enable`, `mux2_1_5__A1`, `mux2_1_5__X`, `mux2_1_6__X`, `mux2_1_7__X`, `nand3_2_0__Y`, `nor2_2_29__Y`, `nor2_2_31__B`, `nor2_2_31__Y`, `o211a_2_7__X`, `o211a_2_8__X`, `o311a_2_1__X`, `or2_2_7__X`, `xor2_2_11__B`, `xor2_2_11__X`, `xor2_2_4__A`, `xor2_2_9__A`, `xor2_2_9__X`

JSON: [`recognized.json`](recognized.json)
