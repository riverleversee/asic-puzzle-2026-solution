# netlist

Trusted Magic extract → structural Verilog.

```bash
# from rework_coded/
python3 netlist/run_generate.py
# or: python3 netlist/run_generate.py netlist/puzzle_gates.spice netlist/puzzle_structural.v
```

- `puzzle_gates.spice` — snapshot (not regenerated here)  
- `spice_to_structural_verilog.py` — generator  
- `puzzle_structural.v` — output  
- `puzzle_instances.csv` — die placement for phase1 maps  
