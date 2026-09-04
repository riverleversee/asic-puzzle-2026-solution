# Phase 1 checkpoint — netlist extract, convert, pattern-match figures

Restarted the trusted flow from GDS → gate SPICE → structural Verilog, re-ran operator pattern matching, and produced writeup figures.

**Rework outputs:** everything in this folder (`rework/phase1/`).  
**Canonical sim netlists:** `netlist/puzzle_gates.spice` + `netlist/structural/puzzle_structural.v`.

**Not used for rework:** `puzzle_core.v`, `puzzle_success_cone.v` (core-derived), behavioral `spice_to_verilog`.

## Commands run

```bash
# WSL — Magic reextract (GDS → spice → gates); structural convert
bash tools/reextract_puzzle.sh

python3 tools/spice_to_structural_verilog.py \
  netlist/puzzle_gates.spice \
  netlist/structural/puzzle_structural.v

export PATH="/home/levers/tools/oss-cad-suite/bin:$PATH"
python3 tools/run_puzzle_structural_all01.py

# Pattern match + figures from structural drivers
python3 tools/match_complex_operators.py
python3 tools/render_phase1_figures.py   # writes rework/phase1/figures/
```

Backup of prior netlist: `netlist/reextract_backup_20260902_230913/`.

## Artifacts

| Path | Role |
|------|------|
| `netlist/puzzle_gates.spice` | Gate-level SPICE (canonical sim input) |
| `netlist/structural/puzzle_structural.v` | Structural Verilog (**728** instances, **66** types) |
| `sim/structural_all01.md` | all0 / all1 sanity |
| `rework/phase1/operator_matches.*` | Pattern-match ranking (writeup copy) |
| `rework/phase1/figures/` | Writeup figures (PNG + SVG) |

## Sanity

```text
MODE=0 … MSG=…EMPTY SKY…
MODE=1 … MSG=…BIG BANG…
```

Fresh extract MD5-matched the pre-reextract backup (same netlist as the known solution).

## Figures

See [`figures/README.md`](figures/README.md).

| File | Caption |
|------|---------|
| `01_chip_overview` | Success path: I → SIPO → FA/phase → leaf checks → success |
| `02_operator_matches` | Ranked operator matches |
| `03_status_ab` | Status A / B SET window |
| `04_die_hotspots` | Combined die overview of strong matches |
| `die_maps_technical/` | One map per G_* grouping — original IDs / operator names |
| `die_maps_plain/` | Same maps — plain-language circuit purpose |

Seven per-group maps (score ≥ 0.8), styled like `04` (gray cone background, OG band, colored scatter + rounded callout).

```bash
python3 tools/render_phase1_figures.py
```
