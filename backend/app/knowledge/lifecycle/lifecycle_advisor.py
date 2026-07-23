"""Lifecycle advisor — growth advice with safe life-planning language (no LLM)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.intelligence.interpretation_layer import InterpretationLayer

_FALLBACK_TEMPLATES: dict[str, dict[str, str]] = {
    "career": {
        "strength_template": "当前阶段在事业维度具备可扩展的能力结构，适合把优势产品化。",
        "risk_template": "需关注节奏过快带来的资源透支，建议保留安全垫与复盘机制。",
        "growth_template": "用季度里程碑验证方向，把大限主题落实为可执行的能力投资。",
    },
    "entrepreneurship": {
        "strength_template": "创业相关阶段强调资源整合与执行闭环，适合小范围试点。",
        "risk_template": "传统周期视角提示关注现金流与风险管理，避免一次性押注。",
        "growth_template": "把十年大限主题拆成两年能力建设与一年市场验证。",
    },
    "wealth": {
        "strength_template": "财富维度宜巩固既有配置能力，强调长期稳健。",
        "risk_template": "关注波动周期中的过度集中风险，保持流动性。",
        "growth_template": "以安全垫优先，再用可验证配置逐步优化结构。",
    },
    "relationship": {
        "strength_template": "关系阶段适合深化沟通质量与相互支持。",
        "risk_template": "注意边界不清带来的消耗，及时对齐期待。",
        "growth_template": "建立定期复盘对话，把关心变成可持续的互动习惯。",
    },
    "life_stage": {
        "strength_template": "人生周期视角帮助识别当前主题重心。",
        "risk_template": "避免把阶段主题误解为命运判决。",
        "growth_template": "按年龄与大限主题设定下一阶段学习与规划重点。",
    },
    "default": {
        "strength_template": "当前周期提供自我认知与规划参考框架。",
        "risk_template": "避免绝对化解读，保持行动弹性。",
        "growth_template": "把传统周期主题转成可验证的成长实验。",
    },
}

_SCENARIO = {
    "career": "career",
    "entrepreneurship": "entrepreneurship",
    "career_switch": "career",
    "wealth": "wealth",
    "relationship": "relationship",
    "marriage": "relationship",
    "life_stage": "life_stage",
}


class LifecycleAdvisor:
    """Compose life_timeline + growth advice using cycle templates."""

    @classmethod
    @lru_cache(maxsize=16)
    def _template(cls, scenario: str) -> dict[str, str]:
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT scenario, strength_template, risk_template, growth_template
                    FROM public.cycle_analysis_templates
                    WHERE scenario = :s
                    LIMIT 1
                    """
                ),
                {"s": scenario},
            ).mappings().first()
            if row:
                return {
                    "strength_template": row["strength_template"] or "",
                    "risk_template": row["risk_template"] or "",
                    "growth_template": row["growth_template"] or "",
                }
        except Exception:
            pass
        finally:
            db.close()
        return dict(_FALLBACK_TEMPLATES.get(scenario) or _FALLBACK_TEMPLATES["default"])

    @classmethod
    def refresh(cls) -> None:
        cls._template.cache_clear()

    @classmethod
    def advise(
        cls,
        *,
        question_type: str,
        stage: dict[str, Any],
        major_limit: dict[str, Any] | None,
        annual: dict[str, Any] | None = None,
        timeline: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        scenario = _SCENARIO.get(question_type, "default")
        tmpl = cls._template(scenario)
        palace = (major_limit or {}).get("palace") or "相关宫位"
        age_range = (major_limit or {}).get("age_range") or stage.get("age_range") or ""
        focus = list(stage.get("focus") or [])

        traditional_view = InterpretationLayer.apply(
            (
                f"传统大限规则显示当前参考宫位为{palace}"
                + (f"（{age_range}）" if age_range else "")
                + f"。人生阶段模型对应{stage.get('stage_name')}。"
                " 以上仅描述阶段性主题重心，供传统文化学习与人生规划参考，"
                "不作绝对事件预测。"
            )
        )
        if annual and annual.get("summary"):
            traditional_view = InterpretationLayer.apply(
                traditional_view + " " + str(annual["summary"])
            )

        growth_advice = InterpretationLayer.apply(
            " ".join(
                [
                    stage.get("advisor_template") or "",
                    tmpl.get("growth_template") or "",
                    (annual or {}).get("growth_advice") or "",
                ]
            ).strip()
        )
        strength = InterpretationLayer.apply(tmpl.get("strength_template") or "")
        risk = InterpretationLayer.apply(tmpl.get("risk_template") or "")

        # Forbid absolute prediction vocabulary leftovers
        banned = ("必有", "注定", "必然发生", "一定会", "大难", "横死")
        for b in banned:
            if b in growth_advice:
                growth_advice = growth_advice.replace(b, "")
            if b in traditional_view:
                traditional_view = traditional_view.replace(b, "")

        life_timeline = {
            "current_stage": stage.get("stage_name") or "career_expand",
            "age_range": stage.get("age_range") or age_range or "",
            "focus": focus,
            "traditional_view": traditional_view,
            "growth_advice": growth_advice,
            "major_limit_palace": palace,
            "major_limit_range": (major_limit or {}).get("age_range"),
            "strength": strength,
            "risk": risk,
            "annual": {
                "year": (annual or {}).get("year"),
                "ganzhi": (annual or {}).get("ganzhi"),
                "summary": (annual or {}).get("summary"),
            }
            if annual
            else None,
        }
        sources: list[dict[str, Any]] = []
        if stage.get("source"):
            sources.append(stage["source"])
        if major_limit and major_limit.get("source"):
            sources.append(major_limit["source"])
        if annual:
            sources.extend(list(annual.get("sources") or [])[:3])
        if timeline:
            for s in timeline.get("sources") or []:
                if isinstance(s, dict) and s not in sources:
                    sources.append(s)
        life_timeline["sources"] = sources

        return {
            "life_timeline": life_timeline,
            "strength": strength,
            "risk": risk,
            "growth_advice": growth_advice,
            "traditional_view": traditional_view,
            "scenario": scenario,
            "call_trace": [
                f"lifecycle_advisor:scenario={scenario}",
                f"lifecycle_advisor:stage={stage.get('stage_name')}",
                f"lifecycle_advisor:palace={palace}",
            ],
        }
