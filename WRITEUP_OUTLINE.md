# Writeup outline — ASIC Puzzle 2026 (`rework_coded` path)

Outline for the Jane Street “how we solved it” note. Repo spine: `rework_coded/`
(generators live next to their results). Structural sims via Icarus + Sky130 PDK.

**Claimed I pattern (22 ones, period-11 exact-2):**
`[7, 9, 11, 16, 29, 31, 33, 35, 48, 50, 57, 63, 70, 76, 78, 83, 91, 98, 104, 107, 111, 113]`

---

## 0. One-paragraph arc

GDS → SPICE → structural Verilog → map the success tree → find FA / leaf /
sticky machines → lock per-subsystem **I rules** with targeted sims →
combine rules in a **forcer** that uniquely determines the 121-cycle `I`
bitstream → (verify `success` under the puzzle’s enable timing).

---

## 1. Netlist provenance

| Step | Code | In → out |
|------|------|----------|
| Magic gate extract (snapshot) | — | `netlist/puzzle_gates.spice` |
| SPICE → structural Verilog | `netlist/spice_to_structural_verilog.py` (wrapper `netlist/run_generate.py`) | `puzzle_gates.spice` → `netlist/puzzle_structural.v` |

`spice_to_structural_verilog.py` specifics — worth a sentence in the writeup
because it is the whole trust argument:

- Reads `.subckt` **pin lists** so instances are emitted with *named* port
  connections, not positional guesses.
- Keeps power pins only for position mapping, then drops them; a signal pin tied
  to `VGND`/`VNB` becomes `1'b0`, to `VPWR`/`VPB` becomes `1'b1`.
- Skips `fill` / `decap` / `tap` / `diode` instances.
- Net-name mangling `vnet()`: `/`→`__`, `[n]`→`_n`, other chars→`_`. This is why
  every net in the sims reads like `sky130_fd_sc_hd__and4_2_3__X`.
- **No behavioral rewrite.** Cell semantics come from the official
  `sky130_fd_sc_hd` Verilog models at compile time, not from hand-written
  equations.

**Explicitly not used** (the “forbidden” list `structural_drivers.write_provenance()`
prints): `puzzle_core.v`, the behavioral `spice_to_verilog` output, the
core-derived `puzzle_success_cone.v`, and `stub_og` stand-ins when expanding the
success fan-in.

**Not self-contained:** `rework_coded/` reads two things from the parent repo —
the PDK at `../netlist/structural/pdk` and the leaf open schedules in `../sim/`.
Say this plainly rather than implying the folder is standalone.

---

## 2. Tooling

### 2.1 Static tracing tools (`lib/`)

These are the tools the structural reading is built on. All of them work off the
driver map — none of them read a simulation.

| Tool | What it does | Uses |
|------|--------------|------|
| `lib/structural_drivers.py` | Parses `puzzle_structural.v` into the **driver map**: net → `{deps, in_pins (pin→net), rhs, kind, cell, instance, class}`. `classify_cell()` buckets cells into flop / mux / xor / xnor / nand / and / nor / or / buf / aoi / inv. `is_clk()` masks clock nets so cones stay data-only. `write_provenance()` emits the trust chain + forbidden list. | `netlist/puzzle_structural.v` |
| `lib/render_success_logic_depth.py` | The main **cone tracer / schematic renderer** — every `*_fanin_depth<N>` figure in the tree. Detailed in §2.4. | driver map, `phase2/fa_endpoints.json` |
| `lib/identify_fa_endpoints.py` | Finds **full-adder endpoints**: an XOR/XNOR (sum) greedily paired with the AO/OA/maj (carry) sharing the most data inputs, accepted at **≥2 shared inputs**. | driver map → `phase2/fa_endpoints.{json,md}` |
| `lib/ao_oa_labels.py` | Formula table for the compound cells (`a221o` → `(A1∧A2)∨(B1∧B2)∨C1`, `o21ai` → `¬((A1∨A2)∧B1)`, …), pin-group edge colours A/B/C/D, mux pin styling. Makes the diagrams readable as logic rather than blobs. | — (static table) |
| `lib/structures/` | **Pattern recognizer.** `graph.py` (`Match`, `fanin_cone`), `catalog.py` (templates), `recognize.py` (run matchers → filter to cone → greedy non-overlapping cover), `render_blocks.py`. Cover priority: `enabled_mux_shift_register` 100, `sticky_ao_latch` 90, `andN_flopped_inputs` 80, `mux_hold_flop_stage` 50, `and2b_enable_gate` 40, `inv_on_flop_Q` 35, `nand2_I_gate` 30, `fa_prior_stub_driver` 20. Reports cone coverage fraction + uncovered nets. | driver map |
| `phase2/and2_2_15/and4_2_3/pin_i_hop_rule.py` | **Watch-eligibility rule** (kept us from chasing irrelevant pins). A net is watchable iff it reaches `I`, *or* it does not reach `I` but directly feeds an `I`-reaching gate. Anything deeper on a non-`I` branch is out. `classify_net()` returns the reason: `reaches_I` / `feeds_I_parent` / `deeper_non_I`. | driver map |
| `phase3/a221o_set/trace_I_comparisons.py` | Finds **I-vs-I comparison sites** along `a221o.A2/B2/C1` and `a22o.A2/B2`: a `mux2` with *both* `A0` and `A1` reaching `I`, or a `xor`/`xnor` with both data inputs reaching `I`. | driver map |
| `phase3/a221o_set/match_known_delay_structures.py` | **Structural template check**, not a “looks like a delay in sim” claim. Templates: `enabled_mux_shift_register` (expected to match — per stage `mux.S=S_common`, `mux.A1=din`, `mux.A0=Q_i`, `flop.D=mux.X`), `plain_dff_chain` (must *not* match), `fa_xor_arith_path` (counter-example). Netlist either satisfies the pin rules or it doesn’t. | driver map |
| `lib/rework_paths.py` | `find_rework()` root discovery (keys on `netlist/` + `phase3/`); `savefig_locked()` writes a PNG via temp name and falls back to `*_updated.png` when Windows has the target locked. | — |
| `lib/rc_paths.py` | The *other* root finder: `coded_root()` keys on `lib/` + `netlist/` + `phase1/`, and `ensure_lib()` puts `lib/` on `sys.path`. Two root-finders with different keys coexist — worth naming so a reviewer running a script from the wrong directory knows which one failed. | — |
| `verify_vs_golden.py` | Diffs `rework_coded/` text artifacts against the golden `rework/` tree with path mapping + normalization (markdown links, `summary.json` `source`, unordered FA-pair lists, `cell_counts` key order). | both trees |

Root-discovery idiom repeated across phase2/3 scripts: walk up from `__file__`
until a directory contains **both** `lib/` and `netlist/`.

### 2.2 Sim construction

**Shared harness:** `lib/probe_timeline.py` → `run_probe(root, build, out_dir, tag, probes, modes, n_cyc)`.
It generates a testbench, compiles, runs, and returns parsed CSV rows. The
generated artifacts land in `phase2/build/` or `phase3/build/` as
`tb_<tag>.v`, `tb_<tag>.vvp`, `pats_<tag>.txt`, `probe_<tag>.csv`.

The module exports exactly three things to callers: `run_probe()` (collect),
`pat_bits()` (build a pattern string from a list of one-cycles), and
`ones(rows, key)` (project a probe column down to the list of cycles where it
was high). That last one is what every timeline summary table is computed from,
though several scripts inline the equivalent comprehension instead.

**Compile line** (`iverilog_cmd()`):

```
iverilog -g2012 -DFUNCTIONAL -DUNIT_DELAY=#1 -I <pdk>/include \
         <only the cell models actually instantiated> \
         netlist/puzzle_structural.v build/tb_<tag>.v
```

`cells_used()` regexes `sky130_fd_sc_hd__\w+_\d+` out of the structural Verilog
and resolves each to `pdk/cells/<family>/<cell>.v`, where `family()` strips the
trailing `_<drive>`. Only those models are compiled, which is what keeps a
121-cycle × N-mode sweep fast.

`find_iverilog()` (in `lib/run_sim.py`) probes `~/tools/oss-cad-suite/bin`,
`~/oss-cad-suite/bin`, `/opt/oss-cad-suite/bin`, then `PATH`. **Gotcha for
reviewers:** `lib/run_sim.py`’s `main()` is a deliberately disabled legacy
entrypoint (the behavioral `puzzle_full.v` was removed as untrustworthy); only
`find_iverilog()` is ever imported from it.

**Testbench shape** (identical in the shared harness and the phase-3 scripts):

```verilog
`timescale 1ns/1ps
always #5 clk = ~clk;              // 10 ns period

rst_n=0; enable=0; I=0;
repeat(3) @(posedge clk);
rst_n=1;  @(posedge clk);
enable=1;                          // I bit 0 lands on the first enable-high edge
for (cyc=0; cyc<N_CYC; cyc=cyc+1) begin
  @(negedge clk);  I = <bit cyc>;  // drive on NEGEDGE
  @(posedge clk);  #1;             // settle, then sample every probe
  <write one CSV row: mode, cyc, probes…>
end
```

Points to make explicitly in the writeup:

- **Negedge `I` drive is deliberate.** With `-DUNIT_DELAY=#1` the clock tree
  delays the flop clock by 1 ns. Driving `I` on the posedge gives nets 1 gate
  from `I` the edge but makes nets 2 gates away miss it, putting two constraint
  families a full cycle apart. Negedge drive gives every path half a clock of
  setup. (Diagnosis in `../sim/fold_repair_and_timebase.md`,
  `../sim/properly_timed_harness.md`.)
- **`enable` rises one cycle after reset release and then stays high** for the
  whole `N_CYC` window; bit 0 of the pattern is sampled on the same edge
  `enable` first goes high. Matches the contest `example_inputs.vcd`
  (`../sim/I_enable_alignment.md`).
- **Sample point is `#1` after the posedge**, so a row records post-edge state.
- **Batched modes.** One compiled `.vvp` runs every pattern in `modes`
  back-to-back, each preceded by its own reset sequence; the CSV carries a
  `mode` column and `run_probe()` re-attaches the human-readable mode name. This
  is why the sweeps could afford hundreds of patterns per script.
- **Probe list is `(csv_label, net)`.** `I` and `enable` are read as testbench
  regs; everything else is dumped as `uut.<net>` using the mangled flat name.
- **`n_cyc` is a parameter, not a constant.** Most sweeps use 121. The
  `and4_2_3` report deliberately runs 125 (121 + 4) — see §5.3.

**Two bit-order conventions, both self-consistent.** This bit a reader will
get wrong if it isn’t spelled out, because `$readmemb` treats the leftmost
character as the MSB of the word:

| Builder | String layout | TB index | Net effect |
|---------|---------------|----------|-----------|
| `probe_timeline.pat_bits()` | char `i` = cycle `i` (cycle 0 leftmost) | `pat[mode][N_CYC-1-cyc]` | cycle `i` ← reg bit `N-1-i` |
| phase-3 `bits_from_ones()` = `format(Σ 1<<c, '0121b')` | MSB-first, so reg bit `k` = cycle `k` | `pat[mode][cyc]` | cycle `i` ← reg bit `i` |

Both land the same cycle on the same edge; they just index from opposite ends.
Any new script must match the convention of the pattern builder it uses.

### 2.3 Timeline rendering & output convention

**There is no shared timeline renderer.** `probe_timeline.py` stops at the data;
every sweep script builds its own matplotlib figure. The only surface the
timeline scripts genuinely share is `run_probe` / `pat_bits` / `ones`,
`savefig_locked`, and root discovery. Say this rather than implying a plotting
library exists — it explains why the figures differ slightly between folders.

**Every sweep emits a triple**, `timelines/<stem>.{csv,png,md}`:

- **`.csv`** is *not* the raw probe dump. Scripts re-project `build/probe_<tag>.csv`
  into per-suite columns using display labels. Probe columns are auto-named and
  deduped across lanes (`all_probes()` tags them per pin, e.g. `dfrtp_`→`f`,
  `nor3_`→`n`), so `lab_for()` maps a display lane name back to its CSV column.
  CSV column names deliberately differ from figure labels.
- **`.png`** is the lane plot (below).
- **`.md`** is the human-readable evidence page (below).

**Lane-plot convention**, using `write_suite()` in
`phase2/and2_2_15/and4_2_3/run_i_suites_all_pins.py` as the reference
implementation:

- One subplot per pattern mode, `sharex=True` on the cycle axis, ~1.35 in of
  height per mode, so a suite reads top-to-bottom as one experiment.
- Inside a subplot, one horizontal lane per probed net; a `barh` of width 1 is
  drawn at every cycle where that net is high. Lanes are drawn reversed so the
  first-declared lane sits at the top.
- The **key lane** — the pin whose behaviour the suite is actually testing, e.g.
  the one gating `and4.X` — gets a yellow `Rectangle` band with a red edge
  spanning the full cycle range, a ★ on its tick, and a bold dark-red tick
  label. This is the “where to look” marker in every figure.
- A faint red `axvline` at each `I=1` cycle; per-window suites add dotted
  period-11 boundaries.
- **The subplot title carries the actual result:** `#I`, the key lane’s high
  count, its first high cycle, and the `and4.X` high count. When quoting a
  figure in the writeup, that title line is the claim.

**Markdown companion** contains: which lane is highlighted and why, links to the
`.png` and `.csv`, an **Observe summary** table (`mode | #I | key n | first |
and4.X n`) that is the compact pass/fail evidence, then per-mode lane listings
of high cycles (long lists truncated by `fmt(xs, lim=24)`), a link back to the
parent README, and the exact command to reproduce it.

**Generated index pages.** `update_pin_readme()` rewrites a
`## Timelines (I-pattern suite)` block in each pin folder’s `README.md` with
links to every stem. Those per-pin index pages are build artifacts, not
hand-written notes — don’t cite them as commentary.

Phase-3 timeline scripts follow the same triple + lane idea but roll their own
figure code against their own testbenches (§5), which is why e.g. `open_log.md`
and `k_ones_flops.md` look related but not identical to the phase-2 pages.

### 2.4 Logic-node schematic generator

`lib/render_success_logic_depth.py` is the single generator behind **every**
`*_fanin_depth<N>.{png,svg,md}` in the tree. Unlike the timelines there *is* one
shared implementation here; the phase-2 `expand_*.py` scripts are thin wrappers
that import `render_one()` and call it with a chosen root, depth, and title.

**Entry points.** `render_one(root, drivers, stubs, max_depth, out, *,
with_behind, fa_ends, title, only_i)`, or the CLI:

```bash
python3 lib/render_success_logic_depth.py --root <net> --depth 5 --behind-counts
python3 lib/render_success_logic_depth.py --bundle
```

`--depth` defaults to 2, `--root` to `success`. Default output directory is
`phase2/success/`; the filename is `_stem(root) + "_fanin_depth<N>.png"`, which
is where names like `and4_2_3__X_fanin_depth5.png` come from.

**Graph construction.** `fanin_bounded()` does a bounded-depth BFS back from the
root over data dependencies only (`_data_deps` drops clock nets and `rst_n`).
Two things make the figures legible rather than hairballs:

- **only-I protocol** (`only_i=True`, what the phase-2 expands use). Any
  dependency whose fan-in never reaches primary `I` is *not* expanded — it is
  drawn once as a collapsed `i_stub`. This is the visual counterpart of the
  `pin_i_hop_rule` watch rule.
- **Depth cutting is annotated, not silent.** `reach_tags()` labels every
  frontier net with whether its hidden fan-in still reaches an FA endpoint
  and/or primary `I`, so a truncated drawing tells you what it hid.

**Layout.** `layout_layers()` assigns layers by depth, `_seed_layer_order()`
seeds within-layer order, and `_barycenter()` / `_reduce_crossings()` iterate to
cut edge crossings. `_pin_rank()` and `_dep_order_key()` order a gate's inputs by
pin letter so AO/OA groups (`A1 A2 | B1 B2 | C1`) stay visually adjacent, and
`_edge_kind()` classifies back-edges (the console prints how many).

**Rendering details worth one sentence in the writeup:** compound cells get their
formula printed on the node box from `ao_oa_labels.AO_OA_FORMULA`, edges are
coloured by pin group and labelled with the destination pin, and node colour
encodes cell class (flop / and / or / xor / aoi / mux / inv / leaf / primary).
So the pictures are readable as logic, not just connectivity.

**Outputs per invocation — a triple, like the timelines:**

- **`.png`** at `dpi=200`, tight bbox, white background.
- **`.svg`** alongside, automatically, same name.
- **`.md`** companion from `write_summary()` — this is the citable artifact:
  header counts (root, visible nodes, edges, nodes truncated at the cut, count
  and list of stubbed non-`I` nets), then a **Stubbed non-I inputs** table
  (net, driver instance, collapsed pins, depth, nodes behind), a **Depth-cut
  reachability** table (net, →FA, →I, sample FA hits, stub flag), optionally a
  **Behind counts** table (nodes / flops / leaves / primaries / undriven behind
  each visible net, from `count_behind()`, enabled by `--behind-counts`), and a
  **Nodes by depth** listing.

**`--bundle` mode** (`run_bundle()`) is the one-shot survey: a depth-2 overview
at `phase2/success/success_fanin_depth2.{png,svg,md}`, then a depth-4 map per
visible net into `phase2/success/fanin_depth4_from_depth2/`, plus a generated
`README.md` index table linking them. Each per-net page cross-links the parent
overview, `phase2/fa_endpoints.md`, `phase2/PROVENANCE.md`, and
`phase2/gate_types.md` — so provenance rides along with every figure.

**Note for anyone re-running this:** it has its own write workaround (tempfile +
`copyfile`, because WSL writing to `/mnt/c` can raise `OSError 22` on overwrite),
which is separate from `rework_paths.savefig_locked()` used by the timeline
scripts. Two different fixes for two different Windows/WSL write failures.

---

## 3. Phase 1 — operators & die context

**Goal:** recognize complex cells / layout neighborhoods.

| Built | Uses → produces |
|-------|-----------------|
| `phase1/match_complex_operators.py` (wrapper `run_match.py`) | driver map + `phase1/complex_operators_db.json` → `phase1/operator_matches.{json,md,txt}` |
| `phase1/render_phase1_figures.py` (wrapper `run_figures.py`) | operator matches + layout → `phase1/figures/` |

**Explored:** FA-like clusters, sticky AO/OA families, die maps (plain + technical).

---

## 4. Phase 2 — success tree fan-in (visual structure)

**Goal:** expand only-`I` cones from `success` and the key joins; label stubs vs
`I`-reaching nets. Every folder holds its generator next to its `.md`/`.png`.

### 4.1 Success entry

```text
success ← … ← and2_2_15.X = inv_2_6.Y ∧ and4_2_3.X
```

| Area | Path | Generator |
|------|------|-----------|
| Success fan-in bundles | `phase2/success/` | `render_success_logic_depth.py`, `run_bundle.py` |
| FA endpoints | `phase2/fa_endpoints.{json,md}` | `phase2/identify_fa_endpoints.py`, `run_fa.py` |
| Join AND expand | `phase2/and2_2_15/` | `expand_and2_15.py`, `run_count_pre_and4.py` |
| A-arm (`inv_2_6` / fail sticky) | `phase2/and2_2_15/inv_2_6/` (+ `o211a_2_8/`) | `expand_o211a.py`, `run_recognize_structures.py` |
| B-arm (`and4_2_3`) | `phase2/and2_2_15/and4_2_3/` | `expand_pin_subs.py`, `run_recognize_structures.py` |
| Pin folders A/B/C/D | `dfrtp_2_24/`, `dfrtp_2_25/`, `dfrtp_2_20/`, `nor3_2_2/` (+ `or3_2_8_B/`) | per-folder `run.py`, `expand_or3_2_8_B.py` |
| SET path behind `inv_2_23` | `phase2/a221o_behind_inv23/` | `expand_inv23.py` |
| and4b leaf taxonomy | `phase2/and4b/behind/`, `phase2/and4b/groups/t01…t08/` | `render_strong_group_backtrees.py`, `compare_and2b_behind_and4b.py`, `expand_and4b_main_groups.py` |

### 4.2 Timeline sims run here

All collect via `lib/probe_timeline.py` and emit the
`timelines/<stem>.{csv,png,md}` triple described in §2.3.

- **No-`I` / stub baselines** — `run_noI_stub_timeline.py` (in `inv_2_6/` and
  `a221o_behind_inv23/`). Establishes what moves with `I` held at 0.
- **Single-`I` probes** — `inv_2_6/run_I1_probe_timeline.py`.
- **Spacing sweeps** — `run_I2_I3_spacing_timeline.py`,
  `run_I2_I3_from30_timeline.py`, `run_I2_I3_from75_timeline.py`,
  `run_I4eq_delta_timeline.py` (same family duplicated under `inv_2_6/` and
  `inv_2_6/o211a_2_8/` so each subsystem has its own evidence).
- **Per-window sweeps** — `run_I2_every_window_timeline.py`,
  `run_Ik_all11_timeline.py`, `and4_2_3/run_I2win_perwindow_rand_timeline.py`,
  `run_I2win_rand_spacing_timeline.py`.
- **Random-spacing sweeps** — `run_Ik_random_spacing_all_pins.py`,
  `nor3_2_2/run_Ik_random_spacing_timeline.py`.
- **All-pin suites / watches** — `and4_2_3/run_i_suites_all_pins.py`,
  `run_and4_inputs_timeline.py`, `run_active_watches_timeline.py`,
  `inv_2_6/run_mux_pins_I123_from2_timeline.py`.
- **and4.A extended horizon** — `dfrtp_2_24/run_I2win_extended_report.py` at
  `n_cyc=125` → `dfrtp_2_24/reports/I2win_2per_extended.{csv,md}`. This one
  consolidated and replaced a batch of exploratory `run_I2win_*` scripts.

**Key structural takes:**
- Fail sticky on the A-arm, gated by mux / period-11 FA edge.
- SET sticky on the `a221o` shift taps (+1/+10/+11/+12) plus FA gates.
- `and4b` hasI leaves are `set_once` / `sticky_or` families with FA **open windows**.
- Pin-watch hygiene: ≤1 hop from `I`-reaching nets (`pin_i_hop_rule.py`).

---

## 5. Phase 3 — confirm rules with sims

**Goal:** turn structure into hard constraints on `I`. Each subsystem gets a
`rules/*.txt` file that is the deliverable; the sims are the evidence.

Phase-3 sims build their own testbenches (same shape as §2.2) rather than going
through `probe_timeline`, and read the leaf schedules from the parent repo:
`../sim/opens_exact_shift1.json`, `../sim/retrace_all22_opens_structural.json`,
plus `phase2/and4b/groups/summary.json` for group membership. Leaf naming comes
from an `OUT_TO_LEAF` map (`and4_2_0__A` → `slot.0.A`, `and4_2_5__D` → `a5.D`,
`and3_2_12__C` → `a12.C`, …).

### 5.1 and4b leaves (22 hasI)

| Rule | File |
|------|------|
| Exactly **2** ones on each leaf’s FA opens; gaps don’t matter; k≠2 fails | `phase3/and4b/groups/rules/and2b_set_once_t01_t02_t05.txt`, `and2_sticky_or_t03_t04.txt` |

**Sims:** `phase3_and4_I_group_opens.py` (`run_opens.py`) logs each leaf’s open
entry and writes `open_log.md`; `phase3_k_ones_flops_timeline.py`
(`run_k_ones.py`) puts `I=1` on the first *k* open cycles and watches the leaf
input pins (`A_N`/`B` for and2b, `A`/`B` for and2) plus leaf `Y`;
`phase3_two_ones_open_gaps.py` and `phase3_ones_gap_variants.py` sweep gaps;
`phase3_or4b_nand2_I_opens.py`, `phase3_fa_input_to_nand2.py`, and
`flop_init_all0/phase3_flop_init_all0.py` pin down the open mechanism and the
post-reset state. Deep dive on one group in
`t01_…_shallow_27n/a5A/` (`phase3_a5A_k2_k3_timeline.py`,
`phase3_a5A_two_flops_vs_I.py`, `phase3_timeline_and2b_25_ffs.py`).

### 5.2 SET path (`inv_2_23` / a221o)

| Rule | File |
|------|------|
| Neighbor / fold Δ∈{1,10,11,12}; allowed later windows ≡0 / ≡10 / never (Δ=11) — measured sticky | `phase3/a221o_set/rules/a31o_sticky_set_spacing.txt` (evidence: `fold_windows/`) |

**Sims / structure:** `run_I_dep_a221o_pins.py`, `run_I_dep_a22o_pins.py`,
`run_I_dep_response_timelines.py`, `run_shift_chain_inspect.py`, plus the two
static tools `trace_I_comparisons.py` and `match_known_delay_structures.py`
(§2.1). The rule file also records the **FA phase schedule** — `or4_2_4` ABCD by
`cyc mod 11`, with the all-zero phase at 10.

**Note:** same mechanism as the earlier `inv11` hot-offset; the forcer uses the
**forbid** form (unsafe partner → 0), the SET arm the **rise** form.

### 5.3 Success-entry AND (`and2_2_15`)

| Rule | File |
|------|------|
| Fail sticky trips @ cyc≡10 mod 11 unless mux inhibit | `phase3/and2_2_15/rules/a31o_2_11_fail_trip_mux_gate.txt` |
| **Exactly 2** ones per period-11 cycle inhibit fail | `mux_period11_two_ones_inhibit.txt` |
| **Exactly 2** per cycle also satisfies the and4 arm | `and4_2_3_two_per_cycle.txt` |

**Sims:** `run_mux_dependence_figure.py`; `inv_2_6/run_I2_every_window_timeline.py`;
and the `and4.A` exhaustive + per-window random sweep at `n_cyc=125`
(`phase2/.../dfrtp_2_24/run_I2win_extended_report.py`).

**Horizon lesson worth its own paragraph in the writeup.** At `n_cyc=121`,
`I@120` looked like a hard failure for the and4 arm. It was a truncation
artifact: `and4.X` rises on cycle 121, one cycle past the end of the driven
window. With the horizon extended, all 213 modes pass and placement inside the
period-11 cycle stops mattering — which is what collapsed the rule from a
fragile intra-cycle spacing story to a plain **total-ones budget**
(2 × 11 = 22 ones over 0..120).

### 5.4 Misc

- `phase3/nand2b_B2/` — success-path peer watches
  (`phase3_confirm_nand2b_no_I.py`, `phase3_watch_nand2b.py`).
- Watch rule written up as `phase3/and2_2_15/rules/pin_watch_1hop_to_I.txt`.

---

## 6. Phase 4 — combine rules → forced `I`

| Built | Path | Uses |
|-------|------|------|
| Forcer | `phase4/run_forcer.py` | `../sim/opens_exact_shift1.json` (fallback `../sim/retrace_all22_opens_structural.json`); compares against `../sim/cpsat_exact.json` |
| Rule alignment note | `phase4/RULES_ALIGN.md` | — |
| Window cross-check helper | `phase4/_cmp_set_inv11_windows.py` | `probe_all22_opens.csv` — recovers the `or4_2_4` ABCD-by-phase schedule and lines the SET gate windows up against the `inv11`-safe cycles |
| Sim wrapper | `phase4/sim_solution.py` | `phase4/out/forced.json` + `lib/probe_timeline.py`, `n_cyc=125` |
| Forced solution | `phase4/out/forced.{json,md}` | — |
| Fill GIFs | `phase4/out/solver_fill_11x11.gif`, `solver_fill_timeline.gif` | **copies** — generated by `../tools/plot_solver_fill_gif.py` and `../tools/plot_solver_fill_timeline_gif.py` |

### 6.1 What the forcer actually enforces

Leaf records are read as `{name, kind, bank, opens}` where `opens` prefers
`opens_all0`. The 22 leaves split evenly: `bank=main` (11 — `slot.0.A–D`,
`slot.1.A–D`, `and3.A–C`) and `bank=and4b_D` (11 — `a5.A–D`, `a6.A–D`,
`a12.A–C`); mains are processed shortest-open-list first.

1. **Leaf Σ=2** — every hasI leaf takes exactly 2 ones on its FA opens
   (this *is* the “slot oracle”, not a separate constraint).
2. **Period-11 exactly 2** — `≤2` while a window is still partial, and once a
   window holds 2 forced ones the rest of that window is zeroed.
3. **a221o hot-offset** — for Δ∈{1,10,11,12}, force the partner to 0 unless the
   later cycle sits on the allowed window (`later_allowed()`).
4. **D-hold** — when an `and4b_D` leaf reaches Σ=2, its remaining opens go to 0.

Structure: `close_force()` runs zero-propagation plus the period rule to a
fixpoint; `fixpoint_k()` enumerates every legal pick for groups of *k* leaves,
keeps the survivors that pass `survivor_ok()`, and locks whatever **all**
survivors agree on. Combinatorial guard `MAX_COMBOS = 500_000`, with a
`SKIP_TOO_MANY` status rather than a hang.

### 6.2 Result

22 ones / 99 zeros / **0 unidentified**; every period-11 window at exactly 2.

Sweep counts from `out/forced.md` are `{'solo': 5, 'pairs': 1}`: the *k*=1
stage reached its fixpoint in 5 sweeps and fully determined the pattern, and
the *k*=2 stage then ran one confirming sweep that added **no** new locks.
The *k*=3 stage was never run — the recorded invocation is `--skip-triples`.
So the honest claim is “single-leaf propagation was sufficient, pairs confirmed
the fixpoint,” not “doubles were needed.”

The output matches `../sim/cpsat_exact.json` bit-for-bit. Be precise about what
that comparison is worth: that CP-SAT run was handed `force_1_in` (all 22 ones)
and `force_0_in` (99 zeros) from `sim/solver_forced_exact.json` with
`free_cycles=[120]`, so it *confirmed* a pattern rather than searched for one
(`status: OPTIMAL`, `objective: 22`, `new_assignments: {}`, `wall_s ≈ 0.014`).
The phase-4 forcer starts from an empty assignment and derives all 121 bits from
the four rules, so the agreement is a genuine independent rederivation — which
is the stronger sentence for the writeup.

**Opens timebase — cite it explicitly.** `../sim/opens_exact_shift1.json` is
`schema 1`, `method: "OPEN_SHIFT=+1 from structural measured opens"`, derived
from `retrace_all22_opens_structural.json`. Each leaf carries `opens_measured`
alongside the shifted `opens_all0` / `opens_all1`, and the file's own note
points at `sim/fold_repair_and_timebase.md` and `tools/exact_model.py`. The
`+1` is a timebase correction, not a re-measurement.

---

## 7. Paths explored but not in the final constraint set

Worth a short “what we tried” paragraph:

- Early behavioral / CP-SAT / status-B searches under the parent `tools/`
  (pre-rework or parallel).
- The `and4.A` “last-entry fail” at `n_cyc=121` — horizon artifact (§5.3).
- Hand-written `FoldInv11` model — replaced by netlist-derived simulation after
  it was shown to miss real `inv11` trips.
- Forcer without the hot-offset rule — under-constrained and far slower, since
  the pair/triple stages explode without that pruning.
- Deep expands of every `and4` pin — good for intuition; the leaf opens plus the
  period rule carried the actual solve.
- Neighbor-freeze heuristics beyond the a221o Δ windows — dropped once the
  windows were explicit.

---

## 8. Suggested writeup section order (Jane Street)

1. **Setup** — GDS → SPICE → structural Verilog; what `I` / `enable` / `success`
   are; why cell models come from the PDK and not from us.
2. **Harness** — negedge `I` drive, `enable` alignment to the contest VCD, the
   `#1`-after-posedge sample, and the setup-time race that forced it.
3. **Architecture** — `success` = AND of the fail-cleared A-arm and the `and4`
   B-arm; SET sticky; 22 FA leaves.
4. **Leaf rule** — exactly two ones on each leaf’s open windows (evidence:
   k-ones and gap sims).
5. **Period-11 rule** — exactly two ones every 11 cycles (fail inhibit + and4),
   including the horizon lesson.
6. **Fold / neighbor rule** — no Δ∈{1,10,11,12} pair unless the later cycle is
   on the allowed window (Δ=11 never).
7. **Solver** — propagate forced 0/1 from those four rules; single-leaf
   propagation alone pins all 121 bits.
8. **Verification** — structural sim of the bitstream; leaf PASS; `success` /
   message under the enable protocol.
9. **Artifacts** — `rework_coded/phase3/**/rules/`, `phase4/out/`, the GIFs.

---

## 9. Status / honesty checklist before submit

- [ ] Confirm the structural sim uses the **correct bit-order for its pattern
      builder** (§2.2 table) and an `enable` protocol matching the contest
      harness (121 driven cycles, then off).
- [ ] Confirm `success=1`. The prior cpsat structural run had leaves 22/22 and
      MSG `(* TWO STARS *)` but reported `success=0` under that testbench —
      resolve the enable/sample edge if still open.
- [ ] Sim a few cycles past 121 whenever quoting `and4.X`.
- [ ] Cite the opens timebase (`opens_exact_shift1`, `OPEN_SHIFT=+1`) explicitly.
- [ ] State that the PDK and `../sim/*.json` come from the parent repo.
- [ ] Label the phase-4 GIFs as copies of parent-repo `tools/` output.

---

## 10. Quick file index for reviewers

```text
rework_coded/
  netlist/                spice_to_structural_verilog.py → puzzle_structural.v
  lib/
    structural_drivers.py       driver map (all tracing starts here)
    render_success_logic_depth.py  cone tracer + schematic renderer
    identify_fa_endpoints.py    FA sum/carry pairing
    ao_oa_labels.py             compound-cell formulas
    structures/                 pattern catalog + greedy cover
    probe_timeline.py           shared Icarus probe harness (run_probe/pat_bits/ones)
    rework_paths.py             phase3 root discovery, Windows-safe savefig
    rc_paths.py                 phase1/2 root discovery + sys.path setup
  phase1/                 operator match + die maps
  phase2/                 fan-in expands + I timelines (generator next to output)
  phase3/**/rules/        locked constraints (the deliverable)
  phase4/                 forcer + forced I + sim wrapper + GIFs
  verify_vs_golden.py     diff against golden rework/ tree
```
