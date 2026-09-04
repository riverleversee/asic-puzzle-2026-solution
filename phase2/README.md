# Phase 2 — success fan-in → and4b → type groups (visuals)

Interpreting structural Verilog / spice via fan-in figures and expands.
**Sims and confirmed rules → phase 3.**

```text
success/                 fan-in depth maps from `success`
a221o_behind_inv23/      SET-path fan-in (a31o + a221o, only-I) + stub timeline
and2_2_15/               success-entry AND join; arms in and4_2_3/ + inv_2_6/
  and4_2_3/              B-arm expands + input timelines + structures
  inv_2_6/               A-arm sticky a31o + I-indep/I=1 timelines + structures
and4b/
  behind/                how and2/and2b type groups were formed
  groups/tNN/            expand-back figures (same names as phase3)
```

## Regenerate

```bash
# from rework_coded/
python3 phase2/run_fa.py
python3 phase2/success/run_bundle.py
python3 phase2/a221o_behind_inv23/run.py
python3 phase2/a221o_behind_inv23/run_noI_stub_timeline.py
python3 phase2/and2_2_15/run.py
python3 phase2/and2_2_15/run_count_pre_and4.py
python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py
python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py
python3 phase2/and2_2_15/and4_2_3/run_recognize_structures.py
python3 phase2/and2_2_15/inv_2_6/run_recognize_structures.py
python3 phase2/and4b/behind/run_compare.py
python3 phase2/and4b/behind/run_backtrees.py
python3 phase2/and4b/groups/run_expand.py
```

SET-path **tests** (I-dep, shift-chain, sticky SET rule):
[`../phase3/a221o_set/`](../phase3/a221o_set/).
