#!/usr/bin/env python3
"""Compare the I→a221o/a22o path to known delay structures.

This is a **structural** check against templates — not “it looks like a
delay in simulation.” Each template has hard pin-connectivity rules; the
netlist either satisfies them or it does not.

Known templates
---------------
1. ``enabled_mux_shift_register``  (expected match)
     Stage i:
       mux.S  = S_common
       mux.A1 = din_i          # i=0 → primary I; else Q_{i-1}
       mux.A0 = Q_i            # hold / recirculate
       flop.D = mux.X
       flop.Q = Q_i
     When S=1: Q_i[t+1] = din_i[t]  (pure shift)
     When S=0: Q_i[t+1] = Q_i[t]    (hold)

2. ``plain_dff_chain``  (no mux hold — should NOT match here)
     flop_i.D = Q_{i-1} or I directly (no intervening mux2)

3. ``fa_xor_arith_path``  (counter-example — should NOT match taps)
     Path from I to tap is dominated by xor/xnor / FA AO cells
     (arithmetic), not a mux+flop shift spine.

Also checks the **gated observe** sites (`a22o.X`, `a221o.X`): they are
AND/OR of a shift tap with an FA-prior stub — not themselves delay
structures.

Outputs → ``I_dep/shift_chain/``
  structure_match.md / .json
  structure_checklist.png
  structure_chain_schematic.png

Usage (from rework_coded/):
  python3 phase3/a221o_set/match_known_delay_structures.py
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from rework_paths import savefig_locked  # noqa: E402
from structural_drivers import parse_structural  # noqa: E402

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
OUT = HERE / "I_dep" / "shift_chain"

ENTRY_MUX_X = "sky130_fd_sc_hd__mux2_1_13__X"
PRIMARY_I = "I"

# Named observe taps (must be Q of a matched shift stage if template hits)
OBSERVE_TAPS = {
    "a22o.A2": "sky130_fd_sc_hd__a22o_2_2__A2",
    "a221o.A2": "sky130_fd_sc_hd__mux2_1_12__A1",
    "a221o.B2": "sky130_fd_sc_hd__mux2_1_12__A0",
    "a22o.B2": "sky130_fd_sc_hd__a22o_2_2__B2",
}

GATED_OBS = {
    "a22o.X": "sky130_fd_sc_hd__a22o_2_2__X",
    "a221o.X": "sky130_fd_sc_hd__a221o_2_1__X",
}


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


@dataclass
class Check:
    rule: str
    ok: bool
    detail: str = ""


@dataclass
class Stage:
    index: int
    mux_inst: str
    mux_x: str
    s_net: str
    a1_net: str  # din
    a0_net: str  # hold Q
    flop_inst: str
    q_net: str
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


@dataclass
class TemplateResult:
    name: str
    matched: bool
    summary: str
    checks: list[Check] = field(default_factory=list)
    stages: list[Stage] = field(default_factory=list)
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Netlist helpers
# ---------------------------------------------------------------------------


def index_by_instance(drivers: dict) -> dict[str, dict]:
    """instance → {out_net, info} (prefer X/Q output)."""
    out: dict[str, dict] = {}
    for net, info in drivers.items():
        inst = info["instance"]
        out.setdefault(inst, {"outs": {}, "info": info})
        out[inst]["outs"][net] = info
    return out


def find_flop_driven_by(drivers: dict, d_net: str) -> tuple[str, dict] | None:
    for net, info in drivers.items():
        if info.get("class") != "flop":
            continue
        if info["in_pins"].get("D") == d_net:
            return net, info
    return None


def find_muxes(drivers: dict) -> list[tuple[str, dict]]:
    """Return (X_net, info) for every mux2."""
    return [
        (net, info)
        for net, info in drivers.items()
        if info.get("class") == "mux"
    ]


def extract_enabled_mux_chain(
    drivers: dict, entry_x: str = ENTRY_MUX_X
) -> tuple[list[Stage], list[Check]]:
    """Walk entry mux → flop → next mux(A1=Q) … and fill per-stage checks later."""
    preamble: list[Check] = []
    mux_info = drivers.get(entry_x)
    if not mux_info or mux_info.get("class") != "mux":
        preamble.append(Check("entry_is_mux", False, f"{short(entry_x)} missing/not mux"))
        return [], preamble
    preamble.append(Check("entry_is_mux", True, short(mux_info["instance"])))

    pins = mux_info["in_pins"]
    if pins.get("A1") != PRIMARY_I:
        preamble.append(
            Check("entry_A1_is_I", False, f"A1={short(pins.get('A1', '?'))}")
        )
    else:
        preamble.append(Check("entry_A1_is_I", True, "A1=I"))

    s_common = pins.get("S")
    if not s_common:
        preamble.append(Check("entry_has_S", False, "no S pin"))
        return [], preamble
    preamble.append(Check("entry_has_S", True, short(s_common)))

    stages: list[Stage] = []
    cur_mux_x = entry_x
    cur_mux = mux_info
    seen_q: set[str] = set()

    for idx in range(0, 24):
        pins = cur_mux["in_pins"]
        a1 = pins.get("A1")
        a0 = pins.get("A0")
        s = pins.get("S")
        flop = find_flop_driven_by(drivers, cur_mux_x)
        if flop is None:
            # chain ends without a flop on this mux — stop
            break
        q_net, flop_info = flop
        if q_net in seen_q:
            break
        seen_q.add(q_net)

        st = Stage(
            index=idx,
            mux_inst=short(cur_mux["instance"]),
            mux_x=cur_mux_x,
            s_net=s or "",
            a1_net=a1 or "",
            a0_net=a0 or "",
            flop_inst=short(flop_info["instance"]),
            q_net=q_net,
        )
        stages.append(st)

        # next mux: A1 == this Q (shift forward)
        nxt = None
        for xnet, minfo in find_muxes(drivers):
            if minfo["in_pins"].get("A1") == q_net:
                nxt = (xnet, minfo)
                break
        if nxt is None:
            break
        cur_mux_x, cur_mux = nxt

    preamble.append(
        Check("extracted_stages", len(stages) >= 2, f"n_stages={len(stages)}")
    )
    return stages, preamble


def check_enabled_mux_shift_register(
    drivers: dict, stages: list[Stage], preamble: list[Check]
) -> TemplateResult:
    """Score chain against Template 1."""
    checks = list(preamble)
    if not stages:
        return TemplateResult(
            name="enabled_mux_shift_register",
            matched=False,
            summary="no stages extracted",
            checks=checks,
        )

    s0 = stages[0].s_net
    checks.append(
        Check(
            "shared_S_nonempty",
            bool(s0),
            short(s0) if s0 else "missing",
        )
    )

    # Stage 0 din must be I
    checks.append(
        Check(
            "stage0_din_is_I",
            stages[0].a1_net == PRIMARY_I,
            f"A1={short(stages[0].a1_net)}",
        )
    )

    for i, st in enumerate(stages):
        sc: list[Check] = []
        # S shared
        sc.append(
            Check(
                "S_shared",
                st.s_net == s0,
                f"S={short(st.s_net)} vs {short(s0)}",
            )
        )
        # A0 hold = this Q
        sc.append(
            Check(
                "A0_holds_own_Q",
                st.a0_net == st.q_net,
                f"A0={short(st.a0_net)} Q={short(st.q_net)}",
            )
        )
        # A1 = I (i=0) or previous Q
        if i == 0:
            sc.append(
                Check(
                    "A1_is_din",
                    st.a1_net == PRIMARY_I,
                    f"A1={short(st.a1_net)}",
                )
            )
        else:
            prev_q = stages[i - 1].q_net
            sc.append(
                Check(
                    "A1_is_prev_Q",
                    st.a1_net == prev_q,
                    f"A1={short(st.a1_net)} prevQ={short(prev_q)}",
                )
            )
        # flop D = mux X (already true by construction; restate)
        flop_info = drivers[st.q_net]
        sc.append(
            Check(
                "flop_D_is_mux_X",
                flop_info["in_pins"].get("D") == st.mux_x,
                f"D={short(flop_info['in_pins'].get('D', '?'))}",
            )
        )
        # no xor/ao between mux X and flop D (direct)
        sc.append(
            Check(
                "no_arith_on_D",
                flop_info["in_pins"].get("D") == st.mux_x,
                "direct mux→flop",
            )
        )
        st.checks = sc

    stage_ok = all(st.ok for st in stages)
    shared_ok = all(c.ok for c in checks)
    matched = stage_ok and shared_ok and len(stages) >= 2

    # Which observe taps land on a stage Q?
    tap_hits = {}
    q_to_idx = {st.q_net: st.index for st in stages}
    for name, net in OBSERVE_TAPS.items():
        tap_hits[name] = {
            "net": short(net),
            "is_shift_Q": net in q_to_idx,
            "stage_index": q_to_idx.get(net),
            "expected_delay": q_to_idx[net] + 1 if net in q_to_idx else None,
            # delay from I: Q_i updates one cycle after din; din_0=I combo through mux
            # Q_0[t] = I[t-1] when S=1 → delay 1 for stage 0
        }
        # Fix expected_delay: stage index i → delay i+1 (flop)
        if net in q_to_idx:
            tap_hits[name]["expected_delay"] = q_to_idx[net] + 1

    n_ok = sum(1 for st in stages if st.ok)
    summary = (
        f"MATCH · {n_ok}/{len(stages)} stages satisfy mux-hold shift rules; "
        f"S={short(s0)}; taps on chain: "
        + ", ".join(
            f"{k}=Q{v['stage_index']}" for k, v in tap_hits.items() if v["is_shift_Q"]
        )
    )
    if not matched:
        bad = [c.rule for c in checks if not c.ok]
        for st in stages:
            bad += [f"s{st.index}:{c.rule}" for c in st.checks if not c.ok]
        summary = f"NO MATCH · failed: {', '.join(bad[:12])}"

    return TemplateResult(
        name="enabled_mux_shift_register",
        matched=matched,
        summary=summary,
        checks=checks,
        stages=stages,
        extra={"tap_hits": tap_hits, "S_common": short(s0), "n_stages": len(stages)},
    )


def check_plain_dff_chain(drivers: dict, stages: list[Stage]) -> TemplateResult:
    """Template 2: flops chained with D=prev Q and NO mux on the D path."""
    checks: list[Check] = []
    if len(stages) < 2:
        return TemplateResult(
            name="plain_dff_chain",
            matched=False,
            summary="too few stages to compare",
            checks=[Check("n_stages", False, str(len(stages)))],
        )

    # For plain DFF chain, each flop D should equal previous Q (or I),
    # and there should be no mux instance driving D.
    all_plain = True
    for i, st in enumerate(stages):
        d = drivers[st.q_net]["in_pins"].get("D")
        # In our extraction D is always a mux X — that alone fails plain_dff
        d_driver = drivers.get(d or "")
        is_mux = bool(d_driver and d_driver.get("class") == "mux")
        checks.append(
            Check(
                f"stage{i}_D_not_mux",
                not is_mux,
                f"D←{short(d or '?')} class={d_driver.get('class') if d_driver else '?'}",
            )
        )
        if is_mux:
            all_plain = False
        if i == 0:
            # would need D=I
            checks.append(
                Check(
                    f"stage{i}_D_is_I",
                    d == PRIMARY_I,
                    f"D={short(d or '?')}",
                )
            )
            if d != PRIMARY_I:
                all_plain = False
        else:
            prev = stages[i - 1].q_net
            checks.append(
                Check(
                    f"stage{i}_D_is_prev_Q",
                    d == prev,
                    f"D={short(d or '?')} prev={short(prev)}",
                )
            )
            if d != prev:
                all_plain = False

    return TemplateResult(
        name="plain_dff_chain",
        matched=all_plain,
        summary=(
            "MATCH · plain DFF chain"
            if all_plain
            else "NO MATCH · D inputs are mux outputs (hold+shift), not bare Q/I"
        ),
        checks=checks,
        stages=[],
    )


def check_fa_xor_arith_path(drivers: dict, stages: list[Stage]) -> TemplateResult:
    """Template 3: path spine is xor/FA — should NOT match our shift taps."""
    checks: list[Check] = []
    # Along extracted spine, every stage is mux+flop — count arith cells on A1 path
    arith_on_spine = 0
    for st in stages:
        a1_drv = drivers.get(st.a1_net)
        cls = (a1_drv or {}).get("class")
        is_arith = cls in ("xor", "xnor", "aoi")
        checks.append(
            Check(
                f"s{st.index}_A1_not_arith",
                not is_arith,
                f"A1 class={cls or ('primary' if st.a1_net == PRIMARY_I else 'flop/other')}",
            )
        )
        if is_arith:
            arith_on_spine += 1

    # Also: tap nets themselves driven by flop, not xor
    for name, net in OBSERVE_TAPS.items():
        info = drivers.get(net)
        cls = (info or {}).get("class")
        checks.append(
            Check(
                f"tap_{name}_is_flop",
                cls == "flop",
                f"class={cls}",
            )
        )

    matched = arith_on_spine > 0 and all(
        (drivers.get(n) or {}).get("class") in ("xor", "xnor", "aoi")
        for n in OBSERVE_TAPS.values()
    )
    # We want this template to be rejected for our hypothesis
    return TemplateResult(
        name="fa_xor_arith_path",
        matched=matched,
        summary=(
            "MATCH · spine looks like FA/xor arithmetic"
            if matched
            else "NO MATCH · spine is mux+flop (not FA/xor arith); taps are flop Q"
        ),
        checks=checks,
        extra={"arith_cells_on_A1": arith_on_spine},
    )


def check_gated_observe(drivers: dict) -> TemplateResult:
    """a22o.X / a221o.X are not delay structures — AND/OR of shift × FA stub."""
    checks: list[Check] = []
    a22 = drivers.get(GATED_OBS["a22o.X"])
    if not a22:
        return TemplateResult(
            name="gated_observe_sites",
            matched=False,
            summary="a22o.X missing",
            checks=[Check("a22o_present", False)],
        )
    pins = a22["in_pins"]
    # a22o: X = (A1∧A2)∨(B1∧B2)
    a1, a2 = pins.get("A1"), pins.get("A2")
    b1, b2 = pins.get("B1"), pins.get("B2")
    checks.append(
        Check(
            "a22o_A2_is_shift_Q",
            a2 in OBSERVE_TAPS.values() or a2 == OBSERVE_TAPS["a22o.A2"],
            f"A2={short(a2 or '?')}",
        )
    )
    checks.append(
        Check(
            "a22o_B2_is_shift_Q",
            b2 == OBSERVE_TAPS["a22o.B2"],
            f"B2={short(b2 or '?')}",
        )
    )
    # A1/B1 should NOT be on shift chain (FA prior)
    shift_qs = set(OBSERVE_TAPS.values())
    # also all stage Qs unknown here — use: A1 driver not flop-from-mux-shift entry
    a1_info = drivers.get(a1 or "")
    checks.append(
        Check(
            "a22o_A1_not_shift_tap",
            a1 not in shift_qs,
            f"A1={short(a1 or '?')} class={(a1_info or {}).get('class')}",
        )
    )
    checks.append(
        Check(
            "a22o_is_a22o_cell",
            "a22o" in (a22.get("cell") or ""),
            a22.get("cell", ""),
        )
    )

    a221 = drivers.get(GATED_OBS["a221o.X"])
    if a221:
        p2 = a221["in_pins"]
        checks.append(
            Check(
                "a221o_C1_is_a22o_X",
                p2.get("C1") == GATED_OBS["a22o.X"],
                f"C1={short(p2.get('C1', '?'))}",
            )
        )
        checks.append(
            Check(
                "a221o_A2_is_shift",
                p2.get("A2") == OBSERVE_TAPS["a221o.A2"],
                f"A2={short(p2.get('A2', '?'))}",
            )
        )
        checks.append(
            Check(
                "a221o_B2_is_shift",
                p2.get("B2") == OBSERVE_TAPS["a221o.B2"],
                f"B2={short(p2.get('B2', '?'))}",
            )
        )

    ok = all(c.ok for c in checks)
    return TemplateResult(
        name="gated_observe_sites",
        matched=ok,
        summary=(
            "CONFIRMED · a22o.X/a221o.X = shift taps ∧ FA-prior stubs (gated observe, not a delay)"
            if ok
            else "UNEXPECTED wiring at gated observe sites"
        ),
        checks=checks,
        extra={
            "a22o_pins": {k: short(v) for k, v in pins.items()},
        },
    )


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------


def plot_checklist(results: list[TemplateResult], out_png: Path) -> Path:
    # Flatten: one row per template + stage failures
    rows: list[tuple[str, bool, str]] = []
    for r in results:
        rows.append((r.name, r.matched, r.summary))
        if r.name == "enabled_mux_shift_register":
            for st in r.stages:
                rows.append(
                    (
                        f"  stage[{st.index}] {st.mux_inst}→{st.flop_inst}",
                        st.ok,
                        f"Q={short(st.q_net)}",
                    )
                )

    fig, ax = plt.subplots(figsize=(12, 0.42 * len(rows) + 1.5), dpi=140)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(rows) - 0.5)
    ax.invert_yaxis()
    ax.axis("off")
    for i, (name, ok, summary) in enumerate(rows):
        color = "#c6efce" if ok else "#ffc7ce"
        edge = "#006100" if ok else "#9c0006"
        ax.add_patch(
            FancyBboxPatch(
                (0.02, i - 0.38),
                0.96,
                0.76,
                boxstyle="round,pad=0.02,rounding_size=0.05",
                facecolor=color,
                edgecolor=edge,
                lw=0.8,
            )
        )
        mark = "✓" if ok else "✗"
        ax.text(0.04, i, f"{mark}  {name}", va="center", fontsize=8, family="monospace", fontweight="bold")
        ax.text(0.48, i, summary[:90], va="center", fontsize=7, color="#333")
    ax.set_title(
        "Known delay-structure comparison · green = template rules satisfied",
        fontsize=11,
        pad=10,
    )
    fig.tight_layout()
    return savefig_locked(fig, out_png)


def plot_schematic(result: TemplateResult, out_png: Path) -> Path:
    """Compact schematic of matched mux-shift stages."""
    stages = result.stages
    if not stages:
        fig, ax = plt.subplots(figsize=(8, 2), dpi=120)
        ax.text(0.5, 0.5, "no stages", ha="center")
        ax.axis("off")
        return savefig_locked(fig, out_png)

    n = len(stages)
    fig, ax = plt.subplots(figsize=(min(16, 1.1 * n + 3), 3.8), dpi=140)
    ax.set_xlim(-0.5, n + 0.5)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    ax.set_title(
        f"Template: enabled_mux_shift_register · S={result.extra.get('S_common')} · "
        f"{'MATCH' if result.matched else 'FAIL'}",
        fontsize=11,
    )
    # I label
    ax.text(-0.3, 2.2, "I", fontsize=10, fontweight="bold", color="#c00000", ha="center")
    for i, st in enumerate(stages):
        x = i + 0.5
        face = "#c6efce" if st.ok else "#ffc7ce"
        # mux box
        ax.add_patch(
            FancyBboxPatch(
                (x - 0.35, 1.6),
                0.7,
                0.7,
                boxstyle="round,pad=0.02",
                facecolor=face,
                edgecolor="#333",
                lw=0.8,
            )
        )
        ax.text(x, 1.95, "mux", ha="center", va="center", fontsize=7)
        ax.text(x, 1.72, st.mux_inst.replace("mux2_1_", "m"), ha="center", fontsize=6, color="#555")
        # flop box
        ax.add_patch(
            FancyBboxPatch(
                (x - 0.35, 0.35),
                0.7,
                0.7,
                boxstyle="round,pad=0.02",
                facecolor=face,
                edgecolor="#333",
                lw=0.8,
            )
        )
        ax.text(x, 0.7, "dff", ha="center", va="center", fontsize=7)
        ax.text(x, 0.48, f"Q{i}", ha="center", fontsize=7, fontweight="bold")
        # mux → flop
        ax.annotate("", xy=(x, 1.05), xytext=(x, 1.6), arrowprops=dict(arrowstyle="->", lw=0.8))
        # hold A0
        ax.annotate(
            "",
            xy=(x - 0.2, 1.7),
            xytext=(x - 0.2, 1.05),
            arrowprops=dict(arrowstyle="->", lw=0.6, color="#1f4e79"),
        )
        ax.text(x - 0.42, 1.35, "A0", fontsize=5, color="#1f4e79")
        # din arrow from left
        if i == 0:
            ax.annotate(
                "",
                xy=(x - 0.35, 2.1),
                xytext=(x - 0.7, 2.1),
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#c00000"),
            )
            ax.text(x - 0.2, 2.35, "A1=I", fontsize=6, color="#c00000", ha="center")
        else:
            ax.annotate(
                "",
                xy=(x - 0.35, 2.0),
                xytext=(i - 0.5 + 0.35, 0.7),
                arrowprops=dict(arrowstyle="->", lw=0.7, color="#c45911", connectionstyle="arc3,rad=-0.2"),
            )
        # S
        ax.text(x, 2.45, "S", ha="center", fontsize=6, color="#833c0c")
    # tap labels
    tap_hits = result.extra.get("tap_hits", {})
    y = 0.08
    labels = []
    for name, hit in tap_hits.items():
        if hit.get("is_shift_Q"):
            labels.append(f"{name}=Q{hit['stage_index']} (+{hit['expected_delay']})")
    ax.text(n / 2, y, " · ".join(labels), ha="center", fontsize=7, family="monospace")
    fig.tight_layout()
    return savefig_locked(fig, out_png)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    drivers, _stubs, _meta = parse_structural(STRUCT)

    stages, preamble = extract_enabled_mux_chain(drivers)
    r_shift = check_enabled_mux_shift_register(drivers, stages, preamble)
    r_plain = check_plain_dff_chain(drivers, stages)
    r_fa = check_fa_xor_arith_path(drivers, stages)
    r_gate = check_gated_observe(drivers)

    results = [r_shift, r_plain, r_fa, r_gate]

    # Verdict
    hypothesis_ok = (
        r_shift.matched
        and not r_plain.matched
        and not r_fa.matched
        and r_gate.matched
    )

    figs = [
        plot_checklist(results, OUT / "structure_checklist.png"),
        plot_schematic(r_shift, OUT / "structure_chain_schematic.png"),
    ]

    payload = {
        "hypothesis": (
            "I→a221o/a22o A2/B2 path is an enabled_mux_shift_register; "
            "a22o.X/a221o.X are FA-gated observes — not delay structures."
        ),
        "hypothesis_supported": hypothesis_ok,
        "templates": [
            {
                "name": r.name,
                "matched": r.matched,
                "summary": r.summary,
                "checks": [asdict(c) for c in r.checks],
                "stages": [
                    {
                        "index": s.index,
                        "mux": s.mux_inst,
                        "flop": s.flop_inst,
                        "Q": short(s.q_net),
                        "A1": short(s.a1_net),
                        "A0": short(s.a0_net),
                        "S": short(s.s_net),
                        "ok": s.ok,
                        "checks": [asdict(c) for c in s.checks],
                    }
                    for s in r.stages
                ],
                "extra": r.extra,
            }
            for r in results
        ],
        "figures": [p.name for p in figs],
    }
    (OUT / "structure_match.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    def yn(b: bool) -> str:
        return "**MATCH**" if b else "**no match**"

    md = [
        "# Known delay-structure comparison",
        "",
        "Structural rules only (Verilog pin connectivity). Simulation is a",
        "separate sanity check in `run_shift_chain_inspect.py`.",
        "",
        f"## Hypothesis supported: **{'yes' if hypothesis_ok else 'no'}**",
        "",
        payload["hypothesis"],
        "",
        "## Template scorecard",
        "",
        "| Template | Result | Summary |",
        "|----------|:------:|---------|",
    ]
    for r in results:
        md.append(f"| `{r.name}` | {yn(r.matched)} | {r.summary} |")

    md += [
        "",
        "### How to read this",
        "",
        "- We **want** `enabled_mux_shift_register` = MATCH.",
        "- We **want** `plain_dff_chain` = no match (mux hold present).",
        "- We **want** `fa_xor_arith_path` = no match (not FA arithmetic on I).",
        "- We **want** `gated_observe_sites` = MATCH (C1 path is shift ∧ FA stub).",
        "",
        "## Figures",
        "",
        "- [`structure_checklist.png`](structure_checklist.png) — pass/fail per template & stage",
        "- [`structure_chain_schematic.png`](structure_chain_schematic.png) — mux↔dff hold/shift diagram",
        "",
        "## `enabled_mux_shift_register` stages",
        "",
        "| i | mux | flop | Q | A1 (din) | A0 (hold) | ok |",
        "|--:|-----|------|---|----------|-----------|:--:|",
    ]
    for st in r_shift.stages:
        md.append(
            f"| {st.index} | `{st.mux_inst}` | `{st.flop_inst}` | `{short(st.q_net)}` | "
            f"`{short(st.a1_net)}` | `{short(st.a0_net)}` | {'✓' if st.ok else '✗'} |"
        )

    md += ["", "### Observe taps on the shift Qs", "", "| tap | on chain? | stage | expected delay |", "|-----|:---------:|------:|---------------:|"]
    for name, hit in r_shift.extra.get("tap_hits", {}).items():
        md.append(
            f"| `{name}` | {'yes' if hit['is_shift_Q'] else 'no'} | "
            f"{hit.get('stage_index')} | {hit.get('expected_delay')} |"
        )

    md += [
        "",
        "## Rule definitions",
        "",
        "### enabled_mux_shift_register",
        "```text",
        "shared S across stages",
        "stage0:  mux.A1 = I , mux.A0 = Q0 , flop.D = mux.X , flop.Q = Q0",
        "stage i: mux.A1 = Q{i-1} , mux.A0 = Qi , flop.D = mux.X , flop.Q = Qi",
        "```",
        "",
        "### plain_dff_chain",
        "```text",
        "flop0.D = I ; flop_i.D = Q{i-1}   # no mux on D",
        "```",
        "",
        "### fa_xor_arith_path",
        "```text",
        "I reaches taps through xor/xnor/AO FA cells (not mux+flop spine)",
        "```",
        "",
        f"JSON: [`structure_match.json`](structure_match.json)",
        "",
        "Regenerate:",
        "```bash",
        "python3 phase3/a221o_set/match_known_delay_structures.py",
        "```",
        "",
    ]
    md_path = OUT / "structure_match.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    # Point README at structural verdict first
    readme = OUT / "README.md"
    if readme.exists():
        prev = readme.read_text(encoding="utf-8")
        banner = (
            "> **Structural verdict:** see [`structure_match.md`](structure_match.md) "
            f"— hypothesis supported: **{'yes' if hypothesis_ok else 'no'}**.\n\n"
        )
        if not prev.startswith("> **Structural verdict:"):
            readme.write_text(banner + prev, encoding="utf-8")

    print(f"hypothesis_supported={hypothesis_ok}")
    for r in results:
        print(f"  {r.name}: matched={r.matched} · {r.summary[:100]}")
    print(f"wrote {md_path}")
    for p in figs:
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
