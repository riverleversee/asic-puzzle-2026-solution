> **Structural verdict:** see [`structure_match.md`](structure_match.md) — hypothesis supported: **yes**.

# Shift-chain inspect (I entry @ cycle 1)

**Rule:** sticky SET spacing → [`../rules/a31o_sticky_set_spacing.txt`](../rules/a31o_sticky_set_spacing.txt)
(Δ∈{1,10,11,12} + FA gates ⇒ a31o / dfrtp_2_37 sticky sets).

The A2/B2 path behind `a221o` / `a22o` is a **mux+flop shift register**
fed by `mux2_1_13.A1 = I`. FA-side nets do not carry I; they **gate**
whether a shifted pulse shows up on `a22o.X` / `a221o.X`.

- Reference stimulus: **`I=1` at cycle `1`** (not 120).
- Diff window: cycles `0..119`.
- FA-prior nets identical for all tested I placements: **yes**
- Close gaps Δ∈`[1, 2, 3, 5, 6, 10, 11, 12]` · wide gaps Δ∈`[15, 20, 22, 24, 33, 44, 55, 66, 77, 88]` · triples Δ∈`[22, 33, 44]`

## Figures

| Figure | What to look for |
|--------|------------------|
| [`board_I_at_1.png`](board_I_at_1.png) | Full cascade for I@1 |
| [`board_I_spaced_g44.png`](board_I_spaced_g44.png) | Two cascades, Δ=44 |
| [`chain_delay_match.png`](chain_delay_match.png) | Verilog depth == sim delay |
| [`fa_prior_vs_I.png`](fa_prior_vs_I.png) | FA stubs unchanged with I |
| [`time_entry_shift_vs_gated.png`](time_entry_shift_vs_gated.png) | Diagonal shift vs missing C1 pulses |
| [`aligned_invariance.png`](aligned_invariance.png) | After align-to-I@1: taps overlap; gated may not |
| [`extra_I_close_vs_OR.png`](extra_I_close_vs_OR.png) | Close double-I vs OR(singles) |
| [`extra_I_wide_vs_OR.png`](extra_I_wide_vs_OR.png) | **Wide** double-I (Δ up to 88) vs OR |
| [`extra_I_triple_vs_OR.png`](extra_I_triple_vs_OR.png) | **Triple** spaced I vs OR of 3 |

Structural template scorecard: [`structure_match.md`](structure_match.md).

## Verilog chain (S=1 path)

```text
  [ 0] +0  combo_mux   mux2_1_13__X                  A1=I → X (when S=1)
  [ 1] +1  flop        a22o_2_2__A2                  D←mux2_1_13__X
  [ 1] +1  combo_mux   mux2_1_18__X                  A1←a22o_2_2__A2 → X
  [ 2] +2  flop        mux2_1_19__A1                 D←mux2_1_18__X
  [ 2] +2  combo_mux   mux2_1_19__X                  A1←mux2_1_19__A1 → X
  [ 3] +3  flop        mux2_1_19__A0                 D←mux2_1_19__X
  [ 3] +3  combo_mux   mux2_1_17__X                  A1←mux2_1_19__A0 → X
  [ 4] +4  flop        mux2_1_9__A1                  D←mux2_1_17__X
  [ 4] +4  combo_mux   mux2_1_9__X                   A1←mux2_1_9__A1 → X
  [ 5] +5  flop        mux2_1_9__A0                  D←mux2_1_9__X
  [ 5] +5  combo_mux   mux2_1_16__X                  A1←mux2_1_9__A0 → X
  [ 6] +6  flop        mux2_1_16__A0                 D←mux2_1_16__X
  [ 6] +6  combo_mux   mux2_1_15__X                  A1←mux2_1_16__A0 → X
  [ 7] +7  flop        mux2_1_15__A0                 D←mux2_1_15__X
  [ 7] +7  combo_mux   mux2_1_14__X                  A1←mux2_1_15__A0 → X
  [ 8] +8  flop        mux2_1_8__A1                  D←mux2_1_14__X
  [ 8] +8  combo_mux   mux2_1_8__X                   A1←mux2_1_8__A1 → X
  [ 9] +9  flop        mux2_1_8__A0                  D←mux2_1_8__X
  [ 9] +9  combo_mux   mux2_1_10__X                  A1←mux2_1_8__A0 → X
  [10] +10  flop        mux2_1_12__A1                 D←mux2_1_10__X
  [10] +10  combo_mux   mux2_1_12__X                  A1←mux2_1_12__A1 → X
  [11] +11  flop        mux2_1_12__A0                 D←mux2_1_12__X
  [11] +11  combo_mux   mux2_1_11__X                  A1←mux2_1_12__A0 → X
  [12] +12  flop        a22o_2_2__B2                  D←mux2_1_11__X
```

## Delay match (I@1)

| tap | expected | observed | ok |
|-----|--------:|---------:|:--:|
| `D_A2` | 0 | 0 | ✓ |
| `a22o_A2` | 1 | 1 | ✓ |
| `a221o_A2` | 10 | 10 | ✓ |
| `a221o_B2` | 11 | 11 | ✓ |
| `D_B2` | 11 | 11 | ✓ |
| `a22o_B2` | 12 | 12 | ✓ |

## Does behavior depend on I entry cycle?

Checked across all single-I starts `[1, 2, 3, 4, 6, 7, 11, 12, 13, 16, 21, 23, 25, 34, 45, 56, 67, 78, 89]` (near + wide).

| net | group | shift-invariant (aligned to I@1)? |
|-----|-------|:---------------------------------:|
| `a22o_A2` | shift | **yes** |
| `a221o_A2` | shift | **yes** |
| `a221o_B2` | shift | **yes** |
| `a22o_B2` | shift | **yes** |
| `a22o_X` | gated | **no** |
| `a221o_X` | gated | **no** |

- **Shift taps** (`a22o.A2` … `a22o.B2`): same shape for every entry cycle;
  only a delay. Matches the Verilog flop chain.
- **Gated** (`a22o.X` / `a221o.X`): **depends on entry cycle**, because
  `a22o.X = (or4.X ∧ A2) ∨ (buf ∧ B2)` and `or4.X` (FA bus) has holes
  on a fixed schedule — an I pulse that arrives when `or4.X=0` is swallowed.

## Extra I — close gaps

Δ ∈ `[1, 2, 3, 5, 6, 10, 11, 12]` (pulses can still interact inside the 12-stage chain).

| net | linear OR? | nonlinear gaps |
|-----|:----------:|----------------|
| `a22o_A2` | **yes** | — |
| `a221o_A2` | **yes** | — |
| `a221o_B2` | **yes** | — |
| `a22o_B2` | **yes** | — |
| `a22o_X` | **yes** | — |
| `a221o_X` | **yes** | — |

## Extra I — wide gaps

Δ ∈ `[15, 20, 22, 24, 33, 44, 55, 66, 77, 88]` (well past chain length / on or4 hole period).

| net | linear OR? | nonlinear gaps |
|-----|:----------:|----------------|
| `a22o_A2` | **yes** | — |
| `a221o_A2` | **yes** | — |
| `a221o_B2` | **yes** | — |
| `a22o_B2` | **yes** | — |
| `a22o_X` | **yes** | — |
| `a221o_X` | **yes** | — |

## Extra I — triple spaced

I@{1, 1+Δ, 1+2Δ} for Δ ∈ `[22, 33, 44]` vs OR of three singles.

| net | linear OR? | nonlinear gaps |
|-----|:----------:|----------------|
| `a22o_A2` | **yes** | — |
| `a221o_A2` | **yes** | — |
| `a221o_B2` | **yes** | — |
| `a22o_B2` | **yes** | — |
| `a22o_X` | **yes** | — |
| `a221o_X` | **yes** | — |

## FA-prior independence

These nets are upstream / beside FA and do **not** reach primary `I`.
They must be identical under all0 and every `I@{s}`:

- `or4_X` differs at starts: none
- `or4_A` differs at starts: none
- `or4_B` differs at starts: none
- `or4_C` differs at starts: none
- `or4_D` differs at starts: none
- `or4bb` differs at starts: none
- `S` differs at starts: none
- `AN` differs at starts: none

JSON: [`shift_chain_report.json`](shift_chain_report.json)

Regenerate:
```bash
python3 phase3/a221o_set/match_known_delay_structures.py
python3 phase3/a221o_set/run_shift_chain_inspect.py
```
