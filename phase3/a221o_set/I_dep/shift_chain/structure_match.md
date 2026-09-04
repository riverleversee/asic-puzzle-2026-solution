# Known delay-structure comparison

Structural rules only (Verilog pin connectivity). Simulation is a
separate sanity check in `run_shift_chain_inspect.py`.

## Hypothesis supported: **yes**

I→a221o/a22o A2/B2 path is an enabled_mux_shift_register; a22o.X/a221o.X are FA-gated observes — not delay structures.

## Template scorecard

| Template | Result | Summary |
|----------|:------:|---------|
| `enabled_mux_shift_register` | **MATCH** | MATCH · 12/12 stages satisfy mux-hold shift rules; S=inv_2_7__A; taps on chain: a22o.A2=Q0, a221o.A2=Q9, a221o.B2=Q10, a22o.B2=Q11 |
| `plain_dff_chain` | **no match** | NO MATCH · D inputs are mux outputs (hold+shift), not bare Q/I |
| `fa_xor_arith_path` | **no match** | NO MATCH · spine is mux+flop (not FA/xor arith); taps are flop Q |
| `gated_observe_sites` | **MATCH** | CONFIRMED · a22o.X/a221o.X = shift taps ∧ FA-prior stubs (gated observe, not a delay) |

### How to read this

- We **want** `enabled_mux_shift_register` = MATCH.
- We **want** `plain_dff_chain` = no match (mux hold present).
- We **want** `fa_xor_arith_path` = no match (not FA arithmetic on I).
- We **want** `gated_observe_sites` = MATCH (C1 path is shift ∧ FA stub).

## Figures

- [`structure_checklist.png`](structure_checklist.png) — pass/fail per template & stage
- [`structure_chain_schematic.png`](structure_chain_schematic.png) — mux↔dff hold/shift diagram

## `enabled_mux_shift_register` stages

| i | mux | flop | Q | A1 (din) | A0 (hold) | ok |
|--:|-----|------|---|----------|-----------|:--:|
| 0 | `mux2_1_13` | `dfrtp_2_41` | `a22o_2_2__A2` | `I` | `a22o_2_2__A2` | ✓ |
| 1 | `mux2_1_18` | `dfrtp_2_31` | `mux2_1_19__A1` | `a22o_2_2__A2` | `mux2_1_19__A1` | ✓ |
| 2 | `mux2_1_19` | `dfrtp_2_39` | `mux2_1_19__A0` | `mux2_1_19__A1` | `mux2_1_19__A0` | ✓ |
| 3 | `mux2_1_17` | `dfrtp_2_32` | `mux2_1_9__A1` | `mux2_1_19__A0` | `mux2_1_9__A1` | ✓ |
| 4 | `mux2_1_9` | `dfrtp_2_40` | `mux2_1_9__A0` | `mux2_1_9__A1` | `mux2_1_9__A0` | ✓ |
| 5 | `mux2_1_16` | `dfrtp_2_35` | `mux2_1_16__A0` | `mux2_1_9__A0` | `mux2_1_16__A0` | ✓ |
| 6 | `mux2_1_15` | `dfrtp_2_42` | `mux2_1_15__A0` | `mux2_1_16__A0` | `mux2_1_15__A0` | ✓ |
| 7 | `mux2_1_14` | `dfrtp_2_30` | `mux2_1_8__A1` | `mux2_1_15__A0` | `mux2_1_8__A1` | ✓ |
| 8 | `mux2_1_8` | `dfrtp_2_34` | `mux2_1_8__A0` | `mux2_1_8__A1` | `mux2_1_8__A0` | ✓ |
| 9 | `mux2_1_10` | `dfrtp_2_33` | `mux2_1_12__A1` | `mux2_1_8__A0` | `mux2_1_12__A1` | ✓ |
| 10 | `mux2_1_12` | `dfrtp_2_36` | `mux2_1_12__A0` | `mux2_1_12__A1` | `mux2_1_12__A0` | ✓ |
| 11 | `mux2_1_11` | `dfrtp_2_38` | `a22o_2_2__B2` | `mux2_1_12__A0` | `a22o_2_2__B2` | ✓ |

### Observe taps on the shift Qs

| tap | on chain? | stage | expected delay |
|-----|:---------:|------:|---------------:|
| `a22o.A2` | yes | 0 | 1 |
| `a221o.A2` | yes | 9 | 10 |
| `a221o.B2` | yes | 10 | 11 |
| `a22o.B2` | yes | 11 | 12 |

## Rule definitions

### enabled_mux_shift_register
```text
shared S across stages
stage0:  mux.A1 = I , mux.A0 = Q0 , flop.D = mux.X , flop.Q = Q0
stage i: mux.A1 = Q{i-1} , mux.A0 = Qi , flop.D = mux.X , flop.Q = Qi
```

### plain_dff_chain
```text
flop0.D = I ; flop_i.D = Q{i-1}   # no mux on D
```

### fa_xor_arith_path
```text
I reaches taps through xor/xnor/AO FA cells (not mux+flop spine)
```

JSON: [`structure_match.json`](structure_match.json)

Regenerate:
```bash
python3 phase3/a221o_set/match_known_delay_structures.py
```
