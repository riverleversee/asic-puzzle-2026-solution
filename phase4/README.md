# Phase 4 — combine phase-3 rules → forced I → sim

Goal: apply locked phase-3 rules in Python, force `I=0/1`, then simulate.

## Rules (aligned)

| Rule | Encoding |
|------|----------|
| and4b leaf Σ=2 on FA opens | = “slot oracle” (same thing) |
| Period-11 **exactly 2** ones | mux + and4 |
| Neighbor / Δ∈{1,10,11,12} | = inv11 hot-offset; allowed laters ≡10 / ≡9 / never |
| D-hold when leaf Σ=2 | open-sum consequence |

See [`RULES_ALIGN.md`](RULES_ALIGN.md) and updated
`phase3/a221o_set/rules/a31o_sticky_set_spacing.txt`.

## Run

```bash
# from rework_coded/
python3 phase4/run_forcer.py --skip-triples   # solo+pairs first (fast)
python3 phase4/sim_solution.py
```

Default opens: `../sim/opens_exact_shift1.json`.

## Outputs

- [`out/forced.md`](out/forced.md)
- [`out/sim_solution.md`](out/sim_solution.md)
- Solver fill GIFs (from `solver_forced_exact` / same final 22 ones):
  - [`out/solver_fill_11x11.gif`](out/solver_fill_11x11.gif) — 11×11 grid
  - [`out/solver_fill_timeline.gif`](out/solver_fill_timeline.gif) — open-window timeline
