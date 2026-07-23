"""Decision Engine V5.0 — core orchestration (no LLM)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.decision.decision_advisor import DecisionAdvisor
from app.knowledge.decision.decision_context_builder import DecisionContextBuilder
from app.knowledge.decision.decision_risk_analyzer import DecisionRiskAnalyzer
from app.knowledge.knowledge_service import KnowledgeService


class DecisionEngine:
    """
    Question → Scenario → Context(Theory+Cycle+Memory+Knowledge)
    → Dimension Analysis → Risk → Growth → Safety → Advisor Output
    """

    @classmethod
    def analyze(
        cls,
        *,
        question: str,
        chart_data: dict[str, Any],
        question_type: str | None = None,
        user_context: dict[str, Any] | None = None,
        theory_analysis: dict[str, Any] | None = None,
        life_timeline: dict[str, Any] | None = None,
        user_memory: dict[str, Any] | None = None,
        selected_knowledge: list[dict[str, Any]] | None = None,
        persist_history: bool = False,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        qtype = question_type or KnowledgeService.detect_question_type(question)
        patterns = KnowledgeService.match_patterns(
            KnowledgeService.extract_stars_from_chart(chart_data)
        )
        context = DecisionContextBuilder.build(
            question=question,
            question_type=qtype,
            chart=chart_data,
            theory_analysis=theory_analysis,
            life_timeline=life_timeline,
            user_memory=user_memory or user_context,
            selected_knowledge=selected_knowledge,
            patterns=patterns,
        )
        risk = DecisionRiskAnalyzer.assess(
            scenario=context["scenario"],
            dimension_hits=context["dimension_hits"],
            theory_analysis=theory_analysis,
            life_timeline=life_timeline,
        )
        decision_analysis = DecisionAdvisor.build(
            context=context, risk=risk, question=question
        )

        # final safety pass on all text fields
        decision_analysis = cls._finalize_safety(decision_analysis)

        history_id = None
        if persist_history and user_id:
            try:
                history_id = cls.save_history(
                    user_id=user_id,
                    question_type=qtype,
                    question=question,
                    decision_analysis=decision_analysis,
                )
            except Exception:
                history_id = None

        return {
            "decision_analysis": decision_analysis,
            "scenario": context.get("scenario"),
            "risk": risk,
            "dimension_hits": context.get("dimension_hits"),
            "decision_history_id": history_id,
            "stars": KnowledgeService.extract_stars_from_chart(chart_data),
            "call_trace": [
                "decision:engine:v5.0",
                f"decision:scenario={context['scenario'].get('scenario_name')}",
                f"decision:dimensions={len(context.get('dimension_hits') or [])}",
                f"decision:strengths={len(decision_analysis.get('strengths') or [])}",
            ],
        }

    @classmethod
    def _finalize_safety(cls, payload: dict[str, Any]) -> dict[str, Any]:
        out = dict(payload)
        for key in (
            "current_state",
            "safety_notice",
        ):
            if out.get(key):
                out[key] = DecisionRiskAnalyzer.sanitize(str(out[key]))
        for key in (
            "strengths",
            "challenges",
            "decision_points",
            "action_suggestions",
            "reflection_questions",
        ):
            if isinstance(out.get(key), list):
                out[key] = DecisionRiskAnalyzer.sanitize_list(
                    [str(x) for x in out[key]]
                )
        tv = out.get("traditional_view") or {}
        if isinstance(tv, dict):
            out["traditional_view"] = {
                k: DecisionRiskAnalyzer.sanitize(str(v)) for k, v in tv.items()
            }
        return out

    @classmethod
    def save_history(
        cls,
        *,
        user_id: str,
        question_type: str,
        question: str,
        decision_analysis: dict[str, Any],
    ) -> str | None:
        uid = None
        try:
            uid = str(uuid.UUID(str(user_id)))
        except Exception:
            uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ziwei.user:{user_id}"))

        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    INSERT INTO public.decision_history
                        (user_id, question_type, question_summary, analysis_summary, suggestions)
                    VALUES
                        (CAST(:uid AS uuid), :qtype, :qsum, :asum, CAST(:sug AS jsonb))
                    RETURNING id::text
                    """
                ),
                {
                    "uid": uid,
                    "qtype": question_type,
                    "qsum": (question or "")[:200],
                    "asum": (decision_analysis.get("current_state") or "")[:500],
                    "sug": json.dumps(
                        decision_analysis.get("action_suggestions") or [],
                        ensure_ascii=False,
                    ),
                },
            ).mappings().first()
            db.commit()
            return row["id"] if row else None
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
