"""User growth memory service — save / load / update (no LLM)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.database.database import SessionLocal
from app.knowledge.memory.growth_context_builder import GrowthContextBuilder
from app.knowledge.memory.interest_analyzer import InterestAnalyzer
from app.knowledge.memory.memory_models import (
    AdvisorContinuityContext,
    UserGrowthMemory,
    UserInterestProfile,
    UserQuestionHistory,
)


def _parse_uuid(value: str | uuid.UUID | None) -> uuid.UUID | None:
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        # deterministic namespace UUID for non-UUID string ids (test/dev)
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"ziwei.user:{value}")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _sanitize_analysis(result: dict[str, Any] | None) -> dict[str, Any]:
    """Keep only non-sensitive analysis summary for continuity."""
    if not result:
        return {}
    return {
        "question_type": result.get("question_type"),
        "theory_used": list(result.get("theory_used") or [])[:8],
        "suggestions": list(result.get("suggestions") or [])[:6],
        "scenario_name": result.get("scenario_name"),
        "engine_version": result.get("engine_version"),
    }


class MemoryService:
    """Persistence layer for V3.3 growth memory tables."""

    @classmethod
    def get_user_context(
        cls,
        user_id: str | uuid.UUID,
        *,
        question_type: str = "personality",
        history_limit: int = 20,
    ) -> dict[str, Any]:
        uid = _parse_uuid(user_id)
        if uid is None:
            return GrowthContextBuilder.build_user_context_payload(
                profile={},
                history=[],
                memories=[],
                continuity=None,
                question_type=question_type,
            )

        db = SessionLocal()
        try:
            profile_row = db.scalar(
                select(UserInterestProfile).where(UserInterestProfile.user_id == uid)
            )
            profile = cls._profile_to_dict(profile_row) if profile_row else {
                f: 0.0
                for f in (
                    "career_interest",
                    "wealth_interest",
                    "relationship_interest",
                    "family_interest",
                    "learning_interest",
                    "growth_interest",
                )
            }
            if "keywords" not in profile:
                profile["keywords"] = []

            hist_rows = db.scalars(
                select(UserQuestionHistory)
                .where(UserQuestionHistory.user_id == uid)
                .order_by(UserQuestionHistory.created_at.desc())
                .limit(history_limit)
            ).all()
            history = [
                {
                    "id": str(r.id),
                    "question": r.question,
                    "question_type": r.question_type,
                    "theory_used": r.theory_used or [],
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in hist_rows
            ]

            mem_rows = db.scalars(
                select(UserGrowthMemory)
                .where(UserGrowthMemory.user_id == uid)
                .order_by(UserGrowthMemory.created_at.desc())
                .limit(30)
            ).all()
            memories = [
                {
                    "id": str(m.id),
                    "memory_type": m.memory_type,
                    "content": m.content,
                    "source_question_id": str(m.source_question_id) if m.source_question_id else None,
                }
                for m in mem_rows
            ]

            cont = db.scalar(
                select(AdvisorContinuityContext).where(AdvisorContinuityContext.user_id == uid)
            )
            continuity = (
                {
                    "summary": cont.summary,
                    "important_topics": cont.important_topics or [],
                    "last_analysis": cont.last_analysis or {},
                }
                if cont
                else None
            )

            return GrowthContextBuilder.build_user_context_payload(
                profile=profile,
                history=history,
                memories=memories,
                continuity=continuity,
                question_type=question_type,
            )
        finally:
            db.close()

    @classmethod
    def update_profile(
        cls,
        user_id: str | uuid.UUID,
        question_type: str,
        question: str = "",
    ) -> dict[str, Any]:
        uid = _parse_uuid(user_id)
        if uid is None:
            return {}

        db = SessionLocal()
        try:
            row = db.scalar(select(UserInterestProfile).where(UserInterestProfile.user_id == uid))
            current = cls._profile_to_dict(row) if row else {
                "career_interest": 0.0,
                "wealth_interest": 0.0,
                "relationship_interest": 0.0,
                "family_interest": 0.0,
                "learning_interest": 0.0,
                "growth_interest": 0.0,
                "keywords": [],
            }
            updated = InterestAnalyzer.apply_deltas(current, question_type, question)

            if row is None:
                row = UserInterestProfile(user_id=uid)
                db.add(row)

            row.career_interest = updated["career_interest"]
            row.wealth_interest = updated["wealth_interest"]
            row.relationship_interest = updated["relationship_interest"]
            row.family_interest = updated["family_interest"]
            row.learning_interest = updated["learning_interest"]
            row.growth_interest = updated["growth_interest"]
            row.keywords = updated.get("keywords") or []
            row.updated_at = _utcnow()
            db.commit()
            db.refresh(row)
            return cls._profile_to_dict(row)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def save_memory(
        cls,
        *,
        user_id: str | uuid.UUID,
        question: str,
        question_type: str,
        chart_id: str | uuid.UUID | None = None,
        theory_used: list[str] | None = None,
        analysis_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Persist question history, update interests, extract growth memories,
        refresh advisor continuity context.
        """
        uid = _parse_uuid(user_id)
        if uid is None:
            return {"saved": False, "reason": "invalid_user_id"}

        safe_q = InterestAnalyzer.sanitize_question(question)
        safe_analysis = _sanitize_analysis(analysis_result)
        theories = list(theory_used or safe_analysis.get("theory_used") or [])
        cid = _parse_uuid(chart_id) if chart_id else None

        db = SessionLocal()
        try:
            hist = UserQuestionHistory(
                user_id=uid,
                chart_id=cid,
                question=safe_q,
                question_type=question_type,
                analysis_result=safe_analysis,
                theory_used=theories,
            )
            db.add(hist)
            db.flush()

            # interest profile
            profile_row = db.scalar(
                select(UserInterestProfile).where(UserInterestProfile.user_id == uid)
            )
            current = cls._profile_to_dict(profile_row) if profile_row else {
                "career_interest": 0.0,
                "wealth_interest": 0.0,
                "relationship_interest": 0.0,
                "family_interest": 0.0,
                "learning_interest": 0.0,
                "growth_interest": 0.0,
                "keywords": [],
            }
            updated = InterestAnalyzer.apply_deltas(current, question_type, safe_q)
            if profile_row is None:
                profile_row = UserInterestProfile(user_id=uid)
                db.add(profile_row)
            profile_row.career_interest = updated["career_interest"]
            profile_row.wealth_interest = updated["wealth_interest"]
            profile_row.relationship_interest = updated["relationship_interest"]
            profile_row.family_interest = updated["family_interest"]
            profile_row.learning_interest = updated["learning_interest"]
            profile_row.growth_interest = updated["growth_interest"]
            profile_row.keywords = updated.get("keywords") or []
            profile_row.updated_at = _utcnow()

            # growth memories from explicit intents
            new_memories = GrowthContextBuilder.extract_growth_memories(safe_q)
            for item in new_memories:
                db.add(
                    UserGrowthMemory(
                        user_id=uid,
                        memory_type=item["memory_type"],
                        content=item["content"],
                        source_question_id=hist.id,
                    )
                )

            # continuity context
            main = InterestAnalyzer.main_interests(updated)
            topics = GrowthContextBuilder.previous_topics(
                [{"question": safe_q, "question_type": question_type}],
                keywords=list(updated.get("keywords") or []),
            )
            # merge with existing important topics
            cont = db.scalar(
                select(AdvisorContinuityContext).where(AdvisorContinuityContext.user_id == uid)
            )
            existing_topics = list((cont.important_topics if cont else None) or [])
            for t in topics:
                if t not in existing_topics:
                    existing_topics.append(t)
            goals = [m["content"] for m in new_memories if m["memory_type"] == "goal"]
            # also pull recent goals from DB
            recent_goals = db.scalars(
                select(UserGrowthMemory)
                .where(
                    UserGrowthMemory.user_id == uid,
                    UserGrowthMemory.memory_type == "goal",
                )
                .order_by(UserGrowthMemory.created_at.desc())
                .limit(5)
            ).all()
            for g in recent_goals:
                if g.content not in goals:
                    goals.append(g.content)

            summary = GrowthContextBuilder.build_summary(
                main_interests=main,
                previous_topics=existing_topics,
                goals=goals,
            )
            if cont is None:
                cont = AdvisorContinuityContext(user_id=uid)
                db.add(cont)
            cont.summary = summary
            cont.important_topics = existing_topics[:12]
            cont.last_analysis = {
                "question_type": question_type,
                "theory_used": theories[:8],
                "question_preview": safe_q[:80],
            }
            cont.updated_at = _utcnow()

            db.commit()
            return {
                "saved": True,
                "question_history_id": str(hist.id),
                "memories_added": len(new_memories),
                "main_interests": main,
                "interest_scores": {
                    "career": updated["career_interest"],
                    "wealth": updated["wealth_interest"],
                    "relationship": updated["relationship_interest"],
                    "family": updated["family_interest"],
                    "learning": updated["learning_interest"],
                    "growth": updated["growth_interest"],
                },
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def _profile_to_dict(cls, row: UserInterestProfile | None) -> dict[str, Any]:
        if row is None:
            return {}
        return {
            "career_interest": float(row.career_interest or 0),
            "wealth_interest": float(row.wealth_interest or 0),
            "relationship_interest": float(row.relationship_interest or 0),
            "family_interest": float(row.family_interest or 0),
            "learning_interest": float(row.learning_interest or 0),
            "growth_interest": float(row.growth_interest or 0),
            "keywords": list(row.keywords or []),
        }

    @classmethod
    def delete_user_data(cls, user_id: str | uuid.UUID) -> None:
        """Test helper — remove all V3.3 memory rows for a user."""
        uid = _parse_uuid(user_id)
        if uid is None:
            return
        db = SessionLocal()
        try:
            for model in (
                UserGrowthMemory,
                UserQuestionHistory,
                UserInterestProfile,
                AdvisorContinuityContext,
            ):
                rows = db.scalars(select(model).where(model.user_id == uid)).all()
                for r in rows:
                    db.delete(r)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
