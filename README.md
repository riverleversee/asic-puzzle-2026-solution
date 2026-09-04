# rework_coded — generators live next to results

Golden reference (read-only compare): [`../rework/`](../rework/).

Layout follows the success-tree investigation depth:

```text
netlist/          spice → structural.v   (+ spice_to_structural_verilog.py)
phase1/           operator match + die maps
phase2/           visuals — fan-in / expands (interpret verilog/spice)
  success/        fan-in depth maps
  a221o_behind_inv23/   SET-path fan-in + stub timeline
  and2_2_15/      success-entry AND join (and4_2_3/ + inv_2_6/ arms)
  and4b/
    behind/       how type groups were formed
    groups/tNN/   expand-back figures per type
phase3/           sims / tests / confirmed rules
  and4b/groups/tNN/
  a221o_set/      SET-path I-dep, shift-chain, sticky SET spacing rule
  nand2b_B2/
lib/              shared helpers only
```

## Regenerate (from `rework_coded/`)

```bash
export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"

# Netlist
python3 netlist/run_generate.py netlist/puzzle_gates.spice netlist/puzzle_structural.v

# Phase 1
python3 phase1/run_match.py
python3 phase1/run_figures.py

# Phase 2
python3 phase2/run_fa.py
python3 phase2/success/run_bundle.py --bundle
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

# Phase 3
python3 phase3/and4b/groups/run_FA_opens.py
python3 phase3/and4b/groups/run_k_ones.py
python3 phase3/and4b/groups/run_k_ones.py --groups 3 4 --k-max 5
python3 phase3/and4b/groups/run_two_ones_gaps.py --groups 3 4 --gap-max 4
python3 phase3/and4b/groups/run_ones_gap_variants.py --groups 3 4 --gap-max 4 --start-max 3
python3 phase3/and4b/groups/run_opens.py
python3 phase3/and4b/groups/run_fa_input.py
python3 phase3/and4b/groups/flop_init_all0/run_flop_init.py
python3 phase3/a221o_set/run_I_dep_a221o_pins.py
python3 phase3/a221o_set/run_I_dep_a22o_pins.py
python3 phase3/a221o_set/run_I_dep_response_timelines.py
python3 phase3/a221o_set/match_known_delay_structures.py
python3 phase3/a221o_set/run_shift_chain_inspect.py
python3 phase3/a221o_set/trace_I_comparisons.py
python3 phase3/nand2b_B2/run_confirm_no_I.py
python3 phase3/nand2b_B2/run_watch.py
python3 phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/a5A/run_k2_k3.py
python3 phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/a5A/run_two_flops.py
python3 phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/a5A/run_ff_timeline.py

# Verify vs golden
python3 verify_vs_golden.py
```

Each folder’s `README.md` + `run_*.py` is the local entry point; the generator `.py` sits beside the artifacts it writes.
