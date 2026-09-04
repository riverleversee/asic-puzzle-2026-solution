# Phase 3 — sims / tests under structural interpretations

```text
and4b/groups/
  t01…t05/          FA-open / k-ones / or4b opens / gap sweeps (t03/t04)
  t01…/a5A/         deep-dive leaf and2b_2_25
  rules/            confirmed I-ones rules (exactly-2 for t01–t05)
  fa_input_*        sticky-path FA input
  flop_init_all0/

a221o_set/          SET-path I-dep / shift-chain / sticky SET spacing rule
and2_2_15/          success-entry A-arm fail trip (mux inhibit @ period-11)
nand2b_B2/          success-path nand2b (peer)
build/              iverilog scratch
```

Phase 2 holds the **visual** fan-in expands these tests refer to
(e.g. [`../phase2/a221o_behind_inv23/`](../phase2/a221o_behind_inv23/),
[`../phase2/and2_2_15/inv_2_6/`](../phase2/and2_2_15/inv_2_6/)).

## Regenerate

```bash
export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
python3 phase3/and4b/groups/run_FA_opens.py
python3 phase3/and4b/groups/run_k_ones.py
python3 phase3/and4b/groups/run_opens.py
python3 phase3/and4b/groups/run_fa_input.py
python3 phase3/and4b/groups/flop_init_all0/run_flop_init.py
python3 phase3/a221o_set/run_I_dep_a221o_pins.py
python3 phase3/a221o_set/run_I_dep_a22o_pins.py
python3 phase3/a221o_set/run_I_dep_response_timelines.py
python3 phase3/a221o_set/match_known_delay_structures.py
python3 phase3/a221o_set/run_shift_chain_inspect.py
python3 phase3/a221o_set/trace_I_comparisons.py
python3 phase3/and2_2_15/run_mux_dependence_figure.py
python3 phase3/nand2b_B2/run_confirm_no_I.py
python3 phase3/nand2b_B2/run_watch.py
```

See top [`../README.md`](../README.md) for the full ordered map.
