# Depth-4 fan-in maps for each depth-2 success net

Source cone: `rework/netlist/puzzle_structural.v` (from trusted `puzzle_gates.spice`).

Parent overview: [`success_fanin_depth2.png`](../success_fanin_depth2.png)

FA endpoints: [`../fa_endpoints.md`](../fa_endpoints.md)

Provenance: [`../PROVENANCE.md`](../PROVENANCE.md) · Gate reference: [`../gate_types.md`](../gate_types.md)

Depth-cut boxes tinted when deeper fan-in reaches an FA endpoint (`→FA`) and/or primary `I` (`→I`).
AO/OA edges are colored/labeled by pin group (A / B / C / D).
Layer order is pin-aware + barycentric (fewer crossings). Dashed crimson **↩** arcs are back-edges.

| Net | d from success | nodes behind | flops | leaves | figure |
|-----|---------------:|-------------:|------:|-------:|--------|
| `success` | 0 | 466 | 78 | 3 | [`d0_success_depth4.png`](d0_success_depth4.png) |
| `a32o_2_4__X` | 1 | 466 | 79 | 3 | [`d1_a32o_2_4__X_depth4.png`](d1_a32o_2_4__X_depth4.png) |
| `a32o_2_4__B2` | 2 | 36 | 10 | 1 | [`d2_a32o_2_4__B2_depth4.png`](d2_a32o_2_4__B2_depth4.png) |
| `and2_2_15__X` | 2 | 81 | 20 | 2 | [`d2_and2_2_15__X_depth4.png`](d2_and2_2_15__X_depth4.png) |
| `and4b_2_3__X` | 2 | 383 | 54 | 2 | [`d2_and4b_2_3__X_depth4.png`](d2_and4b_2_3__X_depth4.png) |
| `inv_2_23__A` | 2 | 65 | 22 | 3 | [`d2_inv_2_23__A_depth4.png`](d2_inv_2_23__A_depth4.png) |
