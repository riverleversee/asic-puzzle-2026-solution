"""Rule-based logic structure catalog + recognition + block render."""

from structures.graph import Check, Match, fanin_cone, short
from structures.recognize import all_matches, greedy_cover, recognize_cone
from structures.render_blocks import render_block_fanin, write_block_md

__all__ = [
    "Check",
    "Match",
    "fanin_cone",
    "short",
    "all_matches",
    "greedy_cover",
    "recognize_cone",
    "render_block_fanin",
    "write_block_md",
]
