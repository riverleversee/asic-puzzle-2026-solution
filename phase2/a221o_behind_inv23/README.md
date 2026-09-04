# SET path behind `inv_2_23` — visuals (phase 2)

Fan-in / only-I expands of the sticky SET arm for interpreting the netlist.
**Testing and rules live in phase 3:** [`../../phase3/a221o_set/`](../../phase3/a221o_set/).

## Protocol (only-I)

Deepen only branches that reach primary `I`. Non-I cones stay as **stubs**
(dashed gray · `⋯ no I`).

## Chain

```text
a32o_2_4.A1  =  inv_2_23.A
inv_2_23.A   ←  inv_2_11.Y
inv_2_11.A   ←  dfrtp_2_37.Q          # net inv_2_11__A
dfrtp_2_37.D ←  a31o_2_12.X

a31o_2_12.X  =  (A1 ∧ A2 ∧ A3) ∨ B1
  A1 = I
  A2 = inv_2_7__A = and2b_2_11.Y     # stub; A_N=or2_2_11__A
  A3 = a221o_2_1.X
  B1 = inv_2_11__A                   # sticky Q

a221o_2_1.X  =  (A1 ∧ A2) ∨ (B1 ∧ B2) ∨ C1
```

## Name aliases

| Canonical net | Also |
|---------------|------|
| `inv_2_7__A` | `and2b_2_11.Y` |
| `or2_2_11__A` | `and2b_2_11.A_N`, `dfrtp_2_47.Q` |
| `or4_2_4__X` | `a22o.A1`, `buf_2_0.A` |
| `buf_2_0__X` | `a22o.B1` (= `or4_2_4__X`) |

## Figures

1. Context: [`inv_2_23__A_fanin_depth4.png`](inv_2_23__A_fanin_depth4.png)
2. **a31o**: [`a31o_2_12__X_fanin_depth5.png`](a31o_2_12__X_fanin_depth5.png)
3. **a221o**: [`a221o_2_1__X_fanin_depth5.png`](a221o_2_1__X_fanin_depth5.png)
4. Stub timeline (all0 FA-prior nets): [`timelines/noI_stub_timeline.md`](timelines/noI_stub_timeline.md)

## Phase 3 tests

- I-dep / shift-chain / spaced-I: [`../../phase3/a221o_set/`](../../phase3/a221o_set/)
- Sticky SET spacing rule: [`../../phase3/a221o_set/rules/a31o_sticky_set_spacing.txt`](../../phase3/a221o_set/rules/a31o_sticky_set_spacing.txt)

## Regenerate (visuals only)

```bash
python3 phase2/a221o_behind_inv23/run.py
python3 phase2/a221o_behind_inv23/run_noI_stub_timeline.py
```
