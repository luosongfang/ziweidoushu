"""身宫规则执行。"""

from __future__ import annotations

from typing import Any

from app.ziwei.constants import EARTHLY_BRANCHES, YIN_BRANCH_INDEX
from app.ziwei_classical.rules.loader import assert_has_source, get_shen_rule
from app.ziwei_classical.validator.classical_trace import ClassicalTrace


def apply_shen_gong_rule(
    lunar_month: int,
    hour_index: int,
    trace: ClassicalTrace | None = None,
) -> dict[str, Any]:
    rule = get_shen_rule()
    assert_has_source(rule)
    month_idx = (YIN_BRANCH_INDEX + lunar_month - 1) % 12
    shen_idx = (month_idx + hour_index) % 12
    branch = EARTHLY_BRANCHES[shen_idx]
    result = {
        "branch": branch,
        "branch_index": shen_idx,
        "month_branch": EARTHLY_BRANCHES[month_idx],
        "rule_id": rule["id"],
    }
    if trace is not None:
        trace.add(
            step="shen_gong",
            rule_id=rule["id"],
            source=rule.get("source") or [],
            formula=rule.get("formula") or "",
            inputs={"lunar_month": lunar_month, "hour_index": hour_index},
            result=branch,
        )
    return result
