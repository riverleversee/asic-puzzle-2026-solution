# Structural cone provenance

Standalone rework chain:

1. `rework/netlist/puzzle_gates.spice` (Magic extract snapshot)
2. `rework/tools/spice_to_structural_verilog.py` → `rework/netlist/puzzle_structural.v`
3. `rework/tools/structural_drivers.py` → driver map for fan-in diagrams

**Forbidden:** `puzzle_core.v`, behavioral `spice_to_verilog`, core-derived
`puzzle_success_cone.v`, stub_og stand-ins when expanding success fan-in.

## This run

- **source**: `netlist/puzzle_structural.v`
- **trusted**: `rework/netlist/puzzle_structural.v from puzzle_gates.spice`
- **instances_parsed**: `722`
- **driven_nets**: `722`
- **multi_output_cells**: `0`
- **has_success**: `True`
