#!/usr/bin/env python3
"""Complex-operator database + matcher for core success groupings.

Builds structural fingerprints of known RTL operators and scores how well
each core grouping (and combinations) matches those signatures.

OG stubs are treated as free primary inputs (black box) — never expanded.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict, deque
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
CONE_V = None  # unused — structural drivers only
OUT_DB = ROOT / "phase1" / "complex_operators_db.json"
OUT_MATCH = ROOT / "phase1" / "operator_matches.json"
OUT_TXT = ROOT / "phase1" / "operator_matches.txt"
OUT_MD = ROOT / "phase1" / "operator_matches.md"

IDENT = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")
ASSIGN_RE = re.compile(r"^\s*assign\s+(\S+)\s*=\s*(.+);")
FLOP_ELSE = re.compile(r"else\s+(\S+)\s*<=\s*(.+);")
CLK_RE = re.compile(r"always\s+@\(\s*posedge\s+(\S+)\s*\)")
INST_RE = re.compile(r"^\s*//\s+(sky130_fd_sc_hd__\S+)\s+\((\S+)\)")
STUB_RE = re.compile(r"^\s*input\s+(stub_og\S+);")

PRIMARY = {"I", "clk", "enable", "rst_n", "success"}


# ---------------------------------------------------------------------------
# Operator database — structural signatures (relative cell mixes + motifs)
# ---------------------------------------------------------------------------
OPERATOR_DB: list[dict] = [
    {
        "id": "equality_comparator",
        "name": "Equality / constant comparator",
        "description": "Bitwise XNOR (or EQ) feeding a wide AND-reduce to 1 bit.",
        "warmup_example": "comparator496",
        "expect": {
            "xnor_or_xor_frac": (0.15, 0.55),
            "and_tree_frac": (0.20, 0.70),
            "flop_frac": (0.0, 0.25),
            "mux_frac": (0.0, 0.15),
            "aoi_frac": (0.0, 0.25),
        },
        "motifs": ["and_reduce", "xnor_pair", "multi_and4"],
        "anti_motifs": ["carry_chain_dense"],
    },
    {
        "id": "ripple_adder",
        "name": "Binary adder (ripple / FA chain)",
        "description": "Per-bit XOR for sum + majority/AOI for carry (a21o/o21a/maj).",
        "warmup_example": "adder8",
        "expect": {
            "xor_frac": (0.15, 0.45),
            "aoi_frac": (0.15, 0.55),
            "and_tree_frac": (0.05, 0.35),
            "flop_frac": (0.0, 0.20),
            "mux_frac": (0.0, 0.15),
        },
        "motifs": ["xor_pair", "carry_like"],
        "anti_motifs": [],
    },
    {
        "id": "parity_xor_tree",
        "name": "Parity / XOR-tree",
        "description": "Mostly XOR/XNOR cascaded to one bit.",
        "expect": {
            "xor_frac": (0.45, 1.0),
            "and_tree_frac": (0.0, 0.25),
            "flop_frac": (0.0, 0.20),
            "mux_frac": (0.0, 0.15),
        },
        "motifs": ["xor_pair"],
        "anti_motifs": ["multi_and4"],
    },
    {
        "id": "shift_register",
        "name": "Shift register / serial-in parallel-out",
        "description": "Flop chain with mux or enable; serial bit + enable.",
        "warmup_example": "shift_register",
        "expect": {
            "flop_frac": (0.35, 0.85),
            "mux_frac": (0.05, 0.45),
            "xor_frac": (0.0, 0.20),
            "and_tree_frac": (0.0, 0.30),
        },
        "motifs": ["flop_chain", "mux_enable"],
        "anti_motifs": ["carry_chain_dense"],
    },
    {
        "id": "lfsr_crc",
        "name": "LFSR / CRC / linear feedback",
        "description": "Shift flops with XOR feedback taps.",
        "expect": {
            "flop_frac": (0.25, 0.70),
            "xor_frac": (0.10, 0.45),
            "mux_frac": (0.0, 0.30),
        },
        "motifs": ["flop_chain", "xor_pair"],
        "anti_motifs": [],
    },
    {
        "id": "sticky_sr_latch",
        "name": "Sticky set / SR-style status",
        "description": "Flop with OR-self hold (set-and-stay) or A|B delayed sticky.",
        "expect": {
            "flop_frac": (0.15, 0.70),
            "or_frac": (0.05, 0.50),
            "and_tree_frac": (0.0, 0.40),
            "xor_frac": (0.0, 0.25),
        },
        "motifs": ["sticky_or", "self_feedback"],
        "anti_motifs": [],
    },
    {
        "id": "wide_and_reduce",
        "name": "Wide AND-reduce / all-ones check",
        "description": "Tree of AND/NAND reducing many bits to one.",
        "expect": {
            "and_tree_frac": (0.45, 1.0),
            "xor_frac": (0.0, 0.20),
            "flop_frac": (0.0, 0.25),
            "mux_frac": (0.0, 0.15),
        },
        "motifs": ["and_reduce", "multi_and4"],
        "anti_motifs": ["xor_pair"],
    },
    {
        "id": "wide_or_reduce",
        "name": "Wide OR-reduce / any-ones check",
        "expect": {
            "or_frac": (0.40, 1.0),
            "xor_frac": (0.0, 0.20),
            "flop_frac": (0.0, 0.25),
        },
        "motifs": ["or_reduce"],
        "anti_motifs": [],
    },
    {
        "id": "mux_tree",
        "name": "MUX tree / datapath select",
        "expect": {
            "mux_frac": (0.30, 1.0),
            "flop_frac": (0.0, 0.40),
            "xor_frac": (0.0, 0.25),
        },
        "motifs": ["mux_enable"],
        "anti_motifs": [],
    },
    {
        "id": "onehot_priority",
        "name": "One-hot / priority / thermometer decode",
        "description": "NOR/NAND chains with mutual exclusion flavor.",
        "expect": {
            "nor_nand_frac": (0.35, 1.0),
            "xor_frac": (0.0, 0.20),
            "flop_frac": (0.0, 0.30),
        },
        "motifs": [],
        "anti_motifs": ["xor_pair"],
    },
    {
        "id": "popcount",
        "name": "Population count / adder tree of bits",
        "expect": {
            "xor_frac": (0.15, 0.45),
            "aoi_frac": (0.15, 0.50),
            "and_tree_frac": (0.10, 0.40),
            "flop_frac": (0.0, 0.20),
        },
        "motifs": ["xor_pair", "carry_like"],
        "anti_motifs": [],
    },
    {
        "id": "fsm_control",
        "name": "FSM / control decode",
        "description": "Mixed AOI with modest flops; not XOR-heavy.",
        "expect": {
            "aoi_frac": (0.20, 0.60),
            "flop_frac": (0.10, 0.45),
            "xor_frac": (0.0, 0.20),
            "mux_frac": (0.0, 0.35),
        },
        "motifs": [],
        "anti_motifs": ["xor_pair"],
    },
    {
        "id": "serial_deserializer",
        "name": "Serial bit gather + parallel check",
        "description": "Shift/flops gathering I, then AND/XNOR check — warmup shape.",
        "warmup_example": "adder_demo (shift+add+cmp)",
        "expect": {
            "flop_frac": (0.20, 0.45),
            "and_tree_frac": (0.15, 0.40),
            "xor_frac": (0.08, 0.35),
            "mux_frac": (0.0, 0.25),
            "aoi_frac": (0.05, 0.35),
        },
        "motifs": ["flop_chain", "and_reduce"],
        "anti_motifs": ["carry_chain_dense"],
        "min_nodes": 20,
    },
]


def short(n: str) -> str:
    return n.replace("sky130_fd_sc_hd__", "")


def idents(expr: str) -> set[str]:
    skip = {"if", "else", "begin", "end", "posedge", "or", "and", "xor", "nand", "nor", "not"}
    out = set()
    for m in IDENT.finditer(expr):
        name = m.group(1)
        if name in skip or re.fullmatch(r"b[0-9]+", name):
            continue
        out.add(name)
    return out


def is_clk(n: str) -> bool:
    return n == "clk" or "clkbuf" in n or n.endswith("__CLK") or n.startswith("stub_og_clk")


def classify_cell(cell: str) -> str:
    c = cell.lower()
    if "dfrtp" in c or "dfxtp" in c or "dfstp" in c:
        return "flop"
    if "mux" in c:
        return "mux"
    if "xnor" in c:
        return "xnor"
    if "xor" in c:
        return "xor"
    if c.startswith("and") or "and2" in c or "and3" in c or "and4" in c:
        return "and"
    if c.startswith("nand"):
        return "nand"
    if c.startswith("or") and "nor" not in c and "xor" not in c:
        return "or"
    if c.startswith("nor"):
        return "nor"
    if "clkbuf" in c or c.startswith("buf"):
        return "buf"
    if any(x in c for x in ("a21", "a22", "a31", "a32", "a211", "a221", "a311", "a41", "o21", "o22", "o31", "o32", "o211", "o221", "o311", "maj")):
        return "aoi"
    if "inv" in c:
        return "inv"
    return "other"


def parse_cone(path: Path):
    lines = path.read_text().splitlines()
    stubs: set[str] = set()
    drivers: dict[str, dict] = {}
    last_inst = last_cell = None
    i = 0
    while i < len(lines):
        line = lines[i]
        m = STUB_RE.match(line)
        if m:
            stubs.add(m.group(1))
            i += 1
            continue
        m = INST_RE.match(line)
        if m:
            last_inst, last_cell = m.group(1), m.group(2)
            i += 1
            continue
        m = ASSIGN_RE.match(line)
        if m:
            lhs, rhs = m.group(1), m.group(2)
            deps = idents(rhs) - {lhs}
            drivers[lhs] = {
                "deps": deps,
                "rhs": rhs,
                "kind": "assign",
                "cell": last_cell or "?",
                "instance": last_inst,
                "class": classify_cell(last_cell or ""),
            }
            last_inst = last_cell = None
            i += 1
            continue
        if line.strip().startswith("always"):
            chunk = [line]
            j = i + 1
            while j < len(lines) and "end" not in lines[j]:
                chunk.append(lines[j])
                j += 1
            if j < len(lines):
                chunk.append(lines[j])
            text = "\n".join(chunk)
            clk_m = CLK_RE.search(text)
            q = d = None
            for cl in chunk:
                me = FLOP_ELSE.search(cl)
                if me:
                    q, d = me.group(1), me.group(2).strip()
            if q and d:
                deps = idents(d) - {q}
                if clk_m:
                    deps.add(clk_m.group(1))
                deps.add("rst_n")
                drivers[q] = {
                    "deps": deps,
                    "rhs": d,
                    "kind": "flop",
                    "cell": last_cell or "dfrtp_2",
                    "instance": last_inst,
                    "class": "flop",
                    "clk": clk_m.group(1) if clk_m else None,
                }
            last_inst = last_cell = None
            i = j + 1
            continue
        i += 1
    return drivers, stubs


def fanin_nodes(root: str, drivers: dict, stubs: set[str], stop_extra: set[str] | None = None) -> set[str]:
    """Core nodes in fan-in of root; stubs/primary are leaves (not expanded)."""
    stop = set(stubs) | PRIMARY | (stop_extra or set())
    nodes: set[str] = set()
    q = deque([root])
    seen: set[str] = set()
    while q:
        n = q.popleft()
        if n in seen or is_clk(n) or n == "rst_n":
            continue
        seen.add(n)
        if n != root and n in stop:
            continue
        if n not in drivers:
            continue
        nodes.add(n)
        for d in drivers[n]["deps"]:
            if d not in seen and not is_clk(d) and d != "rst_n":
                q.append(d)
    return nodes


def fingerprint(nodes: set[str], drivers: dict, stubs: set[str], root: str) -> dict:
    classes = Counter()
    cells = Counter()
    for n in nodes:
        info = drivers[n]
        classes[info["class"]] += 1
        cells[info["cell"]] += 1
    total = max(sum(classes.values()), 1)

    def frac(*keys: str) -> float:
        return sum(classes[k] for k in keys) / total

    # Motifs
    motifs = set()
    and_n = classes["and"] + classes["nand"]
    xor_n = classes["xor"] + classes["xnor"]
    if and_n >= 4 and classes["and"] + classes["nand"] >= 0.25 * total:
        motifs.add("and_reduce")
    if cells.get("and4_2", 0) + cells.get("and4bb_2", 0) + cells.get("and4b_2", 0) >= 2:
        motifs.add("multi_and4")
    if classes["xor"] + classes["xnor"] >= 2:
        motifs.add("xor_pair")
    if classes["xnor"] >= 2:
        motifs.add("xnor_pair")
    if classes["or"] + classes["nor"] >= 4 and frac("or", "nor") >= 0.3:
        motifs.add("or_reduce")
    if classes["aoi"] >= 3 and classes["xor"] >= 2:
        motifs.add("carry_like")
    if classes["aoi"] >= 6 and frac("aoi") >= 0.25 and frac("xor", "xnor") < 0.15:
        motifs.add("carry_chain_dense")
    if classes["flop"] >= 3:
        motifs.add("flop_chain")
    if classes["mux"] >= 2:
        motifs.add("mux_enable")

    # sticky / self-feedback: RHS mentions own Q or sibling status
    for n in nodes:
        info = drivers[n]
        if info["kind"] == "flop":
            continue
        if n in info["deps"]:
            motifs.add("self_feedback")
        # a31o style sticky: output feeds flop that feeds back into OR term
    # Detect sticky_or: assign contains "| <flop>" where flop Q is in cone
    flop_qs = {n for n in nodes if drivers[n]["kind"] == "flop"}
    for n in nodes:
        rhs = drivers[n].get("rhs", "")
        for fq in flop_qs:
            if fq in drivers[n]["deps"] and "|" in rhs.replace("||", ""):
                # crude: OR with a flop bit
                if re.search(rf"\|\s*{re.escape(fq)}\b|\b{re.escape(fq)}\s*\|", rhs):
                    motifs.add("sticky_or")

    # Leaves used
    leaf_stubs = set()
    leaf_prim = set()
    for n in nodes:
        for d in drivers[n]["deps"]:
            if d in stubs:
                leaf_stubs.add(d)
            if d in {"I", "enable"}:
                leaf_prim.add(d)

    return {
        "root": short(root),
        "n_nodes": len(nodes),
        "class_counts": dict(classes),
        "cell_counts": dict(cells.most_common(20)),
        "frac": {
            "flop_frac": round(frac("flop"), 3),
            "mux_frac": round(frac("mux"), 3),
            "xor_frac": round(frac("xor", "xnor"), 3),
            "xnor_or_xor_frac": round(frac("xor", "xnor"), 3),
            "and_tree_frac": round(frac("and", "nand"), 3),
            "or_frac": round(frac("or", "nor"), 3),
            "nor_nand_frac": round(frac("nor", "nand"), 3),
            "aoi_frac": round(frac("aoi"), 3),
            "inv_frac": round(frac("inv"), 3),
        },
        "motifs": sorted(motifs),
        "stub_leaves": sorted(leaf_stubs),
        "primary_leaves": sorted(leaf_prim),
        "nodes": sorted(short(n) for n in nodes),
    }


def score_match(fp: dict, op: dict) -> dict:
    """Score 0..1 how well fingerprint matches operator expect ranges + motifs."""
    expect = op.get("expect", {})
    fr = fp["frac"]
    range_scores = []
    details = []
    for key, (lo, hi) in expect.items():
        val = fr.get(key, 0.0)
        if lo <= val <= hi:
            s = 1.0
        elif val < lo:
            s = max(0.0, 1.0 - (lo - val) / max(lo, 0.08))
        else:
            s = max(0.0, 1.0 - (val - hi) / max(1.0 - hi, 0.08))
        range_scores.append(s)
        details.append(f"{key}={val:.2f} in[{lo:.2f},{hi:.2f}]→{s:.2f}")

    motifs = set(fp["motifs"])
    want = set(op.get("motifs") or [])
    anti = set(op.get("anti_motifs") or [])
    if want:
        motif_hit = len(want & motifs) / len(want)
        # require at least one motif if operator declares them
        if motif_hit == 0:
            motif_hit = 0.0
    else:
        motif_hit = 0.4
    anti_pen = 0.20 * len(anti & motifs)

    n = fp["n_nodes"]
    min_n = op.get("min_nodes", 0)
    size_pen = 0.0
    if n < min_n:
        size_pen += 0.35
    if op["id"] in ("ripple_adder", "popcount") and n < 12:
        size_pen += 0.25
    if op["id"] == "shift_register" and (fr["flop_frac"] < 0.3 or fr["mux_frac"] < 0.08):
        size_pen += 0.2
    if op["id"] == "equality_comparator" and fr["xor_frac"] < 0.12 and fr["and_tree_frac"] < 0.35:
        size_pen += 0.15
    # Large AOI+XOR regions: boost adder/popcount slightly via less penalty
    if op["id"] in ("ripple_adder", "popcount") and fr["aoi_frac"] >= 0.2 and fr["xor_frac"] >= 0.06:
        size_pen = max(0.0, size_pen - 0.1)

    if not range_scores:
        base = 0.0
    else:
        # geometric-ish: one bad dimension hurts more
        base = sum(range_scores) / len(range_scores)
        base = base * (0.7 + 0.3 * min(range_scores))

    score = max(0.0, min(1.0, 0.55 * base + 0.45 * motif_hit - anti_pen - size_pen))
    return {
        "operator_id": op["id"],
        "operator_name": op["name"],
        "score": round(score, 3),
        "motif_hits": sorted(want & motifs),
        "anti_hits": sorted(anti & motifs),
        "range_detail": details,
    }


def _data_deps(n: str, drivers: dict) -> set[str]:
    return {d for d in drivers[n]["deps"] if not is_clk(d) and d != "rst_n"}


MUX_ASSIGN_RE = re.compile(r"^(.+?)\s*\?\s*(.+?)\s*:\s*(.+)$")


def analyze_granular(nodes: set[str], drivers: dict, stubs: set[str], root: str) -> dict:
    """Bit-width / component breakdown: shift banks, FA-like pairs, AND-reduce leaves."""
    flops = {n for n in nodes if drivers[n]["kind"] == "flop"}
    muxes = [n for n in nodes if drivers[n]["class"] == "mux"]
    xors = [n for n in nodes if drivers[n]["class"] in ("xor", "xnor")]
    aois = [n for n in nodes if drivers[n]["class"] == "aoi"]

    # --- Mux-hold shift stages: D <= mux(sel ? shift_in : Q) ---
    stages: list[dict] = []
    for m in muxes:
        mm = MUX_ASSIGN_RE.match(drivers[m]["rhs"].strip())
        if not mm:
            continue
        sel, a1, a0 = (x.strip() for x in mm.groups())
        for q in flops:
            if m not in _data_deps(q, drivers) and drivers[q]["rhs"].strip() != m:
                continue
            if a0 != q:
                continue
            stages.append(
                {
                    "flop": short(q),
                    "mux": short(m),
                    "sel": short(sel),
                    "shift_in": short(a1),
                    "hold": short(a0),
                }
            )

    by_flop = {s["flop"]: s for s in stages}
    # Banks: walk from external shift_in along stages
    succ: dict[str, list[str]] = defaultdict(list)
    for s in stages:
        succ[s["shift_in"]].append(s["flop"])

    banks: list[dict] = []
    seen_flops: set[str] = set()
    for s in stages:
        if s["shift_in"] in by_flop:
            continue  # not a head
        chain = [s["flop"]]
        cur = s["flop"]
        while True:
            nxts = [x for x in succ.get(cur, []) if x not in chain]
            if not nxts:
                break
            cur = nxts[0]
            chain.append(cur)
        for f in chain:
            seen_flops.add(f)
        serial = s["shift_in"]
        banks.append(
            {
                "bit_length": len(chain),
                "serial_in": serial,
                "serial_in_kind": (
                    "I"
                    if serial == "I"
                    else ("stub" if serial.startswith("stub_og") else "net")
                ),
                "shift_enable": s["sel"],
                "stages": chain,
            }
        )

    # Head flops driven directly by stub/I with no mux (extend bank if feeds a bank head)
    direct_serial = []
    for q in flops:
        deps = _data_deps(q, drivers)
        if len(deps) == 1:
            d = next(iter(deps))
            if d in stubs or d == "I":
                direct_serial.append({"flop": short(q), "d": short(d)})

    # If a direct-serial flop is the serial_in of a bank, merge → full SIPO width
    for b in banks:
        for ds in direct_serial:
            if b["serial_in"] == ds["flop"]:
                b["stages"] = [ds["flop"]] + b["stages"]
                b["bit_length"] = len(b["stages"])
                b["serial_in"] = ds["d"]
                b["serial_in_kind"] = "I" if ds["d"] == "I" else "stub"
                b["head_no_mux"] = True

    banks.sort(key=lambda b: -b["bit_length"])

    # --- Adder / compare ---
    fa_pairs = []
    used_aoi: set[str] = set()
    for x in xors:
        xd = _data_deps(x, drivers)
        best = None
        best_share = 0
        for a in aois:
            if a in used_aoi:
                continue
            share = len(xd & _data_deps(a, drivers))
            if share > best_share:
                best_share = share
                best = a
        if best is not None and best_share >= 2:
            used_aoi.add(best)
            fa_pairs.append(
                {
                    "sum": short(x),
                    "carry_cell": drivers[best]["cell"],
                    "carry": short(best),
                    "shared": best_share,
                }
            )

    n_xor = sum(1 for n in xors if drivers[n]["class"] == "xor")
    n_xnor = sum(1 for n in xors if drivers[n]["class"] == "xnor")

    # AOI carry-chain length (AOI → AOI)
    aoi_set = set(aois)
    aoi_succ: dict[str, list[str]] = defaultdict(list)
    aoi_pred: dict[str, list[str]] = defaultdict(list)
    for a in aois:
        for n in nodes:
            if n in aoi_set and n != a and a in _data_deps(n, drivers):
                aoi_succ[a].append(n)
                aoi_pred[n].append(a)

    def _longest(start: str, memo: dict) -> int:
        if start in memo:
            return memo[start]
        best = 1
        for n in aoi_succ[start]:
            best = max(best, 1 + _longest(n, memo))
        memo[start] = best
        return best

    carry_chain = 0
    memo: dict = {}
    for a in aois:
        if not aoi_pred[a]:
            carry_chain = max(carry_chain, _longest(a, memo))

    # Heuristic bit-width: prefer FA pairs; else ~xor count for adder-like; else xnor for compare
    est_bits = len(fa_pairs)
    est_method = "fa_pairs"
    if est_bits < 4:
        if n_xor >= 4:
            est_bits = n_xor
            est_method = "xor_count"
        elif n_xnor >= 4:
            est_bits = n_xnor
            est_method = "xnor_count"

    # --- AND-reduce leaf width from root (through and/nand/inv only) ---
    leaves: set[str] = set()
    q = deque([root] if root in drivers or root in nodes else [])
    if root in nodes or root in drivers:
        q = deque([root])
    seen: set[str] = set()
    and_nodes = 0
    while q:
        n = q.popleft()
        if n in seen:
            continue
        seen.add(n)
        if n not in drivers:
            leaves.add(n)
            continue
        cls = drivers[n]["class"]
        if cls in ("and", "nand") or n == root:
            if cls in ("and", "nand"):
                and_nodes += 1
            for d in _data_deps(n, drivers):
                q.append(d)
        elif cls == "inv":
            for d in _data_deps(n, drivers):
                q.append(d)
        else:
            leaves.add(n)

    leaf_flops = sum(1 for L in leaves if L in flops)
    leaf_stubs = sum(1 for L in leaves if L in stubs)

    components = {
        "counts": {
            "flop": len(flops),
            "mux": len(muxes),
            "xor": n_xor,
            "xnor": n_xnor,
            "aoi": len(aois),
            "and_nand": sum(1 for n in nodes if drivers[n]["class"] in ("and", "nand")),
        },
        "shifter": {
            "mux_hold_stages": len(stages),
            "banks": banks,
            "max_bank_bits": banks[0]["bit_length"] if banks else 0,
            "direct_serial_flops": direct_serial,
        },
        "adder_compare": {
            "fa_like_pairs": len(fa_pairs),
            "fa_pairs": fa_pairs[:16],
            "xor_count": n_xor,
            "xnor_count": n_xnor,
            "aoi_count": len(aois),
            "carry_aoi_chain_len": carry_chain,
            "est_datapath_bits": est_bits,
            "est_method": est_method,
        },
        "and_reduce": {
            "and_nodes": and_nodes,
            "leaf_count": len(leaves),
            "leaf_flops": leaf_flops,
            "leaf_stubs": leaf_stubs,
            "leaves": [short(x) for x in sorted(leaves, key=short)],
        },
    }

    # One-line summary for reports
    parts = []
    if banks:
        b0 = banks[0]
        parts.append(
            f"shifter {b0['bit_length']}-bit (in={b0['serial_in']}, en={b0['shift_enable']})"
        )
        if len(banks) > 1:
            parts.append(f"+{len(banks)-1} smaller bank(s)")
    if len(fa_pairs) >= 2 or n_xor + n_xnor >= 6:
        parts.append(
            f"arith ~{est_bits}-bit via {est_method} "
            f"(FA={len(fa_pairs)}, xor={n_xor}, xnor={n_xnor}, carry_len={carry_chain})"
        )
    if len(leaves) >= 3 and and_nodes >= 2:
        parts.append(f"AND-reduce width≈{len(leaves)} (flops={leaf_flops}, stubs={leaf_stubs})")
    components["summary"] = "; ".join(parts) if parts else "no strong width signal"

    return components


def main() -> None:
    # Trusted path: structural from Magic gates (not puzzle_core / no_og stubs).
    from structural_drivers import STRUCTURAL_V, parse_structural

    drivers, stubs, meta = parse_structural(STRUCTURAL_V)
    print(f"match_complex_operators source: {meta}")

    # Define groupings (roots) and combinations
    groups = {
        "G_success_glue": "sky130_fd_sc_hd__a32o_2_4__X",
        "G_and4b_join": "sky130_fd_sc_hd__and4b_2_3__X",
        "G_main_check": "sky130_fd_sc_hd__and3_2_6__X",
        "G_status_A": "sky130_fd_sc_hd__or2_2_11__A",
        "G_status_B": "sky130_fd_sc_hd__or2_2_11__B",
        "G_set_and2": "sky130_fd_sc_hd__and2_2_15__X",
        "G_set_inv": "sky130_fd_sc_hd__inv_2_23__A",
        "G_hold_B2": "sky130_fd_sc_hd__a32o_2_4__B2",
    }

    # Combinations: union of node sets
    combos = [
        ("C_status_A_plus_B", ["G_status_A", "G_status_B"]),
        ("C_and4b_all_inputs", ["G_main_check", "G_status_A", "G_status_B"]),
        ("C_full_set_path", ["G_and4b_join", "G_set_and2", "G_set_inv"]),
        ("C_set_plus_hold", ["G_and4b_join", "G_set_and2", "G_set_inv", "G_hold_B2"]),
        ("C_main_plus_statusA", ["G_main_check", "G_status_A"]),
        ("C_entire_a32o", ["G_success_glue"]),
    ]

    fps: dict[str, dict] = {}
    granular: dict[str, dict] = {}
    node_sets: dict[str, set[str]] = {}
    for gid, root in groups.items():
        if root not in drivers and root != "success":
            # status flops should exist
            pass
        nodes = fanin_nodes(root, drivers, stubs)
        node_sets[gid] = nodes
        fps[gid] = fingerprint(nodes, drivers, stubs, root)
        granular[gid] = analyze_granular(nodes, drivers, stubs, root)

    for cid, parts in combos:
        merged: set[str] = set()
        for p in parts:
            merged |= node_sets.get(p, set())
        # fake root = first part root
        root = groups[parts[0]]
        node_sets[cid] = merged
        fps[cid] = fingerprint(merged, drivers, stubs, root)
        fps[cid]["root"] = cid
        fps[cid]["combined_from"] = parts
        granular[cid] = analyze_granular(merged, drivers, stubs, root)

    # Score all
    matches = {}
    for gid, fp in fps.items():
        scored = [score_match(fp, op) for op in OPERATOR_DB]
        scored.sort(key=lambda s: -s["score"])
        matches[gid] = {
            "fingerprint": {k: v for k, v in fp.items() if k != "nodes"},
            "granular": granular[gid],
            "top_matches": scored[:5],
            "best": scored[0] if scored else None,
        }

    # Rank regions by best score
    ranking = sorted(
        (
            {
                "group": gid,
                "n_nodes": fps[gid]["n_nodes"],
                "best_op": matches[gid]["best"]["operator_name"],
                "best_id": matches[gid]["best"]["operator_id"],
                "score": matches[gid]["best"]["score"],
                "motifs": fps[gid]["motifs"],
                "frac": fps[gid]["frac"],
                "granular_summary": granular[gid].get("summary", ""),
                "shifter_max_bits": granular[gid]["shifter"]["max_bank_bits"],
                "est_datapath_bits": granular[gid]["adder_compare"]["est_datapath_bits"],
                "fa_like_pairs": granular[gid]["adder_compare"]["fa_like_pairs"],
                "and_reduce_leaves": granular[gid]["and_reduce"]["leaf_count"],
            }
            for gid in fps
        ),
        key=lambda r: -r["score"],
    )

    OUT_DB.write_text(json.dumps(OPERATOR_DB, indent=2), encoding="utf-8")
    OUT_MATCH.write_text(
        json.dumps({"ranking": ranking, "matches": matches}, indent=2),
        encoding="utf-8",
    )

    # Text report
    L = []
    L.append("COMPLEX OPERATOR MATCH — CORE GROUPINGS")
    L.append("=" * 64)
    L.append(f"Operator DB entries: {len(OPERATOR_DB)}")
    L.append(f"Groupings scored:    {len(fps)}")
    L.append("OG stubs treated as black-box inputs (not expanded).")
    L.append("")
    L.append("RANKING (best operator match per group/combo)")
    L.append("-" * 64)
    for r in ranking:
        L.append(
            f"  {r['score']:.3f}  {r['group']:28}  n={r['n_nodes']:3d}  → {r['best_op']}"
        )
        L.append(f"         motifs={r['motifs']}")
        fr = r["frac"]
        L.append(
            f"         flop={fr['flop_frac']:.2f} xor={fr['xor_frac']:.2f} "
            f"and={fr['and_tree_frac']:.2f} aoi={fr['aoi_frac']:.2f} mux={fr['mux_frac']:.2f}"
        )
        if r.get("granular_summary"):
            L.append(f"         width: {r['granular_summary']}")
    L.append("")
    L.append("GRANULAR STRUCTURE (≥0.55 score)")
    L.append("-" * 64)
    for r in ranking:
        if r["score"] < 0.55:
            continue
        g = granular[r["group"]]
        L.append("")
        L.append(f"### {r['group']} → {r['best_op']} ({r['score']:.3f})")
        L.append(f"    counts: {g['counts']}")
        sh = g["shifter"]
        L.append(
            f"    shifter: mux_hold_stages={sh['mux_hold_stages']} "
            f"max_bank={sh['max_bank_bits']}-bit  banks={len(sh['banks'])}"
        )
        for b in sh["banks"]:
            L.append(
                f"      bank {b['bit_length']}-bit  in={b['serial_in']} "
                f"({b['serial_in_kind']})  en={b['shift_enable']}"
            )
            L.append(f"        stages: {' -> '.join(b['stages'])}")
        if sh["direct_serial_flops"]:
            L.append(f"      direct_serial: {sh['direct_serial_flops']}")
        ac = g["adder_compare"]
        L.append(
            f"    adder/compare: est≈{ac['est_datapath_bits']}-bit ({ac['est_method']})  "
            f"FA_pairs={ac['fa_like_pairs']} xor={ac['xor_count']} xnor={ac['xnor_count']} "
            f"aoi={ac['aoi_count']} carry_chain={ac['carry_aoi_chain_len']}"
        )
        for p in ac["fa_pairs"][:6]:
            L.append(
                f"      FA {p['sum']} + {p['carry']}[{p['carry_cell']}] share={p['shared']}"
            )
        ar = g["and_reduce"]
        L.append(
            f"    AND-reduce: leaves={ar['leaf_count']} "
            f"(flops={ar['leaf_flops']}, stubs={ar['leaf_stubs']}) and_nodes={ar['and_nodes']}"
        )
        if ar["leaves"]:
            L.append(f"      leaves: {', '.join(ar['leaves'][:24])}")
    L.append("")
    strong = [r for r in ranking if r["score"] >= 0.55]
    L.append("SUMMARY")
    if strong:
        L.append(f"  Strong matches (≥0.55): {len(strong)}")
        for r in strong:
            L.append(f"    - {r['group']}: {r['best_op']} ({r['score']:.3f})")
            if r.get("granular_summary"):
                L.append(f"        {r['granular_summary']}")
    else:
        L.append("  No strong matches (≥0.55). Best candidates below 0.55 — partial resemblance only.")
    OUT_TXT.write_text("\n".join(L) + "\n", encoding="utf-8")

    md = []
    md.append("# Complex operator matching (success groupings)")
    md.append("")
    md.append("Database: `complex_operators_db.json` · Results: `operator_matches.json`")
    md.append("")
    md.append(
        "Source: `rework/netlist/puzzle_structural.v` "
        "(from trusted `puzzle_gates.spice`). OG cells are expanded."
    )
    md.append("")
    md.append("## Ranking")
    md.append("")
    md.append("| Score | Group | Nodes | Best operator | Width / components |")
    md.append("|---:|---|---:|---|---|")
    for r in ranking:
        md.append(
            f"| {r['score']:.3f} | `{r['group']}` | {r['n_nodes']} | {r['best_op']} | "
            f"{r.get('granular_summary') or '—'} |"
        )
    md.append("")
    md.append("## Granular structure (strong matches)")
    md.append("")
    for r in ranking:
        if r["score"] < 0.55:
            continue
        g = granular[r["group"]]
        md.append(f"### `{r['group']}` → {r['best_op']} ({r['score']:.3f})")
        md.append("")
        md.append(f"- **Cell mix:** `{g['counts']}`")
        sh = g["shifter"]
        if sh["banks"]:
            md.append(
                f"- **Shifter:** {sh['max_bank_bits']}-bit max bank, "
                f"{sh['mux_hold_stages']} mux-hold stages"
            )
            for b in sh["banks"]:
                md.append(
                    f"  - `{b['bit_length']}-bit` serial_in=`{b['serial_in']}` "
                    f"({b['serial_in_kind']}), enable=`{b['shift_enable']}`"
                )
                md.append(f"    - stages: `{' → '.join(b['stages'])}`")
        else:
            md.append("- **Shifter:** no mux-hold bank detected")
        ac = g["adder_compare"]
        md.append(
            f"- **Adder/compare:** est **~{ac['est_datapath_bits']}-bit** "
            f"(`{ac['est_method']}`); FA-like pairs={ac['fa_like_pairs']}, "
            f"xor={ac['xor_count']}, xnor={ac['xnor_count']}, "
            f"aoi={ac['aoi_count']}, carry-AOI chain={ac['carry_aoi_chain_len']}"
        )
        ar = g["and_reduce"]
        md.append(
            f"- **AND-reduce:** {ar['leaf_count']} leaves "
            f"({ar['leaf_flops']} flops, {ar['leaf_stubs']} stubs)"
        )
        md.append("")
    md.append("## Operators in the database")
    md.append("")
    for op in OPERATOR_DB:
        md.append(f"- **{op['name']}** (`{op['id']}`): {op.get('description', '')}")
    md.append("")
    md.append("## How to read scores")
    md.append("")
    md.append("- **≥ 0.70** — strong structural match")
    md.append("- **0.55–0.70** — plausible")
    md.append("- **0.45–0.55** — weak / partial")
    md.append("- **< 0.45** — unlikely")
    md.append("")
    md.append("## Width heuristics")
    md.append("")
    md.append("- **Shifter bits:** length of mux-hold flop chain (hold=`Q`, shift=`prev`), "
              "plus a no-mux head flop when its Q is the bank serial_in.")
    md.append("- **Adder bits:** count of XOR↔AOI pairs sharing ≥2 inputs (FA-like); "
              "fallback to xor/xnor counts when FA pairing is sparse.")
    md.append("- **AND-reduce width:** leaf fan-in of the group root through AND/NAND/INV only.")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(OUT_TXT.read_text())
    print(f"Wrote {OUT_DB}")
    print(f"Wrote {OUT_MATCH}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
