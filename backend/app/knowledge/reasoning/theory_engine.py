"""Theory Engine V2 — read ziwei_theory_rules for traditional basis."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.knowledge.knowledge_models import ZiweiTheoryRule
from app.knowledge.reasoning.schemas import ReasoningResult


def _row_to_dict(obj: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if hasattr(val, "hex"):
            val = str(val)
        data[col.name] = val
    return data


class TheoryEngine:
    """读取传统理论规则，输出传统理论依据。"""

    SCOPE_BY_QTYPE: dict[str, str] = {
        "career": "career",
        "entrepreneurship": "career",
        "career_switch": "career",
        "wealth": "wealth",
        "relationship": "relationship",
        "marriage": "relationship",
        "study": "growth",
        "family": "relationship",
        "personality": "growth",
        "life_stage": "growth",
    }

    @classmethod
    def list_rules(
        cls,
        scope: str | None = None,
        categories: list[str] | None = None,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        own = db is None
        db = db or SessionLocal()
        try:
            rows = db.scalars(select(ZiweiTheoryRule)).all()
            out = [_row_to_dict(r) for r in rows]
            if scope:
                out = [r for r in out if scope in (r.get("application_scope") or [])]
            if categories:
                cats = set(categories)
                out = [r for r in out if r.get("category") in cats]
            return out
        finally:
            if own:
                db.close()

    @classmethod
    def match_for_question(
        cls,
        question_type: str,
        pattern_names: list[str] | None = None,
    ) -> ReasoningResult:
        scope = cls.SCOPE_BY_QTYPE.get(question_type, "growth")
        rules = cls.list_rules(scope=scope)
        # always include 三方四正 / 四化 / 格局 related
        extra = cls.list_rules(
            categories=["三方四正", "四化理论", "格局理论", "星曜组合", "命宫理论"]
        )
        by_name = {r["rule_name"]: r for r in rules + extra}
        # boost matched pattern rules
        for pname in pattern_names or []:
            for r in extra:
                if pname in (r.get("rule_name") or "") or pname in (
                    r.get("traditional_meaning") or ""
                ):
                    by_name[r["rule_name"]] = r

        selected = list(by_name.values())[:12]
        trad = []
        modern = []
        risks = []
        sources = []
        for r in selected:
            sources.append(
                {"type": "theory_rule", "name": r.get("rule_name"), "category": r.get("category")}
            )
            if r.get("traditional_meaning"):
                trad.append(f"{r['rule_name']}：{r['traditional_meaning']}")
            if r.get("modern_interpretation"):
                modern.append(str(r["modern_interpretation"]))
            if r.get("risk_expression"):
                risks.append(str(r["risk_expression"]))

        return ReasoningResult(
            dimension=f"theory:{scope}",
            observations=modern[:6],
            traditional_basis=trad,
            strengths=[],
            challenges=risks[:4],
            suggestions=[],
            sources=sources,
            call_trace=[f"theory_engine:scope={scope}", f"theory_rules:{len(selected)}"],
        )

    @classmethod
    def classical_evidence_preview(
        cls,
        *,
        stars: list[str] | None = None,
        palaces: list[str] | None = None,
        patterns: list[str] | None = None,
        limit: int = 8,
    ) -> dict[str, Any]:
        """
        V6.0 Phase 1 optional read from Classical Evidence Layer.
        Does not alter match_for_question / V5.6 dispatch.
        """
        from app.knowledge.classical import EvidenceService

        return EvidenceService.evidence_for_entities(
            stars=stars,
            palaces=palaces,
            patterns=patterns,
            limit=limit,
        )
