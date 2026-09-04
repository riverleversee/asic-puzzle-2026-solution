# I-dep response timelines

Per-pin **stacks**: each row is an I placement (`s=0..10`).
Red tick / pink column = where `I=1`. Colored bars = that pin **≠ all0**.

Zoom `0..48` (early window). Diff scoring still drops cycle `120`.

## Multi-lane boards (all pins together)

Gray = high under the pattern; color overlay = ≠ all0; red tick = I=1.

- [`board_k1_s2.png`](board_k1_s2.png)
- [`board_k1_s3.png`](board_k1_s3.png)
- [`board_k2_s1.png`](board_k2_s1.png)
- [`board_k2_s2.png`](board_k2_s2.png)

## Per-pin stacks

### `a221o_A2` — a221o.A2 ← mux2_1_12__A1

- k=1: [`stack_a221o_A2_k1.png`](stack_a221o_A2_k1.png)
- k=2: [`stack_a221o_A2_k2.png`](stack_a221o_A2_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @10 (n=1) | @10 (n=2) |
| 1 | @11 (n=1) | @11 (n=2) |
| 2 | @12 (n=1) | @12 (n=2) |
| 3 | @13 (n=1) | @13 (n=2) |
| 4 | @14 (n=1) | @14 (n=2) |
| 5 | @15 (n=1) | @15 (n=2) |
| 6 | @16 (n=1) | @16 (n=2) |
| 7 | @17 (n=1) | @17 (n=2) |
| 8 | @18 (n=1) | @18 (n=2) |
| 9 | @19 (n=1) | @19 (n=2) |
| 10 | @20 (n=1) | @20 (n=2) |

### `a221o_B2` — a221o.B2 ← mux2_1_12__A0

- k=1: [`stack_a221o_B2_k1.png`](stack_a221o_B2_k1.png)
- k=2: [`stack_a221o_B2_k2.png`](stack_a221o_B2_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @11 (n=1) | @11 (n=2) |
| 1 | @12 (n=1) | @12 (n=2) |
| 2 | @13 (n=1) | @13 (n=2) |
| 3 | @14 (n=1) | @14 (n=2) |
| 4 | @15 (n=1) | @15 (n=2) |
| 5 | @16 (n=1) | @16 (n=2) |
| 6 | @17 (n=1) | @17 (n=2) |
| 7 | @18 (n=1) | @18 (n=2) |
| 8 | @19 (n=1) | @19 (n=2) |
| 9 | @20 (n=1) | @20 (n=2) |
| 10 | @21 (n=1) | @21 (n=2) |

### `a221o_C1` — a221o.C1 ← a22o_2_2__X

- k=1: [`stack_a221o_C1_k1.png`](stack_a221o_C1_k1.png)
- k=2: [`stack_a221o_C1_k2.png`](stack_a221o_C1_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @1 (n=2) | @1 (n=4) |
| 1 | @2 (n=2) | @2 (n=4) |
| 2 | @3 (n=2) | @3 (n=4) |
| 3 | @4 (n=2) | @4 (n=4) |
| 4 | @5 (n=2) | @5 (n=4) |
| 5 | @6 (n=2) | @6 (n=4) |
| 6 | @7 (n=2) | @7 (n=4) |
| 7 | @8 (n=2) | @8 (n=4) |
| 8 | @9 (n=2) | @9 (n=4) |
| 9 | @10 (n=2) | @10 (n=2) |
| 10 | — | @12 (n=2) |

### `a221o_X` — a221o.X

- k=1: [`stack_a221o_X_k1.png`](stack_a221o_X_k1.png)
- k=2: [`stack_a221o_X_k2.png`](stack_a221o_X_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @1 (n=3) | @1 (n=5) |
| 1 | @2 (n=4) | @2 (n=6) |
| 2 | @3 (n=4) | @3 (n=6) |
| 3 | @4 (n=4) | @4 (n=6) |
| 4 | @5 (n=4) | @5 (n=6) |
| 5 | @6 (n=4) | @6 (n=6) |
| 6 | @7 (n=4) | @7 (n=6) |
| 7 | @8 (n=4) | @8 (n=6) |
| 8 | @9 (n=4) | @9 (n=6) |
| 9 | @10 (n=4) | @10 (n=4) |
| 10 | @20 (n=2) | @12 (n=5) |

### `a22o_A2` — a22o.A2 (flop Q)

- k=1: [`stack_a22o_A2_k1.png`](stack_a22o_A2_k1.png)
- k=2: [`stack_a22o_A2_k2.png`](stack_a22o_A2_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @1 (n=1) | @1 (n=2) |
| 1 | @2 (n=1) | @2 (n=2) |
| 2 | @3 (n=1) | @3 (n=2) |
| 3 | @4 (n=1) | @4 (n=2) |
| 4 | @5 (n=1) | @5 (n=2) |
| 5 | @6 (n=1) | @6 (n=2) |
| 6 | @7 (n=1) | @7 (n=2) |
| 7 | @8 (n=1) | @8 (n=2) |
| 8 | @9 (n=1) | @9 (n=2) |
| 9 | @10 (n=1) | @10 (n=2) |
| 10 | @11 (n=1) | @11 (n=2) |

### `a22o_B2` — a22o.B2 (flop Q)

- k=1: [`stack_a22o_B2_k1.png`](stack_a22o_B2_k1.png)
- k=2: [`stack_a22o_B2_k2.png`](stack_a22o_B2_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @12 (n=1) | @12 (n=2) |
| 1 | @13 (n=1) | @13 (n=2) |
| 2 | @14 (n=1) | @14 (n=2) |
| 3 | @15 (n=1) | @15 (n=2) |
| 4 | @16 (n=1) | @16 (n=2) |
| 5 | @17 (n=1) | @17 (n=2) |
| 6 | @18 (n=1) | @18 (n=2) |
| 7 | @19 (n=1) | @19 (n=2) |
| 8 | @20 (n=1) | @20 (n=2) |
| 9 | @21 (n=1) | @21 (n=2) |
| 10 | @22 (n=1) | @22 (n=2) |

### `D_A2` — mux2_1_13.X → a22o.A2.D

- k=1: [`stack_D_A2_k1.png`](stack_D_A2_k1.png)
- k=2: [`stack_D_A2_k2.png`](stack_D_A2_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @0 (n=1) | @0 (n=2) |
| 1 | @1 (n=1) | @1 (n=2) |
| 2 | @2 (n=1) | @2 (n=2) |
| 3 | @3 (n=1) | @3 (n=2) |
| 4 | @4 (n=1) | @4 (n=2) |
| 5 | @5 (n=1) | @5 (n=2) |
| 6 | @6 (n=1) | @6 (n=2) |
| 7 | @7 (n=1) | @7 (n=2) |
| 8 | @8 (n=1) | @8 (n=2) |
| 9 | @9 (n=1) | @9 (n=2) |
| 10 | @10 (n=1) | @10 (n=2) |

### `D_B2` — mux2_1_11.X → a22o.B2.D

- k=1: [`stack_D_B2_k1.png`](stack_D_B2_k1.png)
- k=2: [`stack_D_B2_k2.png`](stack_D_B2_k2.png)

| start | k1 first≠ | k2 first≠ |
|------:|----------:|----------:|
| 0 | @11 (n=1) | @11 (n=2) |
| 1 | @12 (n=1) | @12 (n=2) |
| 2 | @13 (n=1) | @13 (n=2) |
| 3 | @14 (n=1) | @14 (n=2) |
| 4 | @15 (n=1) | @15 (n=2) |
| 5 | @16 (n=1) | @16 (n=2) |
| 6 | @17 (n=1) | @17 (n=2) |
| 7 | @18 (n=1) | @18 (n=2) |
| 8 | @19 (n=1) | @19 (n=2) |
| 9 | @20 (n=1) | @20 (n=2) |
| 10 | @21 (n=1) | @21 (n=2) |

Regenerate:
```bash
python3 phase3/a221o_set/run_I_dep_response_timelines.py
```
