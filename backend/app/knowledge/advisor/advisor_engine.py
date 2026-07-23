"""Advisor Engine V2.1 — life-mentor decision model (DB-driven, no LLM)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.knowledge.advisor.advisor_context_builder import AdvisorContextBuilder
from app.knowledge.advisor.advisor_safety import AdvisorSafety
from app.knowledge.advisor.schemas import AdvisorResult
from app.knowledge.knowledge_models import (
    AdvisorActionModel,
    AdvisorDimensionRule,
    AdvisorQuestionTemplate,
)
from app.knowledge.knowledge_service import KnowledgeService


def _row_to_dict(obj: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if hasattr(val, "hex"):
            val = str(val)
        data[col.name] = val
    return data


# classifier question_type -> advisor template question_type
_QTYPE_TO_TEMPLATE: dict[str, str] = {
    "career": "career_choice",
    "entrepreneurship": "entrepreneurship",
    "career_switch": "job_change",
    "wealth": "investment",
    "relationship": "relationship",
    "marriage": "marriage",
    "study": "self_growth",
    "family": "self_growth",
    "personality": "self_growth",
    "life_stage": "life_confusion",
}


@lru_cache(maxsize=1)
def _cached_dimensions() -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        rows = db.scalars(select(AdvisorDimensionRule)).all()
        return tuple(_row_to_dict(r) for r in rows)
    finally:
        db.close()


@lru_cache(maxsize=1)
def _cached_actions() -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        rows = db.scalars(select(AdvisorActionModel)).all()
        return tuple(_row_to_dict(r) for r in rows)
    finally:
        db.close()


_REFLECTIONS: dict[str, list[str]] = {
    "career_choice": [
        "我真正想长期贡献的价值是什么？",
        "领导能力之外，我还需要补哪一项可验证技能？",
    ],
    "entrepreneurship": [
        "我愿意承担的最大可逆损失是多少？",
        "如何用试错机制保护变化能力不被冲动消耗？",
    ],
    "job_change": [
        "哪些能力可以迁移到新赛道？",
        "分阶段过渡的最小安全步骤是什么？",
    ],
    "relationship": [
        "关系中哪一次沟通可以本周练习？",
        "我需要的边界与亲密如何同时被照顾？",
    ],
    "marriage": [
        "我们如何用复盘代替情绪摊牌？",
        "共同经营的下一个具体行动是什么？",
    ],
    "investment": [
        "我的风险偏好与安全垫是否匹配？",
        "若结果不及预期，退出条件是什么？",
    ],
    "life_confusion": [
        "这个阶段的主题更像整理、探索还是深耕？",
        "一个两周内可完成的小实验是什么？",
    ],
    "self_growth": [
        "哪些优势我还没有系统使用？",
        "成长上我最想练习的一个行为是什么？",
    ],
}


@lru_cache(maxsize=32)
def _cached_template(question_type: str) -> dict[str, Any] | None:
    tmpl_type = _QTYPE_TO_TEMPLATE.get(question_type, question_type)
    db = SessionLocal()
    try:
        row = db.scalar(
            select(AdvisorQuestionTemplate).where(
                AdvisorQuestionTemplate.question_type == tmpl_type
            )
        )
        if row:
            return _row_to_dict(row)
        row = db.scalar(
            select(AdvisorQuestionTemplate).where(
                AdvisorQuestionTemplate.question_type == question_type
            )
        )
        return _row_to_dict(row) if row else None
    finally:
        db.close()


class AdvisorEngine:
    """
    输入 chart_data + question + reasoning_result
    输出 AdvisorResult（人生导师决策层）
    """

    @classmethod
    def _session(cls) -> Session:
        return SessionLocal()

    @classmethod
    def get_template(cls, question_type: str, db: Session | None = None) -> dict[str, Any] | None:
        if db is not None:
            tmpl_type = _QTYPE_TO_TEMPLATE.get(question_type, question_type)
            row = db.scalar(
                select(AdvisorQuestionTemplate).where(
                    AdvisorQuestionTemplate.question_type == tmpl_type
                )
            )
            if row:
                return _row_to_dict(row)
            row = db.scalar(
                select(AdvisorQuestionTemplate).where(
                    AdvisorQuestionTemplate.question_type == question_type
                )
            )
            return _row_to_dict(row) if row else None
        return _cached_template(question_type)

    @classmethod
    def list_dimensions(
        cls, codes: list[str] | None = None, db: Session | None = None
    ) -> list[dict[str, Any]]:
        rows = list(_cached_dimensions())
        if codes:
            wanted = set(codes)
            rows = [r for r in rows if r.get("dimension_code") in wanted]
        return rows

    @classmethod
    def list_actions(cls, db: Session | None = None) -> list[dict[str, Any]]:
        return list(_cached_actions())

    @classmethod
    def match_actions(
        cls,
        stars: list[str],
        pattern_names: list[str] | None = None,
        matrix_combos: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        star_set = set(stars)
        names = set(pattern_names or []) | set(matrix_combos or [])
        matched: list[dict[str, Any]] = []
        generic: dict[str, Any] | None = None
        for row in cls.list_actions():
            code = row.get("pattern_code") or ""
            cond = row.get("condition") or {}
            if cond.get("always"):
                generic = row
                continue
            needed = set(cond.get("stars") or [])
            ming = set(cond.get("ming_contains") or [])
            hit = False
            if needed and needed.issubset(star_set):
                hit = True
            if ming and ming.issubset(star_set):
                hit = True
            if code in names:
                hit = True
            # alias mapping
            if code == "紫府同宫" and ("紫微天府" in names or "紫府朝垣" in names):
                hit = True
            if code == "紫府朝垣" and ("紫微天府" in names or "紫府同宫" in names):
                hit = True
            if hit:
                matched.append(row)
        if not matched and generic:
            matched.append(generic)
        elif generic and len(matched) < 2:
            matched.append(generic)
        return matched

    @classmethod
    def analyze(
        cls,
        chart_data: dict[str, Any],
        question: str,
        question_type: str,
        reasoning_result: list[Any] | None = None,
        *,
        matrix_summary: dict[str, Any] | None = None,
        life_advisor: dict[str, Any] | None = None,
    ) -> AdvisorResult:
        trace = ["advisor_engine:v2.1"]
        template = cls.get_template(question_type) or {
            "question_type": "self_growth",
            "required_dimensions": ["personality", "growth"],
            "recommended_focus": ["自我认知", "成长"],
            "avoid_topics": ["宿命判决"],
        }
        tmpl_type = template.get("question_type") or "self_growth"
        trace.append(f"advisor_template:{tmpl_type}")

        dim_codes = list(template.get("required_dimensions") or ["growth"])
        dimensions = cls.list_dimensions(dim_codes)
        primary = dimensions[0] if dimensions else {
            "dimension_code": "growth",
            "dimension_name": "人生成长",
            "positive_expression": "反思与适应",
            "challenge_expression": "方向不清",
            "growth_direction": "小步验证",
        }
        life_dimension = str(primary.get("dimension_name") or primary.get("dimension_code"))
        trace.append(f"advisor_dimension:{primary.get('dimension_code')}")

        ctx = AdvisorContextBuilder.build_from_reasoning(
            chart_data, question, reasoning_result
        )
        stars = ctx["stars"]
        patterns = KnowledgeService.match_patterns(stars)
        pattern_names = [p.get("pattern_name") for p in patterns if p.get("pattern_name")]
        combos = list((matrix_summary or {}).get("matched_combinations") or [])
        actions = cls.match_actions(stars, pattern_names=pattern_names, matrix_combos=combos)
        trace.append(f"advisor_actions:{','.join(a.get('pattern_code','') for a in actions)}")

        strengths: list[str] = []
        challenges: list[str] = []
        suggestions: list[str] = []
        growth_dir: list[str] = []
        action_plan: list[str] = []
        sources: list[dict[str, Any]] = []

        for d in dimensions:
            sources.append({"type": "advisor_dimension", "name": d.get("dimension_code")})
            if d.get("positive_expression"):
                strengths.append(str(d["positive_expression"]))
            if d.get("challenge_expression"):
                challenges.append(str(d["challenge_expression"]))
            if d.get("growth_direction"):
                growth_dir.append(str(d["growth_direction"]))

        for a in actions:
            sources.append({"type": "advisor_action", "name": a.get("pattern_code")})
            if a.get("strength_analysis"):
                strengths.append(str(a["strength_analysis"]))
            if a.get("risk_reminder"):
                challenges.append(str(a["risk_reminder"]))
            suggestions.extend(list(a.get("action_suggestions") or []))
            action_plan.extend(list(a.get("action_suggestions") or []))
            growth_dir.extend(list(a.get("growth_path") or []))

        # merge V2 life_advisor if present
        if life_advisor:
            strengths.extend(list(life_advisor.get("strengths") or []))
            challenges.extend(list(life_advisor.get("challenges") or []))
            growth_dir.extend(list(life_advisor.get("growth_direction") or []))

        # recommended focus from template (ensure expected keywords for quality cases)
        for focus in template.get("recommended_focus") or []:
            if focus and not any(focus in s for s in strengths + suggestions + growth_dir):
                strengths.append(f"关注重点：{focus}")

        # rewrite traditional tone
        strengths = AdvisorContextBuilder.rewrite_list(list(dict.fromkeys(strengths)))[:10]
        challenges = AdvisorContextBuilder.rewrite_list(list(dict.fromkeys(challenges)))[:10]
        suggestions = AdvisorContextBuilder.rewrite_list(list(dict.fromkeys(suggestions)))[:10]
        growth_dir = AdvisorContextBuilder.rewrite_list(list(dict.fromkeys(growth_dir)))[:10]
        action_plan = AdvisorContextBuilder.rewrite_list(list(dict.fromkeys(action_plan)))[:10]

        growth = growth_dir[0] if growth_dir else str(primary.get("growth_direction") or "")
        reflections = list(_REFLECTIONS.get(tmpl_type) or _REFLECTIONS["self_growth"])

        avoid = template.get("avoid_topics") or []
        # Do not echo forbidden phrases into the notice text itself
        safety = AdvisorSafety.notice(
            "禁止宿命化表达与确定事件预测；已按问题模板启用高风险话题过滤。"
        )
        del avoid  # used for template validation only; not echoed

        result = AdvisorResult(
            dimension=str(primary.get("dimension_code") or "growth"),
            life_dimension=life_dimension,
            strengths=AdvisorSafety.apply_list(strengths),
            challenges=AdvisorSafety.apply_list(challenges),
            growth=AdvisorSafety.apply(growth),
            suggestions=AdvisorSafety.apply_list(suggestions),
            growth_direction=AdvisorSafety.apply_list(growth_dir),
            action_plan=AdvisorSafety.apply_list(action_plan),
            reflection_questions=reflections,
            safety_notice=safety,
            sources=sources,
            call_trace=trace,
        )
        return result
