"""Long-term user decision profile — updated from feedback loop (no LLM)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.decision_feedback.feedback_analyzer import FeedbackAnalyzer
from app.knowledge.decision_feedback.feedback_service import parse_user_id


class DecisionProfile:
    """Build / refresh user_decision_profile."""

    @classmethod
    def get_profile(cls, user_id: str) -> dict[str, Any]:
        uid = parse_user_id(user_id)
        if uid is None:
            return cls._empty(str(user_id))

        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT user_id::text, decision_style, risk_preference,
                           strength_patterns, challenge_patterns, growth_history, updated_at
                    FROM public.user_decision_profile
                    WHERE user_id = :uid
                    LIMIT 1
                    """
                ),
                {"uid": str(uid)},
            ).mappings().first()
            if row:
                data = dict(row)
                for k in ("strength_patterns", "challenge_patterns", "growth_history"):
                    v = data.get(k)
                    if isinstance(v, str):
                        data[k] = json.loads(v)
                    data[k] = list(data.get(k) or [])
                if data.get("updated_at"):
                    data["updated_at"] = data["updated_at"].isoformat()
                analysis = FeedbackAnalyzer.analyze_user(str(uid))
                data["analytics"] = analysis
                return data
        finally:
            db.close()

        # auto-build if missing
        return cls.refresh_profile(str(uid))

    @classmethod
    def refresh_profile(
        cls,
        user_id: str,
        *,
        extra_strengths: list[str] | None = None,
        extra_challenges: list[str] | None = None,
    ) -> dict[str, Any]:
        uid = parse_user_id(user_id)
        if uid is None:
            raise ValueError("invalid user_id")

        analysis = FeedbackAnalyzer.analyze_user(str(uid))
        strengths = list(extra_strengths or [])
        challenges = list(extra_challenges or [])

        # derive patterns from history suggestions text lightly
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT suggestions, analysis_summary
                    FROM public.decision_history
                    WHERE user_id = :uid
                    ORDER BY created_at DESC
                    LIMIT 20
                    """
                ),
                {"uid": str(uid)},
            ).mappings().all()
            for r in rows:
                sug = r.get("suggestions") or []
                if isinstance(sug, str):
                    sug = json.loads(sug)
                for s in sug[:2]:
                    if s and str(s) not in strengths:
                        strengths.append(str(s)[:120])
                summary = r.get("analysis_summary") or ""
                if "风险" in summary and summary not in challenges:
                    challenges.append("关注风险管理与安全垫")
        finally:
            db.close()

        growth_history = [
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "acceptance_rate": analysis.get("acceptance_rate"),
                "effectiveness": analysis.get("effectiveness"),
                "top_question_types": analysis.get("top_question_types"),
                "decision_style": analysis.get("decision_style"),
            }
        ]

        # merge previous growth_history
        existing = cls._load_raw(str(uid))
        if existing and existing.get("growth_history"):
            prev = list(existing["growth_history"] or [])
            growth_history = (growth_history + prev)[:30]
            if not strengths:
                strengths = list(existing.get("strength_patterns") or [])
            if not challenges:
                challenges = list(existing.get("challenge_patterns") or [])
            # keep unique
            strengths = list(dict.fromkeys(list(existing.get("strength_patterns") or []) + strengths))[:12]
            challenges = list(dict.fromkeys(list(existing.get("challenge_patterns") or []) + challenges))[:12]

        payload = {
            "user_id": str(uid),
            "decision_style": analysis.get("decision_style") or "exploratory",
            "risk_preference": analysis.get("risk_preference") or "balanced",
            "strength_patterns": strengths[:12],
            "challenge_patterns": challenges[:12],
            "growth_history": growth_history,
            "analytics": analysis,
        }

        db = SessionLocal()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO public.user_decision_profile
                        (user_id, decision_style, risk_preference,
                         strength_patterns, challenge_patterns, growth_history, updated_at)
                    VALUES
                        (:uid, :style, :risk,
                         CAST(:strengths AS jsonb), CAST(:challenges AS jsonb),
                         CAST(:growth AS jsonb), NOW())
                    ON CONFLICT (user_id) DO UPDATE SET
                        decision_style = EXCLUDED.decision_style,
                        risk_preference = EXCLUDED.risk_preference,
                        strength_patterns = EXCLUDED.strength_patterns,
                        challenge_patterns = EXCLUDED.challenge_patterns,
                        growth_history = EXCLUDED.growth_history,
                        updated_at = NOW()
                    """
                ),
                {
                    "uid": str(uid),
                    "style": payload["decision_style"],
                    "risk": payload["risk_preference"],
                    "strengths": json.dumps(payload["strength_patterns"], ensure_ascii=False),
                    "challenges": json.dumps(payload["challenge_patterns"], ensure_ascii=False),
                    "growth": json.dumps(payload["growth_history"], ensure_ascii=False),
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        return payload

    @classmethod
    def _load_raw(cls, user_id: str) -> dict[str, Any] | None:
        uid = parse_user_id(user_id)
        if uid is None:
            return None
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT strength_patterns, challenge_patterns, growth_history
                    FROM public.user_decision_profile WHERE user_id = :uid
                    """
                ),
                {"uid": str(uid)},
            ).mappings().first()
            if not row:
                return None
            data = dict(row)
            for k in ("strength_patterns", "challenge_patterns", "growth_history"):
                v = data.get(k)
                if isinstance(v, str):
                    data[k] = json.loads(v)
                data[k] = list(data.get(k) or [])
            return data
        finally:
            db.close()

    @classmethod
    def _empty(cls, user_id: str) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "decision_style": "exploratory",
            "risk_preference": "balanced",
            "strength_patterns": [],
            "challenge_patterns": [],
            "growth_history": [],
            "analytics": FeedbackAnalyzer._empty(),
            "updated_at": None,
        }
