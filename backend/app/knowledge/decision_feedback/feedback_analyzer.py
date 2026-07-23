"""Analyze feedback acceptance / effectiveness / question patterns (no LLM)."""

from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.decision_feedback.feedback_service import parse_user_id

_ACCEPTANCE_SCORE = {
    "helpful": 1.0,
    "partially_helpful": 0.55,
    "future_check": 0.4,
    "not_helpful": 0.1,
}


class FeedbackAnalyzer:
    """Aggregate feedback signals for profile updates."""

    @classmethod
    def analyze_user(cls, user_id: str, *, limit: int = 100) -> dict[str, Any]:
        uid = parse_user_id(user_id)
        if uid is None:
            return cls._empty()

        db = SessionLocal()
        try:
            feedback_rows = db.execute(
                text(
                    """
                    SELECT feedback_type, result_status, feedback_content, created_at
                    FROM public.decision_feedback
                    WHERE user_id = :uid
                    ORDER BY created_at DESC
                    LIMIT :lim
                    """
                ),
                {"uid": str(uid), "lim": limit},
            ).mappings().all()

            history_rows = db.execute(
                text(
                    """
                    SELECT question_type, question_summary, analysis_summary, suggestions, created_at
                    FROM public.decision_history
                    WHERE user_id = :uid
                    ORDER BY created_at DESC
                    LIMIT :lim
                    """
                ),
                {"uid": str(uid), "lim": limit},
            ).mappings().all()
        finally:
            db.close()

        type_counts = Counter(r["feedback_type"] for r in feedback_rows)
        status_counts = Counter(r["result_status"] for r in feedback_rows)
        scores = [_ACCEPTANCE_SCORE.get(r["feedback_type"], 0.3) for r in feedback_rows]
        acceptance = round(sum(scores) / len(scores), 3) if scores else 0.0

        # effectiveness: confirmed > changed > pending
        eff_weights = {"confirmed": 1.0, "changed": 0.6, "pending": 0.3, "unknown": 0.2}
        eff_scores = [eff_weights.get(r["result_status"] or "pending", 0.3) for r in feedback_rows]
        effectiveness = round(sum(eff_scores) / len(eff_scores), 3) if eff_scores else 0.0

        qtypes = Counter(r["question_type"] for r in history_rows if r.get("question_type"))
        top_questions = [q for q, _ in qtypes.most_common(5)]

        decision_style = cls._infer_style(acceptance, type_counts)
        risk_preference = cls._infer_risk(type_counts, status_counts)

        return {
            "acceptance_rate": acceptance,
            "effectiveness": effectiveness,
            "feedback_counts": dict(type_counts),
            "result_status_counts": dict(status_counts),
            "top_question_types": top_questions,
            "decision_style": decision_style,
            "risk_preference": risk_preference,
            "feedback_total": len(feedback_rows),
            "history_total": len(history_rows),
            "recent_summaries": [
                {
                    "question_type": r.get("question_type"),
                    "question_summary": r.get("question_summary"),
                }
                for r in history_rows[:5]
            ],
        }

    @classmethod
    def _empty(cls) -> dict[str, Any]:
        return {
            "acceptance_rate": 0.0,
            "effectiveness": 0.0,
            "feedback_counts": {},
            "result_status_counts": {},
            "top_question_types": [],
            "decision_style": "exploratory",
            "risk_preference": "balanced",
            "feedback_total": 0,
            "history_total": 0,
            "recent_summaries": [],
        }

    @classmethod
    def _infer_style(cls, acceptance: float, counts: Counter) -> str:
        helpful = counts.get("helpful", 0)
        not_h = counts.get("not_helpful", 0)
        if acceptance >= 0.7 and helpful >= not_h:
            return "pragmatic_acceptor"
        if not_h > helpful:
            return "critical_evaluator"
        if counts.get("future_check", 0) >= max(helpful, 1):
            return "long_horizon_checker"
        return "exploratory"

    @classmethod
    def _infer_risk(cls, type_counts: Counter, status_counts: Counter) -> str:
        if status_counts.get("changed", 0) >= 2:
            return "adaptive"
        if type_counts.get("not_helpful", 0) >= type_counts.get("helpful", 0) + 1:
            return "cautious"
        if type_counts.get("helpful", 0) >= 3:
            return "engaged"
        return "balanced"
