# Rules — and4b hasI groups with confirmed I-ones behavior (t01–t05)
# Index over per-class rule files in this directory.

CONFIRMED (22 leaves = all and4b hasI members)
  set_once  and2b  t01, t02, t05  →  and2b_set_once_t01_t02_t05.txt
  sticky_or and2   t03, t04       →  and2_sticky_or_t03_t04.txt

UNIFIED HARD RULE
  For every confirmed leaf: number of I=1 on that leaf's own FA open
  windows must be EXACTLY 2.

  1  → under-armed (no PASS)
  2  → PASS (Y sticks), for any pair of that leaf's opens tested
       (any start index; any number of skipped opens between them)
  ≥3 → FAIL (Y dies), including when the three ones are spaced apart

NOT CONFIRMED HERE
  t06–t08 are noI (no and4 leaf I path) — no ones-count rule from these sims.
  Cross-leaf interactions (fold/inv11, co-open heating) are out of scope of
  these per-leaf rules.

RELATED (phase3 SET path — different mechanism)
  Sticky SET spacing Δ∈{1,10,11,12} + FA gates
    →  phase3/a221o_set/rules/a31o_sticky_set_spacing.txt
