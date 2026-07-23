"""用户云端命盘服务 — 委托 UserIdentityService（兼容层）。"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models import UserChart
from app.models.user import AuthUser
from app.services.user_identity_service import UserIdentityService


class UserChartService:
    @classmethod
    def save(
        cls,
        db: Session,
        user: AuthUser,
        *,
        name: str,
        chart_data: dict,
        birth_info: dict,
        set_default: bool = True,
        birth_date: str | None = None,
        birth_time: str | None = None,
        birth_place: str | None = None,
        gender: str | None = None,
    ) -> UserChart:
        return UserIdentityService.save_chart(
            db,
            user,
            chart_name=name,
            chart_data=chart_data,
            birth_info=birth_info,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place,
            gender=gender,
            set_default=set_default,
        )

    @classmethod
    def list_charts(cls, db: Session, user: AuthUser) -> list[UserChart]:
        return UserIdentityService.list_charts(db, user)

    @classmethod
    def get_chart(cls, db: Session, user: AuthUser, chart_id: UUID) -> UserChart | None:
        return UserIdentityService.get_chart(db, user, str(chart_id))

    @classmethod
    def set_default(cls, db: Session, user: AuthUser, chart_id: UUID) -> UserChart:
        from datetime import datetime, timezone
        from sqlalchemy import update

        record = cls.get_chart(db, user, chart_id)
        if not record:
            raise ValueError("命盘不存在或无权访问")
        uid = str(user.id)
        db.execute(update(UserChart).where(UserChart.user_id == uid).values(is_default=False))
        record.is_default = True
        record.updated_at = datetime.now(timezone.utc)
        return record
