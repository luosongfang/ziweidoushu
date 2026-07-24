"""大限 — V1.0 骨架（方向按阳男阴女）。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace


def calc_daxian(
    *,
    gender: str,
    year_branch: str,
    bureau_number: int,
    ming_branch: str,
    trace: RuleTrace | None = None,
) -> dict:
    # 简化：仅记录规则意图，详细表由 FortuneEngine 后续对齐
    yang = year_branch in "子寅辰午申戌"
    if gender == "male":
        direction = "forward" if yang else "backward"
    else:
        direction = "backward" if yang else "forward"
    out = {
        "direction": direction,
        "start_age": bureau_number,
        "ming_branch": ming_branch,
        "bureau_number": bureau_number,
        "note": "大限细表待与专业盘批量校验",
    }
    if trace is not None:
        trace.add(
            step="daxian",
            rule="阳男阴女顺行，阴男阳女逆行；起运=局数",
            inputs={"gender": gender, "year_branch": year_branch, "bureau": bureau_number},
            outputs=out,
            source="ziwei_classical.fortune.daxian",
        )
    return out
