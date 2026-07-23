"""Advisor safety layer V2.1 — destiny/disaster/medical/legal absolute language."""

from __future__ import annotations

from app.ai.safety_filter import SafetyFilter


# Local high-priority advisor rules (also seeded to DB as version 2.1.0)
_ADVISOR_RULES: list[tuple[str, str]] = [
    ("你今年一定破财", "传统理论认为该阶段需要更加关注风险管理。"),
    ("今年一定破财", "传统理论认为该阶段需要更加关注风险管理。"),
    ("你的婚姻必失败", "关系模式中可能存在需要沟通改善的地方。"),
    ("婚姻必失败", "关系模式中可能存在需要沟通改善的地方。"),
    ("会发生灾难", "不作为确定事件预测，仅作为传统文化角度的反思参考。"),
    ("必然成功", "结果取决于准备度、执行与环境反馈，建议分阶段验证。"),
    ("一定发财", "可能具备财富管理优势，需要结合现实行动与风险控制。"),
    ("离婚预测", "关系议题请聚焦沟通、边界与共同成长，不做确定性预测。"),
    ("必然离婚", "关系模式可能存在需要沟通调整的地方，建议以经营视角看待。"),
    ("疾病结果", "健康议题请咨询专业医疗机构，这里只提供生活与压力管理建议。"),
    ("法律必赢", "法律事务请咨询专业人士；此处仅提供自我认知与规划参考。"),
    ("财务确定", "财务结果存在不确定性，建议控制风险并咨询专业意见。"),
]


_DEFAULT_NOTICE = (
    "本输出定位为：传统文化学习 + 自我认知辅助 + 人生规划参考。"
    "不作为确定事件预测；不讨论寿元议题、突发不幸断言、医学结论，以及法律或投资的确定性结果。"
)


class AdvisorSafety:
    """Advisor-specific safety transform; composes with global SafetyFilter."""

    @classmethod
    def apply(cls, text: str) -> str:
        if not text:
            return text
        out = text
        for forbidden, safe in sorted(_ADVISOR_RULES, key=lambda x: len(x[0]), reverse=True):
            if forbidden in out:
                out = out.replace(forbidden, safe)
        return SafetyFilter.apply(out)

    @classmethod
    def apply_list(cls, items: list[str]) -> list[str]:
        return [cls.apply(x) for x in items if x]

    @classmethod
    def notice(cls, extra: str | None = None) -> str:
        # Do not run substring replacements on the meta notice itself
        # (otherwise words like 灾难/疾病 in the disclaimer get rewritten).
        base = _DEFAULT_NOTICE
        if extra:
            return f"{extra} {base}"
        return base

    @classmethod
    def contains_forbidden(cls, text: str, forbidden_list: list[str]) -> list[str]:
        hits = []
        for f in forbidden_list:
            if f and f in text:
                hits.append(f)
        return hits
