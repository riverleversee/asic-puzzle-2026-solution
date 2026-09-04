#!/usr/bin/env python3
"""Phase 3 — and4 I-dependent groups: folders + FA-open watch.

Creates one subfolder per hasI and2/and2b type under phase3/and2b_set_once/.

For selected groups (default t01, t02, t05), runs an Icarus watch of each
leaf's FA-phase open entry, logs open cycles, and writes timeline PNGs.

Usage (from rework/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 tools/phase3_and4_I_group_opens.py
  python3 tools/phase3_and4_I_group_opens.py --groups 5
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
DEFAULT_SIM_GROUPS = {1, 2, 5}
GROUP_COLORS = {
    1: "#1f4e79",
    2: "#c45911",
    5: "#6a1b9a",
}
GROUP_LEGEND = {
    1: "t01 shallow and2b (and4b_D)",
    2: "t02 deep and2b (main)",
    5: "t05 and2b_2_3 (slot.1.A)",
}

# and4 / and3 pin net → sticky leaf name
OUT_TO_LEAF: dict[str, str] = {}
for _pin in "ABCD":
    OUT_TO_LEAF[f"and4_2_0__{_pin}"] = f"slot.0.{_pin}"
    OUT_TO_LEAF[f"and4_2_1__{_pin}"] = f"slot.1.{_pin}"
    OUT_TO_LEAF[f"and4_2_5__{_pin}"] = f"a5.{_pin}"
    OUT_TO_LEAF[f"and4_2_6__{_pin}"] = f"a6.{_pin}"
for _pin in "ABC":
    OUT_TO_LEAF[f"and3_2_5__{_pin}"] = f"and3.{_pin}"
    OUT_TO_LEAF[f"and3_2_12__{_pin}"] = f"a12.{_pin}"


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


def load_leaf_meta() -> dict[str, dict]:
    opens = {r["name"]: r for r in json.loads(OPENS_JSON.read_text(encoding="utf-8"))["opens"]}
    retrace = {
        r["name"]: r for r in json.loads(RETRACE.read_text(encoding="utf-8"))["opens"]
    }
    out: dict[str, dict] = {}
    for name, o in opens.items():
        rt = retrace.get(name) or {}
        open_net = o.get("open_net") or rt.get("open_net")
        out[name] = {
            "name": name,
            "kind": o.get("kind") or rt.get("kind"),
            "bank": o.get("bank") or rt.get("bank"),
            "phase": o.get("phase") or rt.get("phase"),
            "open_net": open_net,
            "open_when": rt.get("open_when", 1),
            "opens_all0": [c for c in (o.get("opens_all0") or []) if 0 <= c < N_CYC],
            "equation": rt.get("equation"),
        }
    return out


def resolve_open_probe(meta: dict) -> tuple[str | None, int, str]:
    """Return (net, active_level, how) for watching FA open entry."""
    net = meta.get("open_net")
    if net:
        return net, int(meta.get("open_when", 1)), "open_net"
    # sticky_or with null open_net: open iff or4_2_4 == phase
    phase = meta.get("phase")
    if phase and len(phase) == 4 and set(phase) <= {"0", "1"}:
        return None, 1, f"or4=={phase}"
    return None, 1, "unknown"


def hasI_types(summary: dict) -> list[dict]:
    return [t for t in summary["types"] if t.get("i_tag") == "hasI" or t.get("reaches_I")]


def member_rows(t: dict, leaf_meta: dict) -> list[dict]:
    rows = []
    for m in t["members"]:
        out = m["out_net"]
        leaf = OUT_TO_LEAF.get(out)
        lm = leaf_meta.get(leaf or "", {})
        net, level, how = resolve_open_probe(lm) if lm else (None, 1, "unmapped")
        rows.append(
            {
                "instance": m["instance"],
                "family": m["family"],
                "out_net": out,
                "leaf": leaf,
                "kind": lm.get("kind"),
                "bank": lm.get("bank"),
                "phase": lm.get("phase"),
                "fa_open_net": short(net) if net else None,
                "fa_open_net_full": net,
                "open_active": level,
                "open_how": how,
                "opens_ref": lm.get("opens_all0") or [],
            }
        )
    return rows


def write_group_readme(tdir: Path, t: dict, rows: list[dict], simmed: bool) -> None:
    tag = t.get("i_tag") or ("hasI" if t.get("reaches_I") else "noI")
    lines = [
        f"# Type {t['index']} ({t.get('size', len(t['members']))}× · {tag}): {t['label']}",
        "",
        f"- Kind: `{t['kind']}`",
        f"- Source figures: "
        f"[`../../../phase2/figures/and4b_main_groups/{t['folder']}/`]"
        f"(../../../phase2/figures/and4b_main_groups/{t['folder']}/)",
        f"- Representative: `{t['representative']}`",
        "",
        "Each member is an and2/and2b sticky leaf behind and4 / and3. "
        "**FA open entry** = phase-decode net that opens the I-compare/arm window.",
        "",
        "| Instance | Out pin | Leaf | Kind | Phase | FA open entry |",
        "|----------|---------|------|------|-------|---------------|",
    ]
    for r in rows:
        entry = (
            f"`{r['fa_open_net']}`=={r['open_active']}"
            if r["fa_open_net"]
            else f"`{r['open_how']}`"
        )
        lines.append(
            f"| `{r['instance']}` | `{r['out_net']}` | `{r['leaf']}` | "
            f"`{r['kind']}` | `{r['phase']}` | {entry} |"
        )
    lines.append("")
    if simmed:
        lines += [
            "## Sim artifacts",
            "",
            "- [`open_log.csv`](open_log.csv) — per-cycle FA-open bits (all0)",
            "- [`open_log.md`](open_log.md) — cycles where each leaf's FA entry is open",
            "",
        ]
    else:
        lines += [
            "_FA-open sim not run for this group yet._",
            "",
        ]
    (tdir / "README.md").write_text("\n".join(lines), encoding="utf-8")


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


def plot_timeline(
    lanes: list[dict],
    out_png: Path,
    title: str,
) -> None:
    """lanes: {label, group, opens, color}."""
    order = list(lanes)
    nlanes = len(order)
    fig_h = max(6.0, 0.42 * nlanes + 2.0)
    fig, ax = plt.subplots(figsize=(14, fig_h), dpi=140)

    for yi, lane in enumerate(reversed(order)):
        c = lane["color"]
        for a, b, L in windows(lane["opens"]):
            ax.barh(
                yi,
                b - a + 1,
                left=a - 0.5,
                height=0.72,
                color=c,
                edgecolor="white",
                linewidth=0.4,
                zorder=2,
            )
            if L == 1:
                ax.plot([a], [yi], "o", color="white", ms=2.5, zorder=3)

    # group separator between t01 and t02 if both present
    groups = [lane["group"] for lane in order]
    if len(set(groups)) > 1:
        # find boundary in reversed drawing order
        rev = list(reversed(order))
        for i in range(len(rev) - 1):
            if rev[i]["group"] != rev[i + 1]["group"]:
                ax.axhline(i + 0.5, color="#444444", lw=1.0, zorder=1.5)
                break

    ax.set_yticks(range(nlanes))
    ax.set_yticklabels(
        [f"{lane['label']}" for lane in reversed(order)],
        fontsize=8,
        family="monospace",
    )
    ax.set_xlim(-0.5, N_CYC - 0.5)
    ax.set_xlabel("cycle (all0 · enable=1 after reset)")
    ax.set_title(title, fontsize=11)
    ax.grid(axis="x", color="#eeeeee", lw=0.6, zorder=0)
    present = sorted({lane["group"] for lane in order if "group" in lane})
    if not present:
        # per-group plots may omit group id — infer from title color via first lane
        present = []
    handles = [
        Patch(facecolor=GROUP_COLORS[g], label=GROUP_LEGEND.get(g, f"t{g:02d}"))
        for g in present
        if g in GROUP_COLORS
    ]
    if handles:
        ax.legend(handles=handles, loc="upper right", fontsize=8)
    fig.tight_layout()
    savefig_locked(fig, out_png)
    print(f"wrote {out_png}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--groups",
        type=int,
        nargs="+",
        default=sorted(DEFAULT_SIM_GROUPS),
        help="hasI type indices to simulate (default: 1 2 5)",
    )
    args = ap.parse_args()
    sim_group_indices = set(args.groups)

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    leaf_meta = load_leaf_meta()
    types = hasI_types(summary)
    if not types:
        raise SystemExit("no hasI types in and4b_main_groups/summary.json")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    # This section owns set_once and2b only (t01/t02/t05); t03/t04 live under sticky_or_and2/.
    types = [t for t in types if t["index"] in DEFAULT_SIM_GROUPS]
    if not types:
        raise SystemExit("no set_once hasI types (expected t01/t02/t05)")

    group_info: list[dict] = []
    for t in types:
        rows = member_rows(t, leaf_meta)
        folder = t["folder"]
        tdir = OUT_ROOT / folder
        tdir.mkdir(parents=True, exist_ok=True)
        # Selected for this run, or already has artifacts from a prior run.
        already = (tdir / "open_log.md").exists()
        selected = t["index"] in sim_group_indices
        simmed = selected or already
        # Only rewrite README when simulating now or when no prior open_log yet.
        if selected or not already:
            write_group_readme(tdir, t, rows, simmed=simmed)
        group_info.append(
            {
                "type": t,
                "rows": rows,
                "dir": tdir,
                "simmed": simmed,
                "run_now": selected,
            }
        )
        print(f"folder {folder}  members={len(rows)}  sim={simmed}  run={selected}")

    # Index README
    idx = [
        "# and2b set_once (t01 / t02 / t05)",
        "",
        "FA-open + k-ones studies for `set_once` and2b leaves.",
        "",
        "## Run scripts (this folder)",
        "",
        "```bash",
        "python3 phase3/and2b_set_once/run_FA_opens.py",
        "python3 phase3/and2b_set_once/run_k_ones.py",
        "```",
        "",
        "One subfolder per **set_once** and2b type (t01/t02/t05) from "
        "[`phase2/figures/and4b_main_groups/`](../../phase2/figures/and4b_main_groups/). "
        "t03/t04 live under [`../sticky_or_and2/`](../sticky_or_and2/). "
        "Deep-dive: [`a5A/`](a5A/).",
        "",
        "FA open entry = phase-decode net that opens the window where `I` is "
        "compared / used to arm the sticky leaf.",
        "",
        "| # | Size | Folder | Sim (FA open watch) |",
        "|--:|-----:|--------|---------------------|",
    ]
    for g in group_info:
        t = g["type"]
        mark = "yes — open_log + timeline" if g["simmed"] else "pending"
        idx.append(
            f"| {t['index']} | {t.get('size', len(t['members']))} | "
            f"[`{t['folder']}/`]({t['folder']}/) | {mark} |"
        )
    idx += [
        "",
        "Per-group FA open timelines (when simulated): `tNN_…/FA_open_timeline.png`",
        "",
        "- Rule text: [`rules/`](rules/)",
        "- Deep-dive a5.A / `and2b_2_25`: [`a5A/`](a5A/)",
        "",
        "```bash",
        "python3 phase3/and2b_set_once/run_FA_opens.py",
        "python3 phase3/and2b_set_once/run_FA_opens.py --groups 5",
        "# (also: python3 tools/phase3_and4_I_group_opens.py)",
        "```",
        "",
    ]
    (OUT_ROOT / "README.md").write_text("\n".join(idx), encoding="utf-8")

    # ---- Sim selected groups (this run only) ----
    sim_groups = [g for g in group_info if g["run_now"]]
    if not sim_groups:
        print("no groups selected for sim")
        return
    probes: list[tuple[str, str]] = [
        ("I", "I"),
        ("enable", "enable"),
        ("or4A", "sky130_fd_sc_hd__or4_2_4__A"),
        ("or4B", "sky130_fd_sc_hd__or4_2_4__B"),
        ("or4C", "sky130_fd_sc_hd__or4_2_4__C"),
        ("or4D", "sky130_fd_sc_hd__or4_2_4__D"),
    ]
    # unique open nets — one probe per leaf (duplicate nets OK)
    for g in sim_groups:
        for r in g["rows"]:
            if not r["leaf"]:
                raise SystemExit(f"unmapped out_net {r['out_net']}")
            lab = f"op_{r['leaf'].replace('.', '_')}"
            if r["fa_open_net_full"]:
                probes.append((lab, r["fa_open_net_full"]))
                r["probe_label"] = lab
            else:
                r["probe_label"] = None  # derive from or4

    # all0 only — FA open decode is I-independent
    pats = [("all0", "0" * N_CYC)]
    pats_path = BUILD / "pats_and4_I_opens.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")

    labels = [p[0] for p in probes]
    n = len(probes)
    dumps = []
    for i, (_lab, net) in enumerate(probes):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_and4_I_opens.csv"
    tb = BUILD / "tb_and4_I_opens.v"
    vvp = BUILD / "tb_and4_I_opens.vvp"

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

    rows_csv = list(csv.DictReader(csv_raw.open(encoding="utf-8")))

    def is_open(row: dict, member: dict) -> bool:
        if member["probe_label"]:
            return int(row[member["probe_label"]]) == int(member["open_active"])
        # or4 phase match
        phase = member["phase"] or ""
        abcd = "".join(row[f"or4{b}"] for b in "ABCD")
        return abcd == phase

    colors = GROUP_COLORS
    lanes: list[dict] = []
    all_ok = True

    for g in sim_groups:
        t = g["type"]
        tdir = g["dir"]
        # per-cycle open matrix
        fieldnames = ["cyc", "I", "enable", "or4"] + [
            r["leaf"] for r in g["rows"] if r["leaf"]
        ]
        log_rows = []
        opens_found: dict[str, list[int]] = {r["leaf"]: [] for r in g["rows"]}
        for row in rows_csv:
            cyc = int(row["cyc"])
            or4 = "".join(row[f"or4{b}"] for b in "ABCD")
            rec = {
                "cyc": cyc,
                "I": row["I"],
                "enable": row["enable"],
                "or4": or4,
            }
            for m in g["rows"]:
                op = 1 if is_open(row, m) else 0
                rec[m["leaf"]] = op
                if op:
                    opens_found[m["leaf"]].append(cyc)
            log_rows.append(rec)

        with (tdir / "open_log.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for rec in log_rows:
                w.writerow({k: rec.get(k, "") for k in fieldnames})

        md = [
            f"# FA open log — type {t['index']} (`{t['label']}`)",
            "",
            "Stimulus: **all0** (FA open decode is I-independent).",
            "Sampled after each posedge with `enable=1`.",
            "",
            "| Leaf | Instance | FA open entry | Sim opens | Ref `opens_all0` | Match |",
            "|------|----------|---------------|-----------|------------------|:-----:|",
        ]
        for m in g["rows"]:
            leaf = m["leaf"]
            sim_o = opens_found[leaf]
            ref = m["opens_ref"]
            missing = [c for c in ref if c not in sim_o]
            extra = [c for c in sim_o if c not in ref]
            # Ref lists are effective I-hit cycles; sim may show one extra edge
            # (cold or4=0000 @0, last period @120). Core match = no missing.
            match = not missing
            all_ok = all_ok and match
            entry = (
                f"`{m['fa_open_net']}`=={m['open_active']}"
                if m["fa_open_net"]
                else f"`{m['open_how']}`"
            )
            note = ""
            if extra and match:
                note = f" (sim+{extra[:3]}{'…' if len(extra) > 3 else ''})"
            elif missing:
                note = f" missing={missing[:5]}"
            md.append(
                f"| `{leaf}` | `{m['instance']}` | {entry} | `{sim_o}` | `{ref}` | "
                f"{'✓' if match else '✗'}{note} |"
            )
            lanes.append(
                {
                    "label": f"t{t['index']:02d} {leaf}  {m['fa_open_net'] or m['open_how']}",
                    "group": t["index"],
                    "opens": sim_o,
                    "color": colors[t["index"]],
                    "leaf": leaf,
                    "instance": m["instance"],
                    "entry": m["fa_open_net"] or m["open_how"],
                }
            )
        md += [
            "",
            f"Figure: [`FA_open_timeline.png`](FA_open_timeline.png)",
            "",
            "## First 45 cycles (open bits)",
            "",
        ]
        hdr = "| cyc | or4 | " + " | ".join(f"`{r['leaf']}`" for r in g["rows"]) + " |"
        sep = "|----:|-----|" + "|".join(["---:"] * len(g["rows"])) + "|"
        md += [hdr, sep]
        for rec in log_rows[:45]:
            bits = " | ".join(str(rec[r["leaf"]]) for r in g["rows"])
            star = ""
            if any(rec[r["leaf"]] for r in g["rows"]):
                star = " ★"
            md.append(f"| {rec['cyc']}{star} | `{rec['or4']}` | {bits} |")
        md.append("")
        (tdir / "open_log.md").write_text("\n".join(md), encoding="utf-8")
        print(f"wrote {tdir / 'open_log.md'}")

        # Per-group FA open timeline image
        group_lanes = [L for L in lanes if L["group"] == t["index"]]
        g_png = tdir / "FA_open_timeline.png"
        plot_timeline(
            group_lanes,
            g_png,
            f"t{t['index']:02d} FA open entries · all0",
        )
        sec_png = OUT_ROOT / f"t{t['index']:02d}_FA_open_timeline.png"
        sec_png.write_bytes(g_png.read_bytes())
        print(f"wrote {g_png}")
        print(f"copied {sec_png}")

    # Combined timeline for whatever was simulated
    if len(sim_groups) > 1:
        tags = "_".join(f"t{g['type']['index']:02d}" for g in sim_groups)
        png = OUT_ROOT / f"{tags}_FA_open_timeline.png"
        plot_timeline(
            lanes,
            png,
            "FA open entries — " + ", ".join(f"t{g['type']['index']:02d}" for g in sim_groups) + " · all0",
        )
        print(f"wrote {png}")

    overview = [
        "# FA open timeline",
        "",
        "Per-group images:",
    ]
    for g in sim_groups:
        t = g["type"]
        overview.append(
            f"- [`t{t['index']:02d}_FA_open_timeline.png`](t{t['index']:02d}_FA_open_timeline.png) · "
            f"[`{t['folder']}/FA_open_timeline.png`]"
            f"({t['folder']}/FA_open_timeline.png)"
        )
    overview += [
        "",
        "Watches the **FA phase-decode open entry** for each sticky leaf "
        "(when that gate is open for an `I` compare/arm).",
        "",
        f"- Sim vs `opens_exact_shift1.json` all0: **{'PASS' if all_ok else 'MISMATCH'}**",
        "- Group folders under [`and2b_set_once/`](.)",
        "",
        "| Group | Leaf | Instance | FA open entry | #opens |",
        "|------:|------|----------|---------------|-------:|",
    ]
    for lane in lanes:
        overview.append(
            f"| t{lane['group']:02d} | `{lane['leaf']}` | `{lane['instance']}` | "
            f"`{lane['entry']}` | {len(lane['opens'])} |"
        )
    overview.append("")
    (OUT_ROOT / "FA_open_timeline.md").write_text(
        "\n".join(overview), encoding="utf-8"
    )
    print(f"match_ref={all_ok}")


if __name__ == "__main__":
    main()
