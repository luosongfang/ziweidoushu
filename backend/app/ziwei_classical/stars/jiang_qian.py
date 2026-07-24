"""将前十二神 — 框架（未接入 AI）。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace

RULE_SOURCE = "将前十二神：以年支三合将星起，顺布"
STARS = ("将星", "攀鞍", "岁驿", "息神", "华盖", "劫煞", "灾煞", "天煞", "指背", "咸池", "月煞", "亡神")

# 三合将星
JIANG_XING = {
    "寅": "午", "午": "午", "戌": "午",
    "申": "子", "子": "子", "辰": "子",
    "巳": "酉", "酉": "酉", "丑": "酉",
    "亥": "卯", "卯": "卯", "未": "卯",
}


def place_jiang_qian(year_branch: str, trace: RuleTrace | None = None) -> dict:
    from app.ziwei.constants import EARTHLY_BRANCHES

    start = JIANG_XING.get(year_branch, "")
    formula = "年支三合取将星，顺布十二神"
    out = {"rule_source": RULE_SOURCE, "formula": formula, "stars": {}, "enabled_framework": True}
    if start:
        si = EARTHLY_BRANCHES.index(start)
        for i, name in enumerate(STARS):
            out["stars"][name] = EARTHLY_BRANCHES[(si + i) % 12]
    if trace is not None:
        trace.add(
            step="jiang_qian",
            rule=RULE_SOURCE,
            inputs={"year_branch": year_branch},
            outputs=out,
            source="ziwei_classical.stars.jiang_qian",
        )
    return out
