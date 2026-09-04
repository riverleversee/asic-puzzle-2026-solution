#!/usr/bin/env python3
"""Sim and2b_2_25 / a5.A pins with k=2 vs k=3 ones on a5.A open window.

Leaf a5.A (set_once, and4b_D): open_net = nand4_2_9__D
  exact opens = [5, 16, 27, 38, 49, 60, 71, 82, 93, 104, 115]
Cone FFs: dfrtp_2_80 (A_N), dfrtp_2_66 (B), FA or4_2_4.

Usage (from rework/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 tools/phase3_a5A_k2_k3_timeline.py
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

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

STRUCT = ROOT / "netlist" / "puzzle_structural.v"
PDK = REPO / "netlist" / "structural" / "pdk"
INC = PDK / "include"
OUT_DIR = HERE
BUILD = ROOT / "phase3" / "build"
OPENS_JSON = REPO / "sim" / "opens_exact_shift1.json"
N_CYC = 121

PROBES = [
    ("I", "I"),
    ("enable", "enable"),
    ("openD", "sky130_fd_sc_hd__nand4_2_9__D"),  # a5.A open decode
    ("ff_AN", "sky130_fd_sc_hd__nand4_2_9__C"),  # dfrtp_2_80
    ("ff_B", "sky130_fd_sc_hd__o21a_2_21__A1"),  # dfrtp_2_66
    ("and2b_Y", "sky130_fd_sc_hd__and4_2_5__A"),
    ("or4A", "sky130_fd_sc_hd__or4_2_4__A"),
    ("or4B", "sky130_fd_sc_hd__or4_2_4__B"),
    ("or4C", "sky130_fd_sc_hd__or4_2_4__C"),
    ("or4D", "sky130_fd_sc_hd__or4_2_4__D"),
]


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


def load_a5a_opens() -> list[int]:
    data = json.loads(OPENS_JSON.read_text(encoding="utf-8"))
    for leaf in data["opens"]:
        if leaf["name"] == "a5.A":
            return [c for c in leaf["opens_all0"] if 0 <= c < N_CYC]
    raise SystemExit("a5.A not found in opens_exact_shift1.json")


def bits_from_ones(ones: set[int]) -> str:
    val = sum(1 << c for c in ones if 0 <= c < N_CYC)
    return format(val, f"0{N_CYC}b")


def main() -> None:
    opens = load_a5a_opens()
    k2_ones = set(opens[:2])
    k3_ones = set(opens[:3])
    pats = [
        ("k2", bits_from_ones(k2_ones)),
        ("k3", bits_from_ones(k3_ones)),
    ]
    print(f"a5.A opens ({len(opens)}): {opens}")
    print(f"k2 ones @ {sorted(k2_ones)}")
    print(f"k3 ones @ {sorted(k3_ones)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    pats_path = BUILD / "pats_a5A_k2k3.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")

    labels = [p[0] for p in PROBES]
    n = len(PROBES)
    dumps = []
    for i, (_lab, net) in enumerate(PROBES):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_a5A_k2k3.csv"
    tb = BUILD / "tb_a5A_k2k3.v"
    vvp = BUILD / "tb_a5A_k2k3.vvp"
    n_pat = len(pats)

    tb.write_text(
        f"""`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O;
  wire success;
  reg [{N_CYC-1}:0] pat [0:{n_pat-1}];
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
    for (mode=0; mode<{n_pat}; mode=mode+1) begin
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
    mode_labels = [p[0] for p in pats]
    for row in rows:
        row["label"] = mode_labels[int(row["mode"])]

    out_csv = OUT_DIR / "a5A_k2_k3_timeline.csv"
    fields = ["label", "mode", "cyc"] + labels
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})

    open_set = set(opens)
    interesting = sorted(
        set(range(0, 35))
        | {c - 1 for c in opens[:4] if c > 0}
        | set(opens[:4])
        | {c + 1 for c in opens[:4]}
        | {c + 2 for c in opens[:4]}
    )
    interesting = [c for c in interesting if 0 <= c < N_CYC]

    md = [
        "# a5.A open-window ones: k=2 vs k=3",
        "",
        "Leaf **`a5.A`** (`set_once`, bank `and4b_D`) drives the shallow "
        "`and2b_2_25` cone (`and4_2_5__A`).",
        "",
        f"- Open net: `nand4_2_9__D`",
        f"- Exact opens: `{opens}`",
        f"- **k2** I=1 @ `{sorted(k2_ones)}`",
        f"- **k3** I=1 @ `{sorted(k3_ones)}`",
        "",
        "Probes: `ff_AN`=`dfrtp_2_80.Q`, `ff_B`=`dfrtp_2_66.Q`, "
        "`and2b_Y`=`and2b_2_25.X`, `openD`=`nand4_2_9__D`.",
        "",
    ]

    for lab, ones in (("k2", k2_ones), ("k3", k3_ones)):
        sub = [r for r in rows if r["label"] == lab]
        md += [f"## Pattern `{lab}` — I=1 on {len(ones)} opens", ""]

        # event summary
        def first(name: str, val: str = "1"):
            hit = next((r for r in sub if r[name] == val), None)
            return hit["cyc"] if hit else None

        def last(name: str, val: str = "1"):
            hits = [r for r in sub if r[name] == val]
            return hits[-1]["cyc"] if hits else None

        md += [
            f"- `ff_AN` first 1 @ **{first('ff_AN')}** · last 1 @ **{last('ff_AN')}** · "
            f"high cycles: {sum(1 for r in sub if r['ff_AN']=='1')}",
            f"- `ff_B` first 1 @ **{first('ff_B')}** · last 1 @ **{last('ff_B')}** · "
            f"high cycles: {sum(1 for r in sub if r['ff_B']=='1')}",
            f"- `and2b_Y` first 1 @ **{first('and2b_Y')}** · high cycles: "
            f"{sum(1 for r in sub if r['and2b_Y']=='1')}",
            "",
            "| cyc | I | open? | openD | ff_AN | ff_B | Y | or4 |",
            "|----:|--:|:-----:|------:|------:|-----:|--:|-----|",
        ]
        by_cyc = {int(r["cyc"]): r for r in sub}
        for c in interesting:
            r = by_cyc[c]
            or4 = f"{r['or4A']}{r['or4B']}{r['or4C']}{r['or4D']}"
            star = "★" if c in open_set else ""
            md.append(
                f"| {c} | {r['I']} | {star} | {r['openD']} | {r['ff_AN']} | "
                f"{r['ff_B']} | {r['and2b_Y']} | `{or4}` |"
            )
        md.append("")

    out_md = OUT_DIR / "a5A_k2_k3_timeline.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")

    # Console: side-by-side around first three opens
    print("\n=== around opens 5,16,27 ===")
    print("cyc  k2:I AN B Y   k3:I AN B Y")
    for c in range(4, 32):
        a = next(r for r in rows if r["label"] == "k2" and int(r["cyc"]) == c)
        b = next(r for r in rows if r["label"] == "k3" and int(r["cyc"]) == c)
        mark = " ★" if c in open_set else ""
        print(
            f"{c:>3}{mark:2}  {a['I']} {a['ff_AN']} {a['ff_B']} {a['and2b_Y']}    "
            f"{b['I']} {b['ff_AN']} {b['ff_B']} {b['and2b_Y']}"
        )


if __name__ == "__main__":
    main()
