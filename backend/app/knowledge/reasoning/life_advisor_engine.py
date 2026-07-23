"""Life Advisor Engine V2 — convert Ziwei analysis into life guidance."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.safety_filter import SafetyFilter
from app.database.database import SessionLocal
from app.knowledge.knowledge_models import LifeScenarioModel
from app.knowledge.reasoning.schemas import LifeAdvisorResult, ReasoningResult


def _row_to_dict(obj: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if hasattr(val, "hex"):
            val = str(val)
        data[col.name] = val
    return data


QUESTION_TYPE_TO_SCENARIO: dict[str, str] = {
    "career": "career_choice",
    "entrepreneurship": "entrepreneurship",
    "career_switch": "life_transition",
    "wealth": "wealth_planning",
    "relationship": "marriage_relationship",
    "marriage": "marriage_relationship",
    "study": "learning_growth",
    "family": "family_relation",
    "personality": "personal_strength",
    "life_stage": "life_transition",
}

_REFLECTION: dict[str, list[str]] = {
    "career": [
        "我真正想贡献的价值是什么？",
        "下一阶段哪个能力最值得验证？",
    ],
    "entrepreneurship": [
        "我愿意承担的最大可逆损失是多少？",
        "最小可行验证需要多久？",
    ],
    "wealth": [
        "我的风险偏好与现金流安全垫是否匹配？",
        "收入增长靠技能、资产还是机会？",
    ],
    "relationship": [
        "我在关系中最需要的安全感是什么？",
        "哪一个沟通习惯可以本周开始练习？",
    ],
    "marriage": [
        "我们如何建立每周复盘而不是情绪摊牌？",
        "边界与亲密如何同时被照顾？",
    ],
    "personality": [
        "哪些优势我还没有系统使用？",
        "压力来临时我的默认反应是什么？",
    ],
    "life_stage": [
        "这个阶段的主题是扩张、整理还是休整？",
        "我需要准备什么才能更从容？",
    ],
}


@lru_cache(maxsize=32)
def _cached_life_scenario(scenario_name: str) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        row = db.scalar(
            select(LifeScenarioModel).where(LifeScenarioModel.scenario_name == scenario_name)
        )
        return _row_to_dict(row) if row else None
    finally:
        db.close()


class LifeAdvisorEngine:
    """把紫微分析转换为人生建议（非宿命判决）。"""

    @classmethod
    def get_scenario(cls, scenario_name: str, db: Session | None = None) -> dict[str, Any] | None:
        if db is not None:
            row = db.scalar(
                select(LifeScenarioModel).where(LifeScenarioModel.scenario_name == scenario_name)
            )
            return _row_to_dict(row) if row else None
        return _cached_life_scenario(scenario_name)

    @classmethod
    def resolve_scenario(cls, question_type: str) -> dict[str, Any]:
        name = QUESTION_TYPE_TO_SCENARIO.get(question_type, "personal_strength")
        scenario = cls.get_scenario(name) or {
            "scenario_name": name,
            "display_name": question_type,
            "required_palaces": ["命宫"],
            "required_patterns": [],
            "analysis_steps": [],
            "safety_rules": ["本分析仅供自我认知参考"],
            "related_question_types": [question_type],
        }
        return scenario

    @classmethod
    def build(
        cls,
        question_type: str,
        theory: ReasoningResult,
        matrix: ReasoningResult,
        v1_parts: list[ReasoningResult] | None = None,
    ) -> LifeAdvisorResult:
        scenario = cls.resolve_scenario(question_type)
        trace = [
            f"life_scenario:{scenario.get('scenario_name')}",
            *(scenario.get("analysis_steps") or [])[:5],
        ]

        traditional = list(
            dict.fromkeys(theory.traditional_basis + matrix.traditional_basis)
        )[:8]
        modern_bits = list(
            dict.fromkeys(theory.observations + matrix.observations)
        )[:6]
        strengths = list(dict.fromkeys(matrix.strengths + theory.strengths))[:8]
        challenges = list(dict.fromkeys(matrix.challenges + theory.challenges))[:8]
        growth = list(dict.fromkeys(matrix.suggestions))[:8]

        if v1_parts:
            for r in v1_parts:
                strengths = list(dict.fromkeys(strengths + r.strengths))[:8]
                challenges = list(dict.fromkeys(challenges + r.challenges))[:8]
                growth = list(dict.fromkeys(growth + r.suggestions))[:8]
                traditional = list(dict.fromkeys(traditional + r.traditional_basis))[:8]

        if question_type == "entrepreneurship":
            growth = list(
                dict.fromkeys(
                    [
                        "若推进创业，先做小范围需求验证再放大投入。",
                        "同步建立止损线与个人能量补给计划。",
                        *growth,
                    ]
                )
            )[:8]

        reflections = _REFLECTION.get(question_type) or _REFLECTION["personality"]
        safety_bits = scenario.get("safety_rules") or []
        safety = "；".join(str(x) for x in safety_bits) if safety_bits else (
            "本分析基于传统文化理论，仅作为自我认知和人生规划参考，不代表确定预测。"
        )
        safety = (
            safety
            + " 定位：传统文化视角下的人生分析与自我认知辅助工具。"
        )

        result = LifeAdvisorResult(
            traditional_view="；".join(traditional) if traditional else "依据三方四正与星曜组合互参。",
            modern_view="；".join(modern_bits) if modern_bits else "聚焦可验证的自我认知与行动设计。",
            strengths=strengths,
            challenges=challenges,
            growth_direction=growth,
            reflection_questions=reflections,
            safety_notice=SafetyFilter.apply(safety),
            sources=theory.sources + matrix.sources
            + [{"type": "life_scenario", "name": scenario.get("scenario_name")}],
            call_trace=trace,
        )
        # apply safety on all text fields
        result.traditional_view = SafetyFilter.apply(result.traditional_view)
        result.modern_view = SafetyFilter.apply(result.modern_view)
        result.strengths = [SafetyFilter.apply(x) for x in result.strengths]
        result.challenges = [SafetyFilter.apply(x) for x in result.challenges]
        result.growth_direction = [SafetyFilter.apply(x) for x in result.growth_direction]
        return result
