#!/usr/bin/env python3
"""Phase 3 — t03/t04 sticky_or: watch or4b (→or4.C) and FA→nand2(I) (→or4.D).

For each and2 leaf in hasI groups 3 and 4:
  or4.X = A | B | C | D
    C ← or4b  (FA decode path)
    D ← nand2(A=I, B=inv_2_7__A) where inv_2_7__A = enable ∧ ¬or2_2_11__A
    FA-side input into that path: or2_2_11__A (and FA phase inv_2_9__A upstream)

Simulates all0, logs those nets, writes open timelines.

Usage (from rework/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 tools/phase3_or4b_nand2_I_opens.py
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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
SUMMARY = ROOT / "phase2" / "and4b" / "groups" / "summary.json"
OPENS_JSON = REPO / "sim" / "opens_exact_shift1.json"
RETRACE = REPO / "sim" / "retrace_all22_opens_structural.json"
OUT_ROOT = HERE
BUILD = ROOT / "phase3" / "build"
N_CYC = 121
GROUP_IDX = (3, 4)
# Distinct colors for path kinds (not just group)
COLOR_OR4B = "#0d7377"       # or4b → or4.C
COLOR_OPEN = "#c45911"       # leaf OPEN windows
COLOR_AND2B_Y = "#6a1b9a"    # and2b_2_11 Y = inv_2_7__A → nand2.B
COLOR_AND2B_AN = "#1b5e20"   # and2b_2_11 A_N = or2_2_11__A
GROUP_COLORS = {3: "#0d7377", 4: "#b5651d"}

OUT_TO_LEAF: dict[str, str] = {}
for _p in "ABCD":
    OUT_TO_LEAF[f"and4_2_0__{_p}"] = f"slot.0.{_p}"
    OUT_TO_LEAF[f"and4_2_1__{_p}"] = f"slot.1.{_p}"
    OUT_TO_LEAF[f"and4_2_5__{_p}"] = f"a5.{_p}"
    OUT_TO_LEAF[f"and4_2_6__{_p}"] = f"a6.{_p}"
for _p in "ABC":
    OUT_TO_LEAF[f"and3_2_5__{_p}"] = f"and3.{_p}"
    OUT_TO_LEAF[f"and3_2_12__{_p}"] = f"a12.{_p}"


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def full(n: str) -> str:
    if n in ("I", "enable") or n.startswith("sky130_"):
        return n
    return f"sky130_fd_sc_hd__{n}"


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


def load_leaf_meta() -> dict[str, dict]:
    opens = {r["name"]: r for r in json.loads(OPENS_JSON.read_text(encoding="utf-8"))["opens"]}
    retrace = {
        r["name"]: r for r in json.loads(RETRACE.read_text(encoding="utf-8"))["opens"]
    }
    out = {}
    for name, o in opens.items():
        rt = retrace.get(name) or {}
        out[name] = {
            "opens_all0": list(o.get("opens_all0") or []),
            "open_net": o.get("open_net") or rt.get("open_net"),
            "open_when": int(rt.get("open_when", 1)),
            "phase": o.get("phase") or rt.get("phase"),
            "kind": o.get("kind") or rt.get("kind"),
            "equation": rt.get("equation"),
        }
    return out


def build_members(drivers: dict, leaf_meta: dict) -> list[dict]:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    by_inst = {
        short(info["instance"]): (net, info)
        for net, info in drivers.items()
        if info.get("instance")
    }
    members: list[dict] = []
    for t in summary["types"]:
        if t["index"] not in GROUP_IDX:
            continue
        for m in t["members"]:
            inst = m["instance"]
            if inst not in by_inst:
                raise SystemExit(f"missing instance {inst}")
            net, info = by_inst[inst]
            pins = info.get("in_pins") or {}
            # and2 A/B are or4__A / or4__B pin nets — recover or4 instance prefix
            a = short(pins["A"])
            if not a.endswith("__A"):
                raise SystemExit(f"{inst}: unexpected A pin {a}")
            or4 = a[: -len("__A")]
            leaf = OUT_TO_LEAF.get(m["out_net"])
            if not leaf or leaf not in leaf_meta:
                raise SystemExit(f"no leaf meta for {inst} / {m['out_net']}")
            lm = leaf_meta[leaf]
            c_net = full(f"{or4}__C")
            d_net = full(f"{or4}__D")
            # drivers of C / D
            c_drv = drivers.get(c_net) or {}
            d_drv = drivers.get(d_net) or {}
            members.append(
                {
                    "group": t["index"],
                    "folder": t["folder"],
                    "label": t["label"],
                    "instance": inst,
                    "leaf": leaf,
                    "slug": leaf.replace(".", "_"),
                    "Y": net,
                    "or4": or4,
                    "C": c_net,
                    "D": d_net,
                    "C_cell": short(c_drv.get("instance") or "?"),
                    "D_cell": short(d_drv.get("instance") or "?"),
                    "C_pins": {
                        k: short(v) for k, v in (c_drv.get("in_pins") or {}).items()
                    },
                    "D_pins": {
                        k: short(v) for k, v in (d_drv.get("in_pins") or {}).items()
                    },
                    "open_net": lm.get("open_net"),
                    "open_when": lm["open_when"],
                    "phase": lm.get("phase"),
                    "opens_ref": lm["opens_all0"],
                    "kind": lm.get("kind"),
                }
            )
    return members


def windows(cycs: list[int]) -> list[tuple[int, int, int]]:
    if not cycs:
        return []
    out = []
    a = b = cycs[0]
    for c in cycs[1:]:
        if c == b + 1:
            b = c
        else:
            out.append((a, b, b - a + 1))
            a = b = c
    out.append((a, b, b - a + 1))
    return out


def plot_timeline(lanes: list[dict], out_png: Path, title: str) -> None:
    order = list(lanes)
    nlanes = len(order)
    fig_h = max(6.0, 0.38 * nlanes + 2.0)
    fig, ax = plt.subplots(figsize=(14, fig_h), dpi=140)
    for yi, lane in enumerate(reversed(order)):
        for a, b, L in windows(lane["opens"]):
            ax.barh(
                yi,
                L,
                left=a - 0.5,
                height=0.72,
                color=lane["color"],
                edgecolor="white",
                linewidth=0.35,
                zorder=2,
                alpha=lane.get("alpha", 0.95),
            )
    groups = [lane["group"] for lane in order]
    if len(set(groups)) > 1:
        rev = list(reversed(order))
        for i in range(len(rev) - 1):
            if rev[i]["group"] != rev[i + 1]["group"]:
                ax.axhline(i + 0.5, color="#444444", lw=1.0, zorder=1.5)
                break
    ax.set_yticks(range(nlanes))
    ax.set_yticklabels(
        [lane["label"] for lane in reversed(order)], fontsize=7.5, family="monospace"
    )
    ax.set_xlim(-0.5, N_CYC - 0.5)
    ax.set_xlabel("cycle (all0 · enable=1 after reset)")
    ax.set_title(title, fontsize=11)
    ax.grid(axis="x", color="#eeeeee", lw=0.6, zorder=0)
    handles = [
        Patch(facecolor=COLOR_OR4B, label="or4b → or4.C  (raw C=1)"),
        Patch(facecolor=COLOR_OPEN, label="leaf OPEN window"),
        Patch(facecolor=COLOR_AND2B_Y, label="and2b_2_11 Y = inv_2_7__A → nand2.B"),
        Patch(facecolor=COLOR_AND2B_AN, label="and2b_2_11 A_N = or2_2_11__A (FA in)"),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=8)
    fig.tight_layout()
    savefig_locked(fig, out_png)
    print(f"wrote {out_png}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--groups", type=int, nargs="+", default=list(GROUP_IDX))
    args = ap.parse_args()
    want = set(args.groups)

    drivers, _, meta = parse_structural()
    print("structural:", meta)
    leaf_meta = load_leaf_meta()
    members = [m for m in build_members(drivers, leaf_meta) if m["group"] in want]
    print(f"members: {len(members)}")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    # Probes
    probes: list[tuple[str, str]] = [
        ("I", "I"),
        ("enable", "enable"),
        # and2b_2_11: FA-side A_N and Y (= nand2.B = inv_2_7__A)
        ("and2b_AN", "sky130_fd_sc_hd__or2_2_11__A"),
        ("and2b_Y", "sky130_fd_sc_hd__inv_2_7__A"),
        ("or4A", "sky130_fd_sc_hd__or4_2_4__A"),
        ("or4B", "sky130_fd_sc_hd__or4_2_4__B"),
        ("or4C", "sky130_fd_sc_hd__or4_2_4__C"),
        ("or4D", "sky130_fd_sc_hd__or4_2_4__D"),
    ]
    for m in members:
        probes.append((f"C_{m['slug']}", m["C"]))
        probes.append((f"D_{m['slug']}", m["D"]))

    pats_path = BUILD / "pats_or4b_nand2_I.txt"
    pats_path.write_text("0" * N_CYC + "\n", encoding="utf-8")
    labels = [p[0] for p in probes]
    n = len(probes)
    dumps = []
    for i, (_lab, net) in enumerate(probes):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_or4b_nand2_I.csv"
    tb = BUILD / "tb_or4b_nand2_I.v"
    vvp = BUILD / "tb_or4b_nand2_I.vvp"
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
    $readmemb("{pats_path.as_posix()}", pat);
    fd = $fopen("{csv_raw.as_posix()}", "w");
    $fwrite(fd, "mode,cyc,{','.join(labels)}\\n");
    for (mode=0; mode<1; mode=mode+1) begin
      rst_n=0; enable=0; I=0;
      repeat(3) @(posedge clk);
      rst_n=1; @(posedge clk);
      enable=1;
      for (cyc=0; cyc<{N_CYC}; cyc=cyc+1) begin
        @(negedge clk);
        I = pat[mode][cyc];
        @(posedge clk);
        #1;
{chr(10).join(dumps)}
        $fwrite(fd, "%0d,%0d", mode, cyc);
        for (i=0; i<{n}; i=i+1) $fwrite(fd, ",%0d", bits[i]);
        $fwrite(fd, "\\n");
      end
    end
    $fclose(fd);
    $finish;
  end
endmodule
""",
        encoding="utf-8",
    )

    print("compile…", flush=True)
    r = subprocess.run(
        iverilog_cmd(vvp, [STRUCT, tb]), capture_output=True, text=True, timeout=600
    )
    if r.returncode:
        raise SystemExit((r.stderr or r.stdout)[-5000:])
    _, vvp_bin = find_iverilog()
    print("simulate…", flush=True)
    r2 = subprocess.run(
        [str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=600
    )
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    rows = list(csv.DictReader(csv_raw.open(encoding="utf-8")))

    def is_leaf_open(row: dict, m: dict) -> bool:
        """Same open definition as opens_exact / retrace."""
        if m["open_net"]:
            key = f"C_{m['slug']}"
            # open_net is or4__C for deep; value vs open_when
            if short(m["open_net"]) == short(m["C"]):
                return int(row[key]) == int(m["open_when"])
            # unexpected — fall through
        phase = m.get("phase")
        if phase and len(phase) == 4:
            abcd = "".join(row[f"or4{b}"] for b in "ABCD")
            return abcd == phase
        return False

    all_lanes: list[dict] = []
    all_ok = True

    for gi in sorted(want):
        mems = [m for m in members if m["group"] == gi]
        if not mems:
            continue
        folder = mems[0]["folder"]
        gdir = OUT_ROOT / folder
        gdir.mkdir(parents=True, exist_ok=True)

        # README
        readme = [
            f"# t{gi:02d} or4b + FA→nand2(I) path",
            "",
            f"Group: `{mems[0]['label']}`",
            "",
            "Each sticky_or and2 sits on `or4.A × or4.B`. The shared `or4` also takes:",
            "",
            "- **C** ← **or4b** (plotted as raw `or4.__C`)",
            "- **D** ← **nand2(I, inv_2_7__A)**; `inv_2_7__A` = **and2b_2_11.Y**",
            "- **and2b_2_11**: `A_N=or2_2_11__A` (FA in), `B=enable`, `Y=inv_2_7__A`",
            "",
            "Stimulus: **all0**. OPEN = leaf FA-open definition from `opens_exact_shift1`.",
            "",
            "| Leaf | and2 | or4 | or4b→C | nand2→D | open def |",
            "|------|------|-----|--------|---------|----------|",
        ]
        for m in mems:
            if m["open_net"]:
                odef = f"`{short(m['open_net'])}`=={m['open_when']}"
            else:
                odef = f"`or4_2_4`==`{m['phase']}`"
            readme.append(
                f"| `{m['leaf']}` | `{m['instance']}` | `{m['or4']}` | "
                f"`{m['C_cell']}`→`{short(m['C'])}` | `{m['D_cell']}` | {odef} |"
            )
        readme += [
            "",
            "## Artifacts",
            "",
            "- [`open_log.md`](open_log.md) / [`open_log.csv`](open_log.csv)",
            "- [`FA_open_timeline.png`](FA_open_timeline.png) — or4b C vs OPEN vs and2b",
            "",
        ]
        (gdir / "README.md").write_text("\n".join(readme), encoding="utf-8")

        # Per-cycle log
        fieldnames = ["cyc", "I", "enable", "and2b_AN", "and2b_Y", "or4_2_4"]
        for m in mems:
            fieldnames += [
                f"C_{m['slug']}",
                f"D_{m['slug']}",
                f"open_{m['slug']}",
            ]

        log_rows = []
        opens_found: dict[str, list[int]] = {m["leaf"]: [] for m in mems}
        c_hi: dict[str, list[int]] = {m["leaf"]: [] for m in mems}
        and2b_an_hi: list[int] = []
        and2b_y_hi: list[int] = []
        for row in rows:
            cyc = int(row["cyc"])
            or44 = "".join(row[f"or4{b}"] for b in "ABCD")
            an = int(row["and2b_AN"])
            yy = int(row["and2b_Y"])
            if an:
                and2b_an_hi.append(cyc)
            if yy:
                and2b_y_hi.append(cyc)
            rec = {
                "cyc": cyc,
                "I": row["I"],
                "enable": row["enable"],
                "and2b_AN": an,
                "and2b_Y": yy,
                "or4_2_4": or44,
            }
            for m in mems:
                c_val = int(row[f"C_{m['slug']}"])
                rec[f"C_{m['slug']}"] = c_val
                rec[f"D_{m['slug']}"] = int(row[f"D_{m['slug']}"])
                if c_val:
                    c_hi[m["leaf"]].append(cyc)
                op = 1 if is_leaf_open(row, m) else 0
                rec[f"open_{m['slug']}"] = op
                if op:
                    opens_found[m["leaf"]].append(cyc)
            log_rows.append(rec)

        with (gdir / "open_log.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(log_rows)

        y_line = (
            f"- **Y** `inv_2_7__A` high: n={len(and2b_y_hi)}"
            + (" (all cycles)" if len(and2b_y_hi) == N_CYC else f" `{and2b_y_hi}`")
        )
        md = [
            f"# Open log — t{gi:02d} or4b / and2b→nand2(I)",
            "",
            "all0 · sample after posedge with enable=1.",
            "",
            "### Shared and2b_2_11 (→ every nand2.B as `inv_2_7__A`)",
            "",
            f"- **A_N** `or2_2_11__A` high: `{and2b_an_hi}`  (n={len(and2b_an_hi)})",
            y_line,
            "",
            "### Per-leaf or4b → C and OPEN",
            "",
            "| Leaf | or4b cell | or4.C net | C=1 (n) | OPEN | Ref | Match |",
            "|------|-----------|-----------|--------:|------|-----|:-----:|",
        ]
        for m in mems:
            sim = opens_found[m["leaf"]]
            ref = m["opens_ref"]
            ok = sim == ref
            if not ok:
                sim_s = [c for c in sim if 0 < c < N_CYC - 1]
                ref_s = [c for c in ref if 0 < c < N_CYC - 1]
                ok = sim_s == ref_s
                tag = "✓ (edges may differ)" if ok and sim != ref else ("✓" if ok else "✗")
            else:
                tag = "✓"
            if not ok:
                all_ok = False
            md.append(
                f"| `{m['leaf']}` | `{m['C_cell']}` | `{short(m['C'])}` | "
                f"{len(c_hi[m['leaf']])} | `{sim}` | `{ref}` | {tag} |"
            )
        md += [
            "",
            "Figure: [`FA_open_timeline.png`](FA_open_timeline.png)",
            "",
            "Lane key: **or4b→C** (raw C=1) · **OPEN** · "
            "**and2b Y=inv_2_7__A** · **and2b A_N=or2_2_11__A**",
            "",
        ]
        (gdir / "open_log.md").write_text("\n".join(md), encoding="utf-8")
        print(f"wrote {gdir / 'open_log.md'}")

        # Lanes: per leaf or4b C + OPEN, then shared and2b Y / A_N
        group_lanes: list[dict] = []
        for m in mems:
            c_lane = {
                "label": f"or4b→{short(m['C'])}  [{m['C_cell']}]",
                "group": gi,
                "opens": c_hi[m["leaf"]],
                "color": COLOR_OR4B,
                "alpha": 0.85,
            }
            o_lane = {
                "label": f"OPEN {m['leaf']}",
                "group": gi,
                "opens": opens_found[m["leaf"]],
                "color": COLOR_OPEN,
                "alpha": 0.95,
            }
            group_lanes += [c_lane, o_lane]
            all_lanes += [c_lane, o_lane]

        y_lane = {
            "label": "and2b_2_11 Y = inv_2_7__A → nand2.B",
            "group": gi,
            "opens": and2b_y_hi,
            "color": COLOR_AND2B_Y,
            "alpha": 0.55,
        }
        an_lane = {
            "label": "and2b_2_11 A_N = or2_2_11__A (FA in)",
            "group": gi,
            "opens": and2b_an_hi,
            "color": COLOR_AND2B_AN,
            "alpha": 0.9,
        }
        group_lanes += [y_lane, an_lane]
        all_lanes += [y_lane, an_lane]

        g_png = gdir / "FA_open_timeline.png"
        plot_timeline(
            group_lanes,
            g_png,
            f"t{gi:02d}  or4b→C  vs  OPEN  vs  and2b_2_11 (inv_2_7__A)  · all0",
        )
        src = g_png if g_png.exists() else g_png.with_name("FA_open_timeline_updated.png")
        dest = OUT_ROOT / f"t{gi:02d}_or4b_nand2_I_timeline.png"
        try:
            dest.write_bytes(src.read_bytes())
            print(f"copied {dest}")
        except OSError:
            alt = dest.with_name(dest.stem + "_updated.png")
            alt.write_bytes(src.read_bytes())
            print(f"locked {dest.name} → wrote {alt.name}")

    if len(want) > 1 and all_lanes:
        tags = "_".join(f"t{g:02d}" for g in sorted(want))
        png = OUT_ROOT / f"{tags}_or4b_nand2_I_timeline.png"
        plot_timeline(
            all_lanes,
            png,
            "t03+t04  or4b→C  vs  OPEN  vs  and2b_2_11 (inv_2_7__A)  · all0",
        )

    idx = [
        "# or4b + and2b→nand2(I) path (t03 / t04)",
        "",
        "## Run scripts (this folder)",
        "",
        "```bash",
        "python3 phase3/sticky_or_and2/run_opens.py",
        "python3 phase3/sticky_or_and2/run_fa_input.py",
        "python3 phase3/sticky_or_and2/run_flop_init.py",
        "```",
        "",
        "Also: [`flop_init_all0/`](flop_init_all0/) — all flop Q @ all0 (used for this FA/nand path).",
        "",
        "Timelines separate:",
        "- **or4b → or4.C** (raw C=1)",
        "- **leaf OPEN** windows",
        "- **and2b_2_11 Y** = `inv_2_7__A` → nand2.B",
        "- **and2b_2_11 A_N** = `or2_2_11__A` (FA input, I-independent, 0 on all0/all1)",
        "",
        "| # | Folder | Timeline |",
        "|--:|--------|----------|",
    ]
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    for t in summary["types"]:
        if t["index"] not in want:
            continue
        idx.append(
            f"| {t['index']} | [`{t['folder']}/`]({t['folder']}/) | "
            f"[`FA_open_timeline.png`]({t['folder']}/FA_open_timeline.png) |"
        )
    idx.append("")
    (OUT_ROOT / "README.md").write_text("\n".join(idx), encoding="utf-8")
    print(f"match_ref={all_ok}")


if __name__ == "__main__":
    main()
