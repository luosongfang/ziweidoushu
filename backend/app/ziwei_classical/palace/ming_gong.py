"""命宫 — 传统三合：寅起正月顺数生月，自月支逆数生时。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES, YIN_BRANCH_INDEX
from app.ziwei.engines.calendar_engine import stem_branch_at_palace
from app.ziwei_classical.validator.rule_trace import RuleTrace

# 口诀（与 ALGORITHM / PalaceEngine 一致，可 trace）
MING_GONG_RULE = (
    "寅起正月顺数至生月得月支；自月支逆数至生时辰得命宫。"
    "公式：month_idx=(寅+month-1)%12；ming=(month_idx-hour+12)%12"
)


def calc_ming_gong(
    lunar_month: int,
    hour_index: int,
    year_stem: str = "",
    trace: RuleTrace | None = None,
) -> dict:
    month_idx = (YIN_BRANCH_INDEX + lunar_month - 1) % 12
    ming_idx = (month_idx - hour_index + 12) % 12
    branch = EARTHLY_BRANCHES[ming_idx]
    stem_branch = stem_branch_at_palace(year_stem, ming_idx) if year_stem else branch
    out = {
        "branch": branch,
        "branch_index": ming_idx,
        "ganzhi": stem_branch,
        "stem": stem_branch[0] if len(stem_branch) >= 2 else "",
        "month_branch": EARTHLY_BRANCHES[month_idx],
    }
    if trace is not None:
        trace.add(
            step="ming_gong",
            rule=MING_GONG_RULE,
            inputs={"lunar_month": lunar_month, "hour_index": hour_index, "year_stem": year_stem},
            outputs=out,
            source="ziwei_classical.palace.ming_gong",
        )
    return out
