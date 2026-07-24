"""岁前十二神 — 框架（未接入 AI）。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace

RULE_SOURCE = "传统岁前十二神：以年支起岁建顺行"
STARS = ("岁建", "晦气", "丧门", "贯索", "官符", "小耗", "大耗", "龙德", "白虎", "天德", "吊客", "病符")

# 年支 → 岁建地支（子年岁建在寅…简化表待专业校验）
SUI_JIAN_FROM_YEAR = {
    "子": "寅", "丑": "卯", "寅": "辰", "卯": "巳", "辰": "午", "巳": "未",
    "午": "申", "未": "酉", "申": "戌", "酉": "亥", "戌": "子", "亥": "丑",
}


def place_sui_qian(year_branch: str, trace: RuleTrace | None = None) -> dict:
    from app.ziwei.constants import EARTHLY_BRANCHES

    start = SUI_JIAN_FROM_YEAR.get(year_branch, "")
    formula = "自年支定岁建，顺布十二神"
    out = {"rule_source": RULE_SOURCE, "formula": formula, "stars": {}, "enabled_framework": True}
    if start:
        si = EARTHLY_BRANCHES.index(start)
        for i, name in enumerate(STARS):
            out["stars"][name] = EARTHLY_BRANCHES[(si + i) % 12]
    if trace is not None:
        trace.add(
            step="sui_qian",
            rule=RULE_SOURCE,
            inputs={"year_branch": year_branch},
            outputs=out,
            source="ziwei_classical.stars.sui_qian",
        )
    return out
