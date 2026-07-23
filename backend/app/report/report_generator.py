"""Report generator — 调用 Knowledge Core V5.6 pipeline，输出人生档案模板。"""

from __future__ import annotations

from typing import Any

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.ai.safety_filter import SafetyFilter
from app.report.templates.life_profile_template import empty_life_profile

ENGINE_VERSION = "5.6"

_REPORT_QUESTIONS = {
    "life_profile": "请从传统文化视角生成完整人生成长档案，涵盖自我认知、事业、财富、关系与人生阶段。",
    "six_dimension": "请从六维人生模块（自我认知、事业、财富、关系、人生阶段、行动建议）给出结构化成长分析。",
    "stage_growth": "请重点分析当前人生阶段特点、关注焦点与可执行成长建议。",
}


def _safe(text: str) -> str:
    return SafetyFilter.apply(text or "")


def _safe_list(items: list | None, limit: int = 6) -> list[str]:
    out: list[str] = []
    for item in list(items or [])[:limit]:
        s = _safe(str(item))
        if s.strip():
            out.append(s)
    return out


def _apply_safety_to_report(report: dict[str, Any]) -> dict[str, Any]:
    """递归 Safety Filter。"""
    if isinstance(report, dict):
        return {k: _apply_safety_to_report(v) for k, v in report.items()}
    if isinstance(report, list):
        return [_apply_safety_to_report(v) for v in report]
    if isinstance(report, str):
        return _safe(report)
    return report


def _populate_from_pipeline(result: Any, chart_data: dict[str, Any]) -> dict[str, Any]:
    report = empty_life_profile()
    decision = getattr(result, "decision_analysis", None) or {}
    life_timeline = getattr(result, "life_timeline", None) or {}
    traditional = getattr(result, "traditional_analysis", None) or []
    if isinstance(traditional, str):
        traditional = [traditional]
    suggestions = list(getattr(result, "suggestions", None) or [])
    advisor = getattr(result, "advisor_analysis", None) or {}

    ming = chart_data.get("chart", {}).get("ming_gong") if isinstance(chart_data.get("chart"), dict) else None
    ming = ming or chart_data.get("ming_gong") or "命宫"
    five = chart_data.get("chart", {}).get("five_element") if isinstance(chart_data.get("chart"), dict) else None
    five = five or chart_data.get("five_element") or ""

    report["identity"]["chart_summary"] = _safe(
        f"命宫在{ming}，五行{five}。本报告基于 Knowledge Core V5.6 多理论引擎生成，供自我探索参考。"
    )
    report["identity"]["traditional_basis"] = _safe("；".join(list(traditional)[:3]))
    report["identity"]["modern_interpretation"] = _safe(
        str(decision.get("current_state") or (suggestions[0] if suggestions else ""))
    )

    report["personality"]["strengths"] = _safe_list(
        list(decision.get("strengths") or []) + list(advisor.get("strengths") or [])
    )
    report["personality"]["challenges"] = _safe_list(
        list(decision.get("challenges") or []) + list(advisor.get("challenges") or [])
    )
    report["personality"]["growth_direction"] = _safe_list(
        list(advisor.get("growth_direction") or []) + suggestions[:3]
    )

    trad_view = decision.get("traditional_view")
    if isinstance(trad_view, dict):
        report["career"]["traditional_view"] = _safe("；".join(str(v) for v in trad_view.values() if v)[:400])
    else:
        report["career"]["traditional_view"] = _safe(str(trad_view or traditional[0] if traditional else ""))
    report["career"]["advantages"] = _safe_list(list(decision.get("strengths") or [])[:4])
    report["career"]["development_advice"] = _safe_list(
        list(decision.get("action_suggestions") or [])[:4]
    )

    report["wealth"]["resource_pattern"] = _safe(
        str(decision.get("scenario") or "资源结构需结合个人节奏与阶段规划。")
    )
    report["wealth"]["risk_awareness"] = _safe(
        "；".join(list(decision.get("challenges") or [])[:2]) or "注意节奏与风险边界，避免过度激进。"
    )
    report["wealth"]["growth_advice"] = _safe(
        suggestions[1] if len(suggestions) > 1 else (suggestions[0] if suggestions else "")
    )

    report["relationship"]["interaction_style"] = _safe(
        str(decision.get("current_state") or "重视沟通边界与情绪节奏。")
    )
    report["relationship"]["growth_advice"] = _safe(
        suggestions[2] if len(suggestions) > 2 else (suggestions[0] if suggestions else "")
    )

    report["life_cycle"]["current_stage"] = _safe(str(life_timeline.get("current_stage") or "当前阶段"))
    report["life_cycle"]["focus"] = _safe(str(life_timeline.get("age_range") or life_timeline.get("focus") or ""))
    report["life_cycle"]["advice"] = _safe(str(life_timeline.get("growth_advice") or ""))

    continuity = getattr(result, "reflection_questions", None) or []
    advisor_msg = _safe(
        str(getattr(result, "safety_notice", "") or "")
        + " "
        + (continuity[0] if continuity else "")
        + " "
        + str(advisor.get("life_dimension") or "")
    ).strip()
    report["advisor_message"] = advisor_msg or _safe(
        "欢迎继续探索：传统文化视角帮助理解自己，辅助做出更清醒的选择，而非预测未来。"
    )

    return _apply_safety_to_report(report)


class ReportGenerator:
    @classmethod
    def generate(
        cls,
        *,
        chart_data: dict[str, Any],
        report_type: str = "life_profile",
        user_id: str | None = None,
    ) -> dict[str, Any]:
        question = _REPORT_QUESTIONS.get(report_type, _REPORT_QUESTIONS["life_profile"])
        result = ReasoningEngineV2.run(
            question=question,
            chart_data=chart_data,
            user_id=user_id,
            persist_memory=False,
            persist_growth_memory=False,
        )
        sections = _populate_from_pipeline(result, chart_data)
        summary_parts = [
            sections["identity"]["modern_interpretation"],
            sections["life_cycle"]["advice"],
        ]
        summary = _safe(" ".join(p for p in summary_parts if p)[:500])
        knowledge_trace = getattr(result, "knowledge_trace", None) or {}
        safety = _safe(str(getattr(result, "safety_notice", "") or ""))
        if not safety:
            safety = "本报告仅供传统文化学习、自我认知辅助与人生规划参考，不作绝对预测。"
        return {
            "engine_version": ENGINE_VERSION,
            "summary": summary,
            "report_sections": sections,
            "knowledge_trace": knowledge_trace if isinstance(knowledge_trace, dict) else {},
            "safety_notice": safety,
        }
