"""用户身份与成长档案服务 — V1.2。"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database.models import AnalysisHistory, GrowthProfile, UserChart
from app.models.user import AuthUser


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserIdentityService:
    @staticmethod
    def get_or_create_profile(db: Session, user: AuthUser) -> dict:
        """返回用户 profile 摘要（内存 + 可选 DB）。"""
        from app.services.membership_service import MembershipService
        from app.services.profile_service import ProfileService

        p = ProfileService.get_me(user)
        membership = MembershipService.get_status(str(user.id), db=db)
        return {
            "id": str(user.id),
            "auth_user_id": str(user.id),
            "nickname": p.display_name or user.email or "用户",
            "avatar_url": p.avatar_url,
            "membership": membership["plan_id"],
            "points": membership["points"],
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
        }

    @classmethod
    def save_chart(
        cls,
        db: Session,
        user: AuthUser,
        *,
        chart_name: str,
        chart_data: dict,
        birth_info: dict | None = None,
        birth_date: str | None = None,
        birth_time: str | None = None,
        birth_place: str | None = None,
        gender: str | None = None,
        set_default: bool = True,
    ) -> UserChart:
        uid = str(user.id)
        info = birth_info or {}
        if set_default:
            db.execute(
                update(UserChart).where(UserChart.user_id == uid).values(is_default=False, updated_at=_utcnow())
            )
        record = UserChart(
            user_id=uid,
            chart_name=chart_name or "未命名命盘",
            chart_data=chart_data,
            birth_info=info,
            birth_date=birth_date or info.get("solar", "")[:10] if info.get("solar") else None,
            birth_time=birth_time,
            birth_place=birth_place,
            gender=gender,
            is_default=set_default,
        )
        db.add(record)
        db.flush()
        return record

    @classmethod
    def list_charts(cls, db: Session, user: AuthUser) -> list[UserChart]:
        uid = str(user.id)
        return list(
            db.scalars(
                select(UserChart)
                .where(UserChart.user_id == uid)
                .order_by(UserChart.is_default.desc(), UserChart.created_at.desc())
            ).all()
        )

    @classmethod
    def get_chart(cls, db: Session, user: AuthUser, chart_id: str) -> UserChart | None:
        uid = str(user.id)
        return db.scalar(
            select(UserChart).where(UserChart.id == chart_id, UserChart.user_id == uid)
        )

    @classmethod
    def save_analysis(
        cls,
        db: Session,
        user: AuthUser,
        *,
        chart_id: str | None,
        question: str,
        analysis_type: str,
        summary: str,
    ) -> AnalysisHistory:
        record = AnalysisHistory(
            user_id=str(user.id),
            chart_id=chart_id,
            question=question,
            analysis_type=analysis_type,
            summary=summary[:4000],
        )
        db.add(record)
        db.flush()
        return record

    @classmethod
    def list_analysis_history(cls, db: Session, user: AuthUser, limit: int = 30) -> list[AnalysisHistory]:
        return list(
            db.scalars(
                select(AnalysisHistory)
                .where(AnalysisHistory.user_id == str(user.id))
                .order_by(AnalysisHistory.created_at.desc())
                .limit(limit)
            ).all()
        )

    @classmethod
    def upsert_growth_profile(
        cls,
        db: Session,
        user: AuthUser,
        *,
        interest_tags: list | None = None,
        career_focus: str | None = None,
        decision_style: str | None = None,
        growth_notes: str | None = None,
    ) -> GrowthProfile:
        uid = str(user.id)
        row = db.scalar(select(GrowthProfile).where(GrowthProfile.user_id == uid))
        if row is None:
            row = GrowthProfile(user_id=uid)
            db.add(row)
        if interest_tags is not None:
            row.interest_tags = interest_tags
        if career_focus is not None:
            row.career_focus = career_focus
        if decision_style is not None:
            row.decision_style = decision_style
        if growth_notes is not None:
            row.growth_notes = growth_notes
        row.updated_at = _utcnow()
        db.flush()
        return row

    @classmethod
    def get_growth_profile(cls, db: Session, user: AuthUser) -> GrowthProfile | None:
        return db.scalar(select(GrowthProfile).where(GrowthProfile.user_id == str(user.id)))
