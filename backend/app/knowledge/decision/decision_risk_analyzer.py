"""Decision risk analyzer — convert dangerous absolute claims to planning language."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.decision.decision_models import SAFETY_RULES
from app.knowledge.intelligence.interpretation_layer import InterpretationLayer


class DecisionRiskAnalyzer:
    """Risk assessment + expression conversion (no fear, no fatalism)."""

    @classmethod
    @lru_cache(maxsize=1)
    def _rules(cls) -> tuple[dict[str, str], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT forbidden_expression, safe_expression, reason, risk_level
                    FROM public.decision_safety_rules
                    """
                )
            ).mappings().all()
            if rows:
                return tuple(dict(r) for r in rows)
        except Exception:
            pass
        finally:
            db.close()
        return tuple(SAFETY_RULES)

    @classmethod
    def refresh(cls) -> None:
        cls._rules.cache_clear()

    @classmethod
    def sanitize(cls, text_value: str) -> str:
        out = text_value or ""
        for rule in cls._rules():
            bad = rule.get("forbidden_expression") or ""
            good = rule.get("safe_expression") or ""
            if bad and bad in out:
                out = out.replace(bad, good)
        # also apply global interpretation layer
        out = InterpretationLayer.apply(out)
        # strip residual absolutist markers
        for token in ("必有灾难", "横死", "注定失败", "必死", "大难临头"):
            if token in out:
                out = out.replace(token, "需要更加关注风险管理")
        return out

    @classmethod
    def sanitize_list(cls, items: list[str]) -> list[str]:
        return [cls.sanitize(x) for x in items if x]

    @classmethod
    def assess(
        cls,
        *,
        scenario: dict[str, Any],
        dimension_hits: list[dict[str, Any]],
        theory_analysis: dict[str, Any] | None = None,
        life_timeline: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        challenges: list[str] = []
        risks: list[str] = []
        sources: list[dict[str, Any]] = []

        for hit in dimension_hits:
            if hit.get("challenge_expression"):
                challenges.append(cls.sanitize(str(hit["challenge_expression"])))
            sources.append(
                {
                    "type": "decision_dimension_rule",
                    "factor": hit.get("traditional_factor"),
                    "dimension": hit.get("dimension"),
                    "source_reference": hit.get("source_reference"),
                }
            )

        # wealth scenarios emphasize risk management language
        risk_dims = set(scenario.get("risk_dimensions") or [])
        if "wealth" in risk_dims:
            risks.append(
                cls.sanitize(
                    "财富相关决策宜提前关注安全垫、流动性与集中度风险，"
                    "传统提醒应转化为风险管理而非结果预测。"
                )
            )
        if "relationship" in risk_dims:
            risks.append(
                cls.sanitize(
                    "关系选择中的张力更适合用沟通、边界与期待对齐来处理，"
                    "避免把文化符号解读为必须如何结局。"
                )
            )
        if "career" in risk_dims:
            risks.append(
                cls.sanitize(
                    "事业路径变动期可能伴随节奏压力，建议保留退出机制与复盘节点。"
                )
            )

        if life_timeline and life_timeline.get("risk"):
            risks.append(cls.sanitize(str(life_timeline["risk"])))

        if theory_analysis:
            for key in ("sanhe", "four_transform", "classic_formula", "feixing"):
                block = theory_analysis.get(key) or {}
                for c in (block.get("challenges") or [])[:2]:
                    challenges.append(cls.sanitize(str(c)))

        challenges = list(dict.fromkeys(challenges))[:8]
        risks = list(dict.fromkeys(risks + challenges))[:8]

        return {
            "challenges": challenges,
            "risks": risks,
            "risk_level": scenario.get("safety_level") or "high",
            "sources": sources[:12],
            "notice": cls.sanitize(
                "以上为传统文化学习与人生规划辅助视角，不作绝对未来预测，不制造恐惧。"
            ),
        }
