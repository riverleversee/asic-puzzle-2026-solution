# Phase 1 figures

Writeup figures for the netlist → pattern-match checkpoint.

| File | Caption |
|------|---------|
| `01_chip_overview` | High-level success path. |
| `02_operator_matches` | Ranked operator fingerprint matches. |
| `03_status_ab` | Status A / B one-cycle SET window. |
| `04_die_hotspots` | Combined die overview of strong matches. |
| `die_maps_technical/` | **One map per grouping** — original IDs / operator names. |
| `die_maps_plain/` | **Same maps** — plain-language circuit purpose. |

Each stem is written as `.png` (200 dpi) and `.svg`.

## Top G_* matches (this run)

- **Hold (B2)** → Serial bit gather + parallel check (score 1.000, n=37)
- **Shift / SIPO bank** → Shift register / serial-in parallel-out (score 0.985, n=66)
- **Status A** → LFSR / CRC / linear feedback (score 0.959, n=34)
- **Status B** → LFSR / CRC / linear feedback (score 0.942, n=36)
- **SET AND path** → Serial bit gather + parallel check (score 0.937, n=82)
