# Phase 3 — a221o / a31o sticky SET testing

Sims and confirmed rules for the SET path behind `inv_2_23`
(visual fan-in lives in [`../../phase2/a221o_behind_inv23/`](../../phase2/a221o_behind_inv23/)).

```text
a221o_set/
  rules/                         sticky SET spacing rule
  I_dep/                         I-dependence + I-vs-I tracer outputs
    timelines/                   per-pin response stacks
    shift_chain/                 delay-structure match + spaced-I tests
  run_I_dep_*.py
  run_I_dep_response_timelines.py
  match_known_delay_structures.py
  run_shift_chain_inspect.py
  trace_I_comparisons.py
```

## Rule

[`rules/a31o_sticky_set_spacing.txt`](rules/a31o_sticky_set_spacing.txt) —
Δ∈{1,10,11,12} + FA gates ⇒ a31o sticky latch sets.

## Regenerate

```bash
export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
export MPLBACKEND=Agg
python3 phase3/a221o_set/run_I_dep_a221o_pins.py
python3 phase3/a221o_set/run_I_dep_a22o_pins.py
python3 phase3/a221o_set/run_I_dep_response_timelines.py
python3 phase3/a221o_set/match_known_delay_structures.py
python3 phase3/a221o_set/run_shift_chain_inspect.py
python3 phase3/a221o_set/trace_I_comparisons.py
```
