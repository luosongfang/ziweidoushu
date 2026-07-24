"""身宫 — 寅起正月顺数生月，顺数生时。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES, YIN_BRANCH_INDEX
from app.ziwei_classical.validator.rule_trace import RuleTrace

SHEN_GONG_RULE = (
    "寅起正月顺数至生月得月支；自月支顺数至生时辰得身宫。"
    "公式：month_idx=(寅+month-1)%12；shen=(month_idx+hour)%12"
)


def calc_shen_gong(
    lunar_month: int,
    hour_index: int,
    trace: RuleTrace | None = None,
) -> dict:
    month_idx = (YIN_BRANCH_INDEX + lunar_month - 1) % 12
    shen_idx = (month_idx + hour_index) % 12
    out = {
        "branch": EARTHLY_BRANCHES[shen_idx],
        "branch_index": shen_idx,
        "month_branch": EARTHLY_BRANCHES[month_idx],
    }
    if trace is not None:
        trace.add(
            step="shen_gong",
            rule=SHEN_GONG_RULE,
            inputs={"lunar_month": lunar_month, "hour_index": hour_index},
            outputs=out,
            source="ziwei_classical.palace.shen_gong",
        )
    return out
