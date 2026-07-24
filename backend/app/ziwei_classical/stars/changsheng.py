"""长生十二神 — 框架（未接入 AI）。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace

RULE_SOURCE = "长生十二神：按五行局安长生，阳顺阴逆"
STARS = ("长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养")

# 局数 → 长生起点（阳男常用表骨架）
CHANGSHENG_START = {2: "申", 3: "亥", 4: "巳", 5: "申", 6: "寅"}


def place_changsheng(
    bureau_number: int,
    *,
    yin: bool = False,
    trace: RuleTrace | None = None,
) -> dict:
    from app.ziwei.constants import EARTHLY_BRANCHES

    start = CHANGSHENG_START.get(bureau_number, "")
    formula = "依五行局取长生位；阳顺阴逆排布"
    out = {
        "rule_source": RULE_SOURCE,
        "formula": formula,
        "stars": {},
        "enabled_framework": True,
        "bureau_number": bureau_number,
        "yin": yin,
    }
    if start:
        si = EARTHLY_BRANCHES.index(start)
        for i, name in enumerate(STARS):
            idx = (si - i) % 12 if yin else (si + i) % 12
            out["stars"][name] = EARTHLY_BRANCHES[idx]
    if trace is not None:
        trace.add(
            step="changsheng",
            rule=RULE_SOURCE,
            inputs={"bureau_number": bureau_number, "yin": yin},
            outputs=out,
            source="ziwei_classical.stars.changsheng",
        )
    return out
