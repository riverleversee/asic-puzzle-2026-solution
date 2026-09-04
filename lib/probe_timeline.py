#!/usr/bin/env python3
"""Shared structural-sim probe harness for phase2 timelines."""
from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


def family(cell: str) -> str:
    return re.sub(r"_\d+$", "", cell.replace("sky130_fd_sc_hd__", ""))


def cells_used(struct: Path) -> set[str]:
    text = struct.read_text(encoding="utf-8", errors="replace")
    return {
        c
        for c in re.findall(r"sky130_fd_sc_hd__\w+", text)
        if re.match(r"sky130_fd_sc_hd__\w+_\d+$", c)
    }


def iverilog_cmd(iv: Path, struct: Path, pdk: Path, inc: Path, vvp: Path, tb: Path) -> list[str]:
    cmd = [
        str(iv),
        "-g2012",
        "-DFUNCTIONAL",
        "-DUNIT_DELAY=#1",
        "-I",
        str(inc),
        "-o",
        str(vvp),
    ]
    for c in sorted(cells_used(struct)):
        p = pdk / "cells" / family(c) / f"{c}.v"
        if p.exists():
            cmd.append(str(p))
    cmd += [str(struct), str(tb)]
    return cmd


def pat_bits(n_cyc: int, ones: list[int] | None = None, fill: str = "0") -> str:
    bits = [fill] * n_cyc
    for i in ones or []:
        if 0 <= i < n_cyc:
            bits[i] = "1" if fill == "0" else "0"
    return "".join(bits)


def run_probe(
    *,
    root: Path,
    build: Path,
    out_dir: Path,
    tag: str,
    probes: list[tuple[str, str]],
    modes: list[tuple[str, str]],
    n_cyc: int = 121,
) -> list[dict]:
    """Compile+sim; return list of CSV row dicts with mode name resolved.

    probes: (csv_label, net) — net is I/enable or uut net.
    modes: (name, bitstring of length n_cyc)
    """
    from run_sim import find_iverilog

    repo = root.parent
    struct = root / "netlist" / "puzzle_structural.v"
    pdk = repo / "netlist" / "structural" / "pdk"
    inc = pdk / "include"
    build.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    labels = [p[0] for p in probes]
    n = len(probes)
    n_pat = len(modes)
    pats = build / f"pats_{tag}.txt"
    pats.write_text("\n".join(m[1] for m in modes) + "\n", encoding="utf-8")

    dumps = []
    for i, (_lab, net) in enumerate(probes):
        if net in ("I", "enable"):
            dumps.append(f"        bits[{i}] = {net};")
        else:
            dumps.append(f"        bits[{i}] = uut.{net};")

    csv_raw = build / f"probe_{tag}.csv"
    tb = build / f"tb_{tag}.v"
    vvp = build / f"tb_{tag}.vvp"
    tb.write_text(
        f"""`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O; wire success;
  reg [{n_cyc-1}:0] pat [0:{n_pat-1}];
  reg [{n-1}:0] bits;
  integer mode, cyc, fd, i;
  puzzle uut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),
    .O_0(O[0]),.O_1(O[1]),.O_2(O[2]),.O_3(O[3]),
    .O_4(O[4]),.O_5(O[5]),.O_6(O[6]),.O_7(O[7]),.success(success));
  always #5 clk = ~clk;
  initial begin
    $readmemb("{pats.as_posix()}", pat);
    fd = $fopen("{csv_raw.as_posix()}", "w");
    $fwrite(fd, "mode,cyc,{','.join(labels)}\\n");
    for (mode=0; mode<{n_pat}; mode=mode+1) begin
      rst_n=0; enable=0; I=0;
      repeat(3) @(posedge clk);
      rst_n=1; @(posedge clk);
      enable=1;
      for (cyc=0; cyc<{n_cyc}; cyc=cyc+1) begin
        // $readmemb: left char = MSB = bit[n_cyc-1]. pat_bits writes cycle i as char i.
        @(negedge clk); I = pat[mode][{n_cyc}-1-cyc];
        @(posedge clk); #1;
{chr(10).join(dumps)}
        $fwrite(fd, "%0d,%0d", mode, cyc);
        for (i=0; i<{n}; i=i+1) $fwrite(fd, ",%0d", bits[i]);
        $fwrite(fd, "\\n");
      end
    end
    $fclose(fd); $finish;
  end
endmodule
""",
        encoding="utf-8",
    )

    iv, vvp_bin = find_iverilog()
    print(f"compile {tag}…", flush=True)
    r = subprocess.run(
        iverilog_cmd(iv, struct, pdk, inc, vvp, tb),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if r.returncode:
        raise SystemExit((r.stderr or r.stdout)[-4000:])
    print(f"simulate {tag} ({n_pat} modes)…", flush=True)
    r2 = subprocess.run([str(vvp_bin), str(vvp)], capture_output=True, text=True, timeout=600)
    if r2.returncode:
        raise SystemExit((r2.stdout + r2.stderr)[-4000:])

    rows = list(csv.DictReader(csv_raw.open(encoding="utf-8")))
    name_by_i = {i: m[0] for i, m in enumerate(modes)}
    for row in rows:
        row["mode_name"] = name_by_i[int(row["mode"])]
    return rows


def ones(rows: list[dict], key: str) -> list[int]:
    return [int(r["cyc"]) for r in rows if int(r[key])]
