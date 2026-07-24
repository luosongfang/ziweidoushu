"""命宫规则执行 — 来自 rule catalog，非单盘硬编码。"""

from __future__ import annotations

from typing import Any

from app.ziwei.constants import EARTHLY_BRANCHES, YIN_BRANCH_INDEX
from app.ziwei.engines.calendar_engine import stem_branch_at_palace
from app.ziwei_classical.rules.loader import assert_has_source, get_ming_rule
from app.ziwei_classical.validator.classical_trace import ClassicalTrace


def apply_ming_gong_rule(
    lunar_month: int,
    hour_index: int,
    year_stem: str = "",
    trace: ClassicalTrace | None = None,
) -> dict[str, Any]:
    rule = get_ming_rule()
    assert_has_source(rule)
    month_idx = (YIN_BRANCH_INDEX + lunar_month - 1) % 12
    ming_idx = (month_idx - hour_index + 12) % 12
    branch = EARTHLY_BRANCHES[ming_idx]
    ganzhi = stem_branch_at_palace(year_stem, ming_idx) if year_stem else branch
    result = {
        "branch": branch,
        "branch_index": ming_idx,
        "ganzhi": ganzhi,
        "stem": ganzhi[:1] if len(ganzhi) >= 2 else "",
        "month_branch": EARTHLY_BRANCHES[month_idx],
        "rule_id": rule["id"],
    }
    if trace is not None:
        trace.add(
            step="ming_gong",
            rule_id=rule["id"],
            source=rule.get("source") or [],
            formula=rule.get("formula") or "",
            inputs={
                "lunar_month": lunar_month,
                "hour_index": hour_index,
                "year_stem": year_stem,
            },
            result=branch,
        )
    return result
