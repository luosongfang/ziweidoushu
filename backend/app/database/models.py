"""SQLAlchemy ORM 模型 — Phase 2.5 Supabase 商业级数据层。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    JSON,
    select,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.database import Base
from app.ziwei_engine.transformation.four_hua import DEFAULT_FOUR_HUA_RULES


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    birth_profiles: Mapped[list["BirthProfile"]] = relationship(back_populates="user")
    charts: Mapped[list["ZiweiChart"]] = relationship(back_populates="user")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class BirthProfile(Base):
    __tablename__ = "birth_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    solar_date: Mapped[str] = mapped_column(String(10))
    lunar_date: Mapped[str | None] = mapped_column(String(32))
    birth_time: Mapped[str] = mapped_column(String(5))
    location: Mapped[str | None] = mapped_column(String(128))
    gender: Mapped[str] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User | None"] = relationship(back_populates="birth_profiles")
    charts: Mapped[list["ZiweiChart"]] = relationship(back_populates="birth_profile")


class ZiweiChart(Base):
    __tablename__ = "ziwei_charts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    birth_profile_id: Mapped[str | None] = mapped_column(ForeignKey("birth_profiles.id"))
    ming_gong: Mapped[str] = mapped_column(String(8))
    shen_gong: Mapped[str] = mapped_column(String(8))
    five_element: Mapped[str] = mapped_column(String(16))
    chart_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User | None"] = relationship(back_populates="charts")
    birth_profile: Mapped["BirthProfile | None"] = relationship(back_populates="charts")
    palaces: Mapped[list["ChartPalace"]] = relationship(
        back_populates="chart",
        cascade="all, delete-orphan",
    )
    ai_reports: Mapped[list["AiReport"]] = relationship(back_populates="chart")


class ChartPalace(Base):
    __tablename__ = "chart_palaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chart_id: Mapped[str] = mapped_column(ForeignKey("ziwei_charts.id"), index=True)
    palace_name: Mapped[str] = mapped_column(String(16))
    position: Mapped[str] = mapped_column(String(8))
    stars: Mapped[list] = mapped_column(JSON, default=list)
    transformations: Mapped[list] = mapped_column(JSON, default=list)

    chart: Mapped["ZiweiChart"] = relationship(back_populates="palaces")


class StarRule(Base):
    __tablename__ = "star_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    star_name: Mapped[str] = mapped_column(String(16), index=True)
    category: Mapped[str] = mapped_column(String(16))
    description: Mapped[str | None] = mapped_column(Text)
    rule_json: Mapped[dict | None] = mapped_column(JSON)


class FourHuaRule(Base):
    __tablename__ = "four_hua_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    year_gan: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    hua_lu: Mapped[str] = mapped_column(String(8))
    hua_quan: Mapped[str] = mapped_column(String(8))
    hua_ke: Mapped[str] = mapped_column(String(8))
    hua_ji: Mapped[str] = mapped_column(String(8))


class AiReport(Base):
    __tablename__ = "ai_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chart_id: Mapped[str] = mapped_column(ForeignKey("ziwei_charts.id"), index=True)
    report_type: Mapped[str] = mapped_column(String(32), default="overall")
    content: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(64), default="rule-based")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    chart: Mapped["ZiweiChart"] = relationship(back_populates="ai_reports")


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    level: Mapped[str] = mapped_column(String(16), default="free")
    expire_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="memberships")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="orders")


def seed_four_hua_rules(db: Session) -> None:
    """写入十天干四化规则（幂等）。"""
    existing = db.scalar(select(FourHuaRule).limit(1))
    if existing is not None:
        return
    for rule in DEFAULT_FOUR_HUA_RULES:
        db.add(
            FourHuaRule(
                year_gan=rule.year_gan,
                hua_lu=rule.hua_lu,
                hua_quan=rule.hua_quan,
                hua_ke=rule.hua_ke,
                hua_ji=rule.hua_ji,
            )
        )


def persist_chart(
    db: Session,
    chart_data: dict,
    *,
    solar_date: str,
    birth_time: str,
    location: str | None,
    user_id: str | None = None,
) -> ZiweiChart:
    """将出生资料与命盘 JSON 持久化到 Supabase PostgreSQL。"""
    birth = chart_data.get("birth", {})
    chart_info = chart_data.get("chart", {})

    profile = BirthProfile(
        user_id=user_id,
        solar_date=solar_date,
        lunar_date=birth.get("lunar"),
        birth_time=birth_time,
        location=location,
        gender=chart_data.get("gender", "male"),
    )
    db.add(profile)
    db.flush()

    chart = ZiweiChart(
        user_id=user_id,
        birth_profile_id=profile.id,
        ming_gong=chart_info.get("ming_gong", ""),
        shen_gong=chart_info.get("shen_gong", ""),
        five_element=chart_info.get("five_element", ""),
        chart_json=chart_data,
    )
    db.add(chart)
    db.flush()

    for palace in chart_info.get("palaces", []):
        position = palace.get("branch") or str(palace.get("position", ""))
        db.add(
            ChartPalace(
                chart_id=chart.id,
                palace_name=palace.get("name", ""),
                position=position,
                stars=palace.get("stars", []),
                transformations=palace.get("transformations", []),
            )
        )

    return chart
