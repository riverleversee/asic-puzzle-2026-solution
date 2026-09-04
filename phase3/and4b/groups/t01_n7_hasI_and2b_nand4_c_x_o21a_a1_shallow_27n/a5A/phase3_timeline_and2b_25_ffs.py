#!/usr/bin/env python3
"""Timeline of FFs in the and2b_2_25 / and4_2_5__A shallow cone (t01).

Visible flops from the depth-5 figure:
  dfrtp_2_80.Q = nand4_2_9__C   (and2b A_N)
  dfrtp_2_66.Q = o21a_2_21__A1  (and2b B)
  dfrtp_2_44.Q = or4_2_4__A     (FA)
  dfrtp_2_43.Q = or4_2_4__B
  dfrtp_2_46.Q = or4_2_4__C
  dfrtp_2_45.Q = or4_2_4__D

Usage (from rework/):
  export PATH="$HOME/tools/oss-cad-suite/bin:$PATH"
  python3 tools/phase3_timeline_and2b_25_ffs.py
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
CPSAT = REPO / "sim" / "cpsat_exact.json"
N_CYC = 40  # early window is enough for initial FF state

# label → hierarchical net inside uut
PROBES = [
    ("I", "I"),
    ("enable", "enable"),
    ("ff_AN", "sky130_fd_sc_hd__nand4_2_9__C"),       # dfrtp_2_80
    ("ff_B", "sky130_fd_sc_hd__o21a_2_21__A1"),        # dfrtp_2_66
    ("and2b_Y", "sky130_fd_sc_hd__and4_2_5__A"),       # and2b_2_25
    ("or4A", "sky130_fd_sc_hd__or4_2_4__A"),            # dfrtp_2_44
    ("or4B", "sky130_fd_sc_hd__or4_2_4__B"),            # dfrtp_2_43
    ("or4C", "sky130_fd_sc_hd__or4_2_4__C"),            # dfrtp_2_46
    ("or4D", "sky130_fd_sc_hd__or4_2_4__D"),            # dfrtp_2_45
    ("inv7", "sky130_fd_sc_hd__inv_2_7__A"),
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


def build_patterns() -> list[tuple[str, str]]:
    pats = [("all0", "0" * N_CYC)]
    if CPSAT.exists():
        ones = set(json.loads(CPSAT.read_text(encoding="utf-8"))["I_ones"])
        val = sum(1 << c for c in ones if 0 <= c < N_CYC)
        pats.append(("cpsat", format(val, f"0{N_CYC}b")))
    return pats


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    pats = build_patterns()
    pats_path = BUILD / "pats_and2b25_ff.txt"
    pats_path.write_text("\n".join(p[1] for p in pats) + "\n", encoding="utf-8")

    labels = [p[0] for p in PROBES]
    n = len(PROBES)
    dumps = []
    for i, (lab, net) in enumerate(PROBES):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = BUILD / "probe_and2b25_ff.csv"
    tb = BUILD / "tb_and2b25_ff.v"
    vvp = BUILD / "tb_and2b25_ff.vvp"
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
      // sample right after async reset held (still rst_n=0)
      #1;
{chr(10).join(dumps)}
      $fwrite(fd, "%0d,%0d", mode, -1);
      for (i=0; i<{n}; i=i+1) $fwrite(fd, ",%0d", bits[i]);
      $fwrite(fd, "\\n");
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

    out_csv = OUT_DIR / "and2b_2_25_ff_timeline.csv"
    fields = ["label", "mode", "cyc"] + labels
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})

    # Markdown timeline (cpsat + all0), first 24 cycles + reset sample
    md = [
        "# FF timeline — `and2b_2_25` / `and4_2_5__A` (t01 shallow)",
        "",
        "From figure `and4b_main_groups/t01_…/and2b_2_25_out_and4_2_5__A_d5.png`.",
        "",
        "| Probe | Instance / net | Role |",
        "|-------|----------------|------|",
        "| `ff_AN` | `dfrtp_2_80.Q` = `nand4_2_9__C` | and2b **A_N** |",
        "| `ff_B` | `dfrtp_2_66.Q` = `o21a_2_21__A1` | and2b **B** |",
        "| `and2b_Y` | `and2b_2_25.X` = `and4_2_5__A` | `Y = ¬A_N ∧ B` wait: and2b is `(¬A_N)∧B` |",
        "| `or4A..D` | `dfrtp_2_44/43/46/45.Q` | FA `or4_2_4` |",
        "",
        "`cyc=-1` = held in reset (`rst_n=0`, `enable=0`) — **initial FF state**.",
        "",
    ]

    for lab in mode_labels:
        sub = [r for r in rows if r["label"] == lab]
        md += [f"## Pattern `{lab}`", ""]
        # reset + first 24
        show = [r for r in sub if int(r["cyc"]) < 24]
        hdr = "| cyc | I | en | ff_AN | ff_B | Y | or4 | inv7 |"
        sep = "|----:|--:|---:|------:|-----:|--:|-----|------|"
        md += [hdr, sep]
        for r in show:
            or4 = f"{r['or4A']}{r['or4B']}{r['or4C']}{r['or4D']}"
            md.append(
                f"| {r['cyc']} | {r['I']} | {r['enable']} | {r['ff_AN']} | {r['ff_B']} | "
                f"{r['and2b_Y']} | `{or4}` | {r['inv7']} |"
            )
        md.append("")

        # first time each leaf FF leaves 0
        for name in ("ff_AN", "ff_B", "and2b_Y"):
            rise = next((r for r in sub if int(r["cyc"]) >= 0 and r[name] == "1"), None)
            if rise:
                md.append(f"- First `{name}=1` @ cyc **{rise['cyc']}**")
            else:
                md.append(f"- `{name}` stays 0 through cyc {N_CYC - 1}")
        md.append("")

    out_md = OUT_DIR / "and2b_2_25_ff_timeline.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")

    # Print compact view for chat
    print("\n=== INITIAL (cyc=-1, in reset) ===")
    for lab in mode_labels:
        r = next(x for x in rows if x["label"] == lab and x["cyc"] == "-1")
        print(
            f"  {lab}: ff_AN={r['ff_AN']} ff_B={r['ff_B']} Y={r['and2b_Y']} "
            f"or4={r['or4A']}{r['or4B']}{r['or4C']}{r['or4D']} inv7={r['inv7']}"
        )
    print("\n=== cpsat first 16 cycles ===")
    print("cyc I AN B Y or4")
    for r in rows:
        if r["label"] != "cpsat" or int(r["cyc"]) >= 16 or int(r["cyc"]) < 0:
            continue
        print(
            f"{r['cyc']:>3} {r['I']}  {r['ff_AN']}  {r['ff_B']} {r['and2b_Y']} "
            f"{r['or4A']}{r['or4B']}{r['or4C']}{r['or4D']}"
        )


if __name__ == "__main__":
    main()
