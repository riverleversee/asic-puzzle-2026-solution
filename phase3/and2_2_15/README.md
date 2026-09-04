# Phase 3 — `and2_2_15` A-arm (`inv_2_6` / `a31o_2_11`)

Sticky **fail** latch on the success-entry AND’s A pin.

```text
and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X
inv_2_6.Y   = ¬ inv_2_6.A
inv_2_6.A   = dfrtp_2_28.Q     # sticky Q
dfrtp_2_28.D ← a31o_2_11.X
```

## Rules

- [`rules/a31o_2_11_fail_trip_mux_gate.txt`](rules/a31o_2_11_fail_trip_mux_gate.txt) — trip @ ≡10 mod 11; inhibit = `mux.X=0`
- [`rules/mux_period11_two_ones_inhibit.txt`](rules/mux_period11_two_ones_inhibit.txt) — each period-11 window needs two `I=1` or sticky trips
- Note: [`notes/mux_S_prep_and_switch.txt`](notes/mux_S_prep_and_switch.txt) — first one preps, second switches mux `S`
- [`rules/pin_watch_1hop_to_I.txt`](rules/pin_watch_1hop_to_I.txt) — timeline watches ≤1 hop from an I-reaching net
- [`rules/and4_2_3_two_per_cycle.txt`](rules/and4_2_3_two_per_cycle.txt) — B-arm: 2 `I=1`/period-11 cycle satisfies `and4_2_3` (sim +extra cycles)

## Figures

- Mux pin dependence (A0/A1/S → X → a31o.A3):
  [`figures/mux2_1_7_a31o_dependence.png`](figures/mux2_1_7_a31o_dependence.png)
- Phase-2 only-I expand / stub timelines:
  [`../../phase2/and2_2_15/inv_2_6/`](../../phase2/and2_2_15/inv_2_6/)

## Regenerate figure

```bash
python3 phase3/and2_2_15/run_mux_dependence_figure.py
```
