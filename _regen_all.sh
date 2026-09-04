#!/bin/bash
set -euo pipefail
export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
export MPLBACKEND=Agg
cd /mnt/c/Users/ralev/Documents/CursorCoding/asic-puzzle-2026-master/rework_coded

echo "=== netlist ==="
python3 netlist/run_generate.py

echo "=== phase1 match ==="
python3 phase1/run_match.py

echo "=== phase1 figures ==="
python3 phase1/run_figures.py

echo "=== phase2 fa ==="
python3 phase2/run_fa.py

echo "=== phase2 success bundle ==="
python3 phase2/success/run_bundle.py

echo "=== phase2 inv23 SET path visuals (a31o + a221o) ==="
python3 phase2/a221o_behind_inv23/run.py

echo "=== phase2 inv23 noI stub timeline ==="
python3 phase2/a221o_behind_inv23/run_noI_stub_timeline.py

echo "=== phase2 and2_2_15 join expands ==="
python3 phase2/and2_2_15/run.py

echo "=== phase2 and2_2_15 pre-and4 region size ==="
python3 phase2/and2_2_15/run_count_pre_and4.py

echo "=== phase2 and2_2_15 and4 inputs timeline ==="
python3 phase2/and2_2_15/and4_2_3/run_and4_inputs_timeline.py

echo "=== phase2 and2_2_15 inv_2_6 noI stub timeline ==="
python3 phase2/and2_2_15/inv_2_6/run_noI_stub_timeline.py

echo "=== phase2 and2_2_15 inv_2_6 I=1 probe timeline ==="
python3 phase2/and2_2_15/inv_2_6/run_I1_probe_timeline.py

echo "=== phase2 and2_2_15 structure recognize (both arms) ==="
python3 phase2/and2_2_15/and4_2_3/run_recognize_structures.py
python3 phase2/and2_2_15/inv_2_6/run_recognize_structures.py

echo "=== phase3 a221o_set I-dep + shift-chain + structure match + I-vs-I ==="
python3 phase3/a221o_set/run_I_dep_a221o_pins.py
python3 phase3/a221o_set/run_I_dep_a22o_pins.py
python3 phase3/a221o_set/run_I_dep_response_timelines.py
python3 phase3/a221o_set/match_known_delay_structures.py
python3 phase3/a221o_set/run_shift_chain_inspect.py
python3 phase3/a221o_set/trace_I_comparisons.py

echo "=== phase2 and4b behind compare ==="
python3 phase2/and4b/behind/run_compare.py

echo "=== phase2 and4b behind backtrees ==="
python3 phase2/and4b/behind/run_backtrees.py

echo "=== phase2 and4b groups expand ==="
python3 phase2/and4b/groups/run_expand.py

echo "=== phase3 FA opens ==="
python3 phase3/and4b/groups/run_FA_opens.py

echo "=== phase3 k ones (t01/t02/t05) ==="
python3 phase3/and4b/groups/run_k_ones.py

echo "=== phase3 k ones (t03/t04 sticky_or) ==="
python3 phase3/and4b/groups/run_k_ones.py --groups 3 4 --k-max 5

echo "=== phase3 two-ones open gaps (t03/t04) ==="
python3 phase3/and4b/groups/run_two_ones_gaps.py --groups 3 4 --gap-max 4

echo "=== phase3 three-ones gaps + late two-ones (t03/t04) ==="
python3 phase3/and4b/groups/run_ones_gap_variants.py --groups 3 4 --gap-max 4 --start-max 3

echo "=== phase3 or4b opens ==="
python3 phase3/and4b/groups/run_opens.py

echo "=== phase3 fa input ==="
python3 phase3/and4b/groups/run_fa_input.py

echo "=== phase3 flop init ==="
python3 phase3/and4b/groups/flop_init_all0/run_flop_init.py

echo "=== phase3 nand2b ==="
python3 phase3/nand2b_B2/run_confirm_no_I.py
python3 phase3/nand2b_B2/run_watch.py

echo "=== phase3 a5A ==="
A5=phase3/and4b/groups/t01_n7_hasI_and2b_nand4_c_x_o21a_a1_shallow_27n/a5A
python3 "$A5/run_k2_k3.py"
python3 "$A5/run_two_flops.py"
python3 "$A5/run_ff_timeline.py"

echo "REGEN DONE"
