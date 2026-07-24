"""十二宫排布。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES, PALACE_NAMES
from app.ziwei.engines.calendar_engine import stem_branch_at_palace
from app.ziwei_classical.validator.rule_trace import RuleTrace

OPPOSITE_OFFSET = 6


def build_twelve_palaces(
    ming_index: int,
    shen_index: int,
    year_stem: str = "",
    trace: RuleTrace | None = None,
) -> list[dict]:
    """自命宫地支逆布十二宫名。"""
    palaces = []
    for i, name in enumerate(PALACE_NAMES):
        br_idx = (ming_index - i) % 12
        br = EARTHLY_BRANCHES[br_idx]
        gz = stem_branch_at_palace(year_stem, br_idx) if year_stem else ""
        palaces.append(
            {
                "name": name,
                "branch": br,
                "branch_index": br_idx,
                "ganzhi": gz,
                "stem": gz[:1] if gz else "",
                "opposite_branch": EARTHLY_BRANCHES[(br_idx + OPPOSITE_OFFSET) % 12],
                "is_ming_gong": br_idx == ming_index,
                "is_shen_gong": br_idx == shen_index,
                "main_stars": [],
                "lucky_stars": [],
                "evil_stars": [],
                "minor_stars": [],
            }
        )
    if trace is not None:
        trace.add(
            step="twelve_palace",
            rule="自命宫地支起，逆行排布十二宫",
            inputs={"ming_index": ming_index, "shen_index": shen_index},
            outputs={"palaces": [{"name": p["name"], "branch": p["branch"]} for p in palaces]},
            source="ziwei_classical.palace.twelve_palace",
        )
    return palaces
