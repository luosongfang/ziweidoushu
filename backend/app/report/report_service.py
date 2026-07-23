"""Report persistence service — V1.3。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database.database import SessionLocal, is_database_ready
from app.database.models import ReportFeedback, UserGrowthGoal, UserReport
from app.models.user import AuthUser
from app.report.report_generator import ReportGenerator
from app.services.user_identity_service import UserIdentityService


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReportService:
    @classmethod
    def create_report(
        cls,
        user: AuthUser,
        *,
        chart_id: str,
        report_type: str,
        db: Session,
    ) -> UserReport:
        chart = UserIdentityService.get_chart(db, user, chart_id)
        if not chart:
            raise ValueError("命盘不存在或无权访问")
        chart_data = dict(chart.chart_data or {})
        if chart.birth_info:
            chart_data.setdefault("birth_info", chart.birth_info)
        payload = ReportGenerator.generate(
            chart_data=chart_data,
            report_type=report_type,
            user_id=str(user.id),
        )
        record = UserReport(
            id=str(uuid4()),
            user_id=str(user.id),
            chart_id=str(chart.id),
            report_type=report_type,
            engine_version=payload["engine_version"],
            report_json={
                "sections": payload["report_sections"],
                "knowledge_trace": payload.get("knowledge_trace") or {},
                "safety_notice": payload.get("safety_notice") or "",
            },
            summary=payload["summary"],
        )
        db.add(record)
        db.flush()
        return record

    @classmethod
    def list_reports(cls, user: AuthUser, db: Session, limit: int = 20) -> list[UserReport]:
        return list(
            db.scalars(
                select(UserReport)
                .where(UserReport.user_id == str(user.id))
                .order_by(UserReport.created_at.desc())
                .limit(limit)
            ).all()
        )

    @classmethod
    def get_report(cls, user: AuthUser, report_id: str, db: Session) -> UserReport | None:
        return db.scalar(
            select(UserReport).where(
                UserReport.id == report_id,
                UserReport.user_id == str(user.id),
            )
        )

    @classmethod
    def save_feedback(
        cls,
        user: AuthUser,
        *,
        report_id: str,
        helpful: bool,
        feedback_type: str,
        comment: str,
        db: Session,
    ) -> ReportFeedback:
        report = cls.get_report(user, report_id, db)
        if not report:
            raise ValueError("报告不存在")
        row = ReportFeedback(
            id=str(uuid4()),
            user_id=str(user.id),
            report_id=report_id,
            helpful=helpful,
            feedback_type=feedback_type,
            comment=comment[:2000],
        )
        db.add(row)
        db.flush()
        return row


class GrowthCenterService:
    @classmethod
    def get_profile(cls, user: AuthUser, db: Session) -> dict[str, Any]:
        from app.knowledge.memory.memory_service import MemoryService
        from app.services.user_identity_service import UserIdentityService

        uid = str(user.id)
        ctx = MemoryService.get_user_context(uid, question_type="personality")
        history_rows = UserIdentityService.list_analysis_history(db, user, limit=15)
        history = [
            {
                "id": r.id,
                "question": r.question,
                "analysis_type": r.analysis_type,
                "summary": r.summary,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in history_rows
        ]
        goals = list(
            db.scalars(
                select(UserGrowthGoal)
                .where(UserGrowthGoal.user_id == uid)
                .order_by(UserGrowthGoal.updated_at.desc())
                .limit(10)
            ).all()
        )
        if not goals and is_database_ready():
            cls._seed_default_goals(uid, db)
            goals = list(
                db.scalars(
                    select(UserGrowthGoal).where(UserGrowthGoal.user_id == uid).limit(5)
                ).all()
            )
        return {
            "history": history,
            "focus_topics": list(ctx.get("main_interests") or ctx.get("focus_topics") or []),
            "goals": [
                {
                    "id": g.id,
                    "goal_type": g.goal_type,
                    "goal_content": g.goal_content,
                    "progress": g.progress,
                }
                for g in goals
            ],
            "advisor_suggestions": list(ctx.get("growth_goals") or [])[:5],
            "continuity_message": str(ctx.get("continuity_message") or ""),
        }

    @classmethod
    def _seed_default_goals(cls, user_id: str, db: Session) -> None:
        defaults = [
            ("growth", "建立稳定的自我认知与反思习惯"),
            ("career", "探索适合长期投入的事业方向"),
        ]
        for goal_type, content in defaults:
            db.add(
                UserGrowthGoal(
                    id=str(uuid4()),
                    user_id=user_id,
                    goal_type=goal_type,
                    goal_content=content,
                    progress="planned",
                )
            )
        db.flush()
