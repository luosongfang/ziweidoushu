"""Unified evaluation engine entrypoint (no LLM)."""

from __future__ import annotations

import uuid
from typing import Any

from app.knowledge.evaluation.case_library import CaseLibrary
from app.knowledge.evaluation.expert_review import ExpertReview
from app.knowledge.evaluation.quality_metrics import QualityMetrics
from app.knowledge.evaluation.theory_statistics import TheoryStatistics


class EvaluationEngine:
    """
    Evaluate analysis process quality:
    theory citation / logic completeness / safety / growth value / user feedback.
    Does NOT score destiny prediction accuracy.
    """

    @classmethod
    def evaluate_analysis(
        cls,
        *,
        analysis_result: dict[str, Any],
        feedback: dict[str, Any] | None = None,
        knowledge_trace: dict[str, Any] | None = None,
        sources: list[dict[str, Any]] | None = None,
        theory_used: list[str] | None = None,
        scenario: str | None = None,
        persist: bool = True,
        analysis_id: str | None = None,
        update_theory_stats: bool = True,
    ) -> dict[str, Any]:
        trace = knowledge_trace or analysis_result.get("knowledge_trace")
        quality = QualityMetrics.score(
            analysis_result=analysis_result,
            feedback=feedback,
            knowledge_trace=trace,
            sources=sources or analysis_result.get("sources"),
            persist=persist,
            analysis_id=analysis_id or str(uuid.uuid4()),
        )

        scen = (
            scenario
            or analysis_result.get("scenario_code")
            or (analysis_result.get("decision_analysis") or {}).get("scenario_code")
            or analysis_result.get("question_type")
            or "general"
        )
        theories = theory_used or analysis_result.get("theory_used") or []
        if not theories and analysis_result.get("theory_analysis"):
            theories = list((analysis_result.get("theory_analysis") or {}).keys())
            theories = [t for t in theories if t not in {"conflicts", "synthesis"}]

        stats_rows = []
        ftype = (feedback or {}).get("feedback_type")
        if update_theory_stats:
            stats_rows = TheoryStatistics.record_from_analysis(
                theory_used=theories or ["sanhe"],
                scenario=str(scen),
                feedback_type=ftype,
            )

        # V5.6: close the loop — quality (+ optional feedback) → dynamic weights
        optimization = None
        try:
            from app.knowledge.optimization import OptimizationService

            optimization = OptimizationService.update(
                scenario=str(scen),
                theory_used=theories or ["sanhe"],
                overall_score=float(quality.get("overall_score") or 0),
                feedback_type=ftype,
                analysis_id=analysis_id or quality.get("analysis_id"),
                source="evaluation_analysis",
                update_effectiveness=False,  # already recorded above
            )
        except Exception:
            optimization = {"error": "optimization_update_skipped"}

        return {
            "quality_score": {
                "theory_accuracy": quality["theory_accuracy"],
                "logic_score": quality["logic_score"],
                "safety_score": quality["safety_score"],
                "growth_value": quality["growth_value"],
                "overall_score": quality["overall_score"],
                "user_helpful_score": quality.get("user_helpful_score"),
                "citation_score": quality.get("citation_score"),
            },
            "metrics": quality,
            "theory_stats_updated": stats_rows,
            "optimization": optimization,
            "notice": quality.get("notice"),
            "engine_version": "5.6",
        }

    @classmethod
    def add_case(cls, payload: dict[str, Any]) -> dict[str, Any]:
        return CaseLibrary.save_case(payload)

    @classmethod
    def review_case(cls, **kwargs: Any) -> dict[str, Any]:
        return ExpertReview.submit(**kwargs)

    @classmethod
    def theory_stats(cls, scenario: str | None = None) -> dict[str, Any]:
        rows = TheoryStatistics.list_stats(scenario=scenario)
        return {
            "stats": rows,
            "ranking": TheoryStatistics.ranking_summary(),
            "engine_version": "5.6",
        }
