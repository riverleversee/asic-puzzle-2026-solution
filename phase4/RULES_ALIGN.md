# Phase 4 — rule alignment note

## Period-11
**Exactly 2** ones per `C_k = [11k..11k+10]` (mux inhibit + and4). Not ≤2.

## Leaf / “slot oracle”
Identical: each and4b hasI leaf needs **exactly 2** ones on its FA opens.
No separate slot constraint.

## Neighbor / +10..+12 vs inv11 hot-offset

Same a221o fold (`Δ ∈ {1,10,11,12}`). Phase-3 rule
(`a31o_sticky_set_spacing.txt`) is the source of truth for windows —
measured by observing sticky `inv_2_11__A` directly
(`phase3/a221o_set/fold_windows/`).

| Δ | Allowed later `t1` | Notes |
|--:|--------------------|-------|
| 1, 12 | `t1 ≡ 0 (mod 11)` | sticky does not arm |
| 10 | `t1 ≡ 10 (mod 11)` | sticky does not arm |
| 11 | never | — |

Do **not** use the older or4 ABCD map (0000@phase10 / 0101@phase9) as the
residue table — that was how the superseded ≡10 / ≡9 windows were derived.

Forcer form: force partner to 0 unless on that window. Sticky rises on a
*forbidden* live pair (not on an allowed one).

Source: `phase3/a221o_set/rules/a31o_sticky_set_spacing.txt`
