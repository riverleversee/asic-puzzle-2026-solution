#!/usr/bin/env python3
"""Phase 3 — all0: monitor every flip-flop Q to show initial / early state.

Usage (from rework/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 tools/phase3_flop_init_all0.py
"""
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
_p = HERE
while not ((_p / "lib").is_dir() and (_p / "netlist").is_dir()):
    if _p.parent == _p:
        raise SystemExit(f"rework_coded root not found above {HERE}")
    _p = _p.parent
ROOT = _p  # rework_coded/
import sys
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))
REPO = ROOT.parent

from run_sim import find_iverilog  # noqa: E402
from structural_drivers import parse_structural  # noqa: E402
from rework_paths import savefig_locked  # noqa: E402

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
PDK = REPO / "netlist" / "structural" / "pdk"
INC = PDK / "include"
OUT = HERE
BUILD = ROOT / "phase3" / "build"
N_CYC = 121
# Show first N cycles in the compact timeline figure
FIG_CYCLES = 32

# Path-relevant flops to highlight (or4b / and2b→nand2 / FA)
HIGHLIGHT = {
    "or2_2_11__A",  # and2b_2_11 A_N (FA in)
    "or2_2_11__B",
    "inv_2_7__A",  # and2b_2_11 Y — driven by and2b not a flop, skip if not flop
    "or4_2_4__A",
    "or4_2_4__B",
    "or4_2_4__C",
    "or4_2_4__D",
}


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def family(cell: str) -> str:
    return re.sub(r"_\d+$", "", cell.replace("sky130_fd_sc_hd__", ""))


def cells_used() -> set[str]:
    text = STRUCT.read_text(encoding="utf-8", errors="replace")
    return {
        c
        for c in re.findall(r"sky130_fd_sc_hd__\w+", text)
        if re.match(r"sky130_fd_sc_hd__\w+_\d+$", c)
    }


def iverilog_cmd(vvp: Path, sources: list[Path]) -> list[str]:
    iv, _ = find_iverilog()
    cmd = [
        str(iv),
        "-g2012",
        "-DFUNCTIONAL",
        "-DUNIT_DELAY=#1",
        "-I",
        str(INC),
        "-o",
        str(vvp),
    ]
    for c in sorted(cells_used()):
        p = PDK / "cells" / family(c) / f"{c}.v"
        if p.exists():
            cmd.append(str(p))
    cmd += [str(s) for s in sources]
    return cmd


def list_flops(drivers: dict) -> list[dict]:
    out = []
    for net, info in drivers.items():
        cell = info.get("cell") or ""
        if not any(x in cell for x in ("dfrtp", "dfxtp", "dfstp", "dfbbp")):
            continue
        inst = short(info.get("instance") or "?")
        q = short(net)
        pins = {k: short(v) for k, v in (info.get("in_pins") or {}).items()}
        out.append(
            {
                "instance": inst,
                "cell": short(cell),
                "Q": net,
                "Q_short": q,
                "D": pins.get("D", "?"),
                "label": f"{inst}/{q}",
                "slug": re.sub(r"[^A-Za-z0-9_]", "_", inst),
            }
        )
    out.sort(key=lambda m: m["instance"])
    return out


def main() -> None:
    drivers, _, meta = parse_structural()
    print("structural:", meta)
    flops = list_flops(drivers)
    print(f"flops: {len(flops)}")

    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    probes: list[tuple[str, str]] = [("I", "I"), ("enable", "enable"), ("rst_n", "rst_n")]
    for m in flops:
        probes.append((f"Q_{m['slug']}", m["Q"]))

    pats = BUILD / "pats_flop_init_all0.txt"
    pats.write_text("0" * N_CYC + "\n", encoding="utf-8")
    labels = [p[0] for p in probes]
    n = len(probes)
    dumps = []
    for i, (_lab, net) in enumerate(probes):
        if net in ("I", "enable", "rst_n"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_flop_init_all0.csv"
    tb = BUILD / "tb_flop_init_all0.v"
    vvp = BUILD / "tb_flop_init_all0.vvp"
    tb.write_text(
        f"""`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O;
  wire success;
  reg [{N_CYC-1}:0] pat [0:0];
  reg [{n-1}:0] bits;
  integer mode, cyc, fd, i;

  puzzle uut(
    .clk(clk), .rst_n(rst_n), .enable(enable), .I(I),
    .O_0(O[0]), .O_1(O[1]), .O_2(O[2]), .O_3(O[3]),
    .O_4(O[4]), .O_5(O[5]), .O_6(O[6]), .O_7(O[7]),
    .success(success)
  );
  always #5 clk = ~clk;

  initial begin
    $readmemb("{pats.as_posix()}", pat);
    fd = $fopen("{csv_raw.as_posix()}", "w");
    $fwrite(fd, "cyc,{','.join(labels)}\\n");
    rst_n=0; enable=0; I=0;
    repeat(3) @(posedge clk);
    rst_n=1; @(posedge clk);
    enable=1;
    for (cyc=0; cyc<{N_CYC}; cyc=cyc+1) begin
      @(negedge clk);
      I = pat[0][cyc];
      @(posedge clk);
      #1;
{chr(10).join(dumps)}
      $fwrite(fd, "%0d", cyc);
      for (i=0; i<{n}; i=i+1) $fwrite(fd, ",%0d", bits[i]);
      $fwrite(fd, "\\n");
    end
    $fclose(fd);
    $finish;
  end
endmodule
""",
        encoding="utf-8",
    )

    print(f"compile… ({len(flops)} flop probes)", flush=True)
    r = subprocess.run(
        iverilog_cmd(vvp, [STRUCT, tb]), capture_output=True, text=True, timeout=900
    )
    if r.returncode:
        raise SystemExit((r.stderr or r.stdout)[-6000:])
    _, vvp_bin = find_iverilog()
    print("simulate all0…", flush=True)
    r2 = subprocess.run(
        [str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=900
    )
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    rows = list(csv.DictReader(csv_raw.open(encoding="utf-8")))
    # Copy full probe CSV into out folder (slim: cyc + Q_*)
    out_csv = OUT / "flop_Q_all0.csv"
    q_fields = ["cyc"] + [f"Q_{m['slug']}" for m in flops]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=q_fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in q_fields})

    # Per-flop summary
    summary_rows = []
    for m in flops:
        key = f"Q_{m['slug']}"
        series = [int(r[key]) for r in rows]
        q0 = series[0]
        first_one = next((c for c, v in enumerate(series) if v == 1), None)
        first_zero = next((c for c, v in enumerate(series) if v == 0), None)
        first_chg = next(
            (c for c in range(1, len(series)) if series[c] != series[0]), None
        )
        n_hi = sum(series)
        summary_rows.append(
            {
                **m,
                "Q_cyc0": q0,
                "first_change": first_chg,
                "first_1": first_one,
                "first_0": first_zero,
                "n_high": n_hi,
                "series": series,
            }
        )

    n_init1 = sum(1 for s in summary_rows if s["Q_cyc0"] == 1)
    n_init0 = sum(1 for s in summary_rows if s["Q_cyc0"] == 0)

    md = [
        "# Flip-flop initial state — all0",
        "",
        "```bash",
        "python3 phase3/and4b/groups/flop_init_all0/run_flop_init.py",
        "```",
        "",
        "Icarus structural sim: reset low → release → `enable=1`, **I=0** every cycle.",
        "Sample: after each posedge `#1` (same harness as other phase3 watches).",
        "",
        f"- Flops probed: **{len(flops)}**",
        f"- Q at cycle 0: **{n_init0}** low, **{n_init1}** high",
        f"- Full trace: [`flop_Q_all0.csv`](flop_Q_all0.csv)",
        f"- Figure (first {FIG_CYCLES} cycles): [`flop_init_timeline.png`](flop_init_timeline.png)",
        "",
        "## Cycle-0 (initial after enable)",
        "",
        "| Instance | Q net | D | Q@0 | first Δ | #high/121 |",
        "|----------|-------|---|----:|--------:|----------:|",
    ]
    for s in summary_rows:
        md.append(
            f"| `{s['instance']}` | `{s['Q_short']}` | `{s['D']}` | "
            f"{s['Q_cyc0']} | {s['first_change']} | {s['n_high']} |"
        )

    # Highlight path-related
    md += [
        "",
        "## Path-relevant (or4b / and2b→nand2 / FA phase)",
        "",
        "| Instance | Q net | Q@0 | first Δ | note |",
        "|----------|-------|----:|--------:|------|",
    ]
    for s in summary_rows:
        note = []
        if s["Q_short"] in HIGHLIGHT or s["Q_short"].startswith("or4_2_4__"):
            note.append("FA/or4_2_4 or nand-path")
        if s["Q_short"] == "or2_2_11__A":
            note.append("and2b_2_11 A_N (FA in)")
        if not note:
            # also catch or4_*__A/B that are sticky sides
            if re.match(r"or4_2_[0-9]+__[AB]$", s["Q_short"]):
                note.append("or4 A/B (sticky and2 pin)")
            elif re.match(r"or4_2_[0-9]+__C$", s["Q_short"]):
                note.append("or4.C driven by or4b (not a flop Q usually)")
            else:
                continue
        md.append(
            f"| `{s['instance']}` | `{s['Q_short']}` | {s['Q_cyc0']} | "
            f"{s['first_change']} | {'; '.join(note)} |"
        )

    md += [
        "",
        "## Still 0 forever (all0)",
        "",
    ]
    stuck0 = [s for s in summary_rows if s["n_high"] == 0]
    md.append(f"{len(stuck0)} flops never go high: "
              + ", ".join(f"`{s['instance']}`" for s in stuck0[:40])
              + ("…" if len(stuck0) > 40 else ""))
    md.append("")
    (OUT / "README.md").write_text("\n".join(md), encoding="utf-8")

    # Compact timeline: flops that are high at 0 OR change within FIG_CYCLES,
    # plus all highlight nets that are flops
    show = []
    for s in summary_rows:
        if s["Q_short"] in HIGHLIGHT:
            show.append(s)
            continue
        if s["Q_cyc0"] == 1:
            show.append(s)
            continue
        if s["first_change"] is not None and s["first_change"] < FIG_CYCLES:
            show.append(s)
    # de-dupe preserve order
    seen = set()
    show2 = []
    for s in show:
        if s["instance"] in seen:
            continue
        seen.add(s["instance"])
        show2.append(s)
    show = show2
    if not show:
        show = summary_rows[:40]

    fig_h = max(6.0, 0.22 * len(show) + 1.8)
    fig, ax = plt.subplots(figsize=(14, fig_h), dpi=140)
    for yi, s in enumerate(reversed(show)):
        series = s["series"][:FIG_CYCLES]
        for c, v in enumerate(series):
            if v:
                ax.barh(
                    yi,
                    1.0,
                    left=c - 0.5,
                    height=0.75,
                    color="#1f4e79" if s["Q_cyc0"] == 0 else "#c45911",
                    edgecolor="none",
                )
        # mark cyc0
        ax.plot([-0.5], [yi], marker="|", color="#111", ms=10, mew=1.5, zorder=5)
    ax.set_yticks(range(len(show)))
    ax.set_yticklabels(
        [
            f"{s['instance']}  Q={s['Q_short']}  init={s['Q_cyc0']}"
            for s in reversed(show)
        ],
        fontsize=6.5,
        family="monospace",
    )
    ax.set_xlim(-0.5, FIG_CYCLES - 0.5)
    ax.set_xlabel(f"cycle (all0 · first {FIG_CYCLES})")
    ax.set_title("Flip-flop Q · all0 — orange=init1, blue=init0 then rose")
    ax.axvline(-0.5, color="#888", lw=0.8, ls=":")
    ax.grid(axis="x", color="#eee", lw=0.5)
    fig.tight_layout()
    png = OUT / "flop_init_timeline.png"
    png = savefig_locked(fig, png)
    print(f"wrote {png}")

    print(f"wrote {OUT / 'README.md'}")
    print(f"init0={n_init0} init1={n_init1} stuck0={len(stuck0)}")


if __name__ == "__main__":
    main()
