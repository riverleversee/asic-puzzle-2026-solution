# Rules — SET path behind inv_2_23 / a31o_2_12 / a221o_2_1
# Index over rule files in this directory.
#
# Sibling style: phase3/and4b/groups/rules/ (22 hasI leaves, exactly-2 ones).

CONFIRMED
  a31o sticky SET / a221o fold neighbor spacings
    →  a31o_sticky_set_spacing.txt

UNIFIED HARD RULE
  Same mechanism as tools inv11 / hot-offset (Δ ∈ {1,10,11,12}).

  Allowed later-cycle windows for a second I=1
  (measured: sticky inv_2_11__A does **not** arm — see fold_windows/):
    Δ ∈ {1, 12}  — later ≡ 0  (mod 11)
    Δ = 10       — later ≡ 10 (mod 11)
    Δ = 11       — never

  Forcer form: no neighbor / +10..+12 partner unless on that window;
  else force the partner to 0. Sticky arms on a *forbidden* live pair.

RELATED (phase3 and4b — different mechanism)
  Exactly-2 I=1 on each leaf's FA open windows
    →  phase3/and4b/groups/rules/README.txt
  (Slot oracle ≡ this leaf Σ=2 — not a separate rule.)
