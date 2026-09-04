# Rules — and2_2_15 A-arm (inv_2_6 / a31o_2_11)
# Index over rule files in this directory.

WORKING
  Fail trip at period-11 FA edge; inhibit via mux2_1_7.X=0
    →  a31o_2_11_fail_trip_mux_gate.txt

  Each period-11 window needs two I=1 (prep + mux-S switch) or sticky trips
    →  mux_period11_two_ones_inhibit.txt
    note →  ../notes/mux_S_prep_and_switch.txt

  Watch pins: ≤1 hop from an I-reaching net
    →  pin_watch_1hop_to_I.txt

B-ARM (and4_2_3)
  Two I=1 per period-11 cycle satisfies and4 (sim a few extra cycles)
    →  and4_2_3_two_per_cycle.txt
    report →  phase2/.../dfrtp_2_24/reports/I2win_2per_extended.md

SIBLING (different sticky)
  Success SET behind inv_2_23 / a31o_2_12
    →  phase3/a221o_set/rules/a31o_sticky_set_spacing.txt
