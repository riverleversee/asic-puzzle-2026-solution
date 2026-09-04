# FA input into nand2(I, ·) — not the nand B output

The nand2 that drives each sticky_or `or4.D` is:

```text
nand2.Y = ~( nand2.A  ∧  nand2.B )
        = ~( I        ∧  inv_2_7__A )
```

`inv_2_7__A` is **not** a raw FA bit — it is `and2b_2_11` output:

```text
inv_2_7__A = enable ∧ ¬or2_2_11__A
```

**FA-side input** (the one that can kill the nand B arm) = `or2_2_11__A`
(flop `dfrtp_2_47` Q). Its D fan-in reaches FA phase `or4_2_4` via `inv_2_9__A`
(`and4bb_2_6` of `or4_2_4`).

Stimulus: **all0**.

- `or2_2_11__A` (FA input) high @ `[]`  (n=0)
- `inv_2_7__A` (nand B, enable∧¬FA_in) high n=121
- `inv_2_9__A` (FA phase and4bb) high @ `[10, 21, 32, 43, 54, 65, 76, 87, 98, 109, 120]`  (n=11)

Figure: [`fa_input_to_nand2_timeline.png`](fa_input_to_nand2_timeline.png)
