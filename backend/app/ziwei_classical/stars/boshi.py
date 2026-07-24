"""博士十二神 — 框架（未接入 AI）。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace

RULE_SOURCE = "博士十二神：以禄存起博士，阳顺阴逆"
STARS = ("博士", "力士", "青龙", "小耗", "将军", "奏书", "飞廉", "喜神", "病符", "大耗", "伏兵", "官府")


def place_boshi(
    lu_cun_branch: str,
    *,
    yin: bool = False,
    trace: RuleTrace | None = None,
) -> dict:
    from app.ziwei.constants import EARTHLY_BRANCHES

    formula = "禄存起博士；阳男顺行，阴男逆行（女盘另议）"
    out = {
        "rule_source": RULE_SOURCE,
        "formula": formula,
        "stars": {},
        "enabled_framework": True,
        "lu_cun_branch": lu_cun_branch,
    }
    if lu_cun_branch in EARTHLY_BRANCHES:
        si = EARTHLY_BRANCHES.index(lu_cun_branch)
        for i, name in enumerate(STARS):
            idx = (si - i) % 12 if yin else (si + i) % 12
            out["stars"][name] = EARTHLY_BRANCHES[idx]
    if trace is not None:
        trace.add(
            step="boshi",
            rule=RULE_SOURCE,
            inputs={"lu_cun_branch": lu_cun_branch, "yin": yin},
            outputs=out,
            source="ziwei_classical.stars.boshi",
        )
    return out
