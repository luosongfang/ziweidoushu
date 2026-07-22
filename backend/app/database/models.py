"""SQLAlchemy ORM 模型 — Phase 2 商业级数据层。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

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
    display_name: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    birth_profiles: Mapped[list["BirthProfile"]] = relationship(back_populates="user")
    charts: Mapped[list["Chart"]] = relationship(back_populates="user")
    ai_reports: Mapped[list["AiReport"]] = relationship(back_populates="user")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class BirthProfile(Base):
    __tablename__ = "birth_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    gender: Mapped[str] = mapped_column(String(8))
    solar_date: Mapped[str] = mapped_column(String(10))
    birth_time: Mapped[str] = mapped_column(String(5))
    location: Mapped[str | None] = mapped_column(String(128))
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="birth_profiles")
    charts: Mapped[list["Chart"]] = relationship(back_populates="birth_profile")


class Chart(Base):
    __tablename__ = "charts_orm"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    birth_profile_id: Mapped[str | None] = mapped_column(ForeignKey("birth_profiles.id"))
    name: Mapped[str] = mapped_column(String(64))
    chart_json: Mapped[dict] = mapped_column(JSON)
    engine_version: Mapped[str] = mapped_column(String(16), default="1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User | None"] = relationship(back_populates="charts")
    birth_profile: Mapped["BirthProfile | None"] = relationship(back_populates="charts")
    palaces: Mapped[list["PalaceRecord"]] = relationship(back_populates="chart")
    ai_reports: Mapped[list["AiReport"]] = relationship(back_populates="chart")


class PalaceRecord(Base):
    __tablename__ = "palaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chart_id: Mapped[str] = mapped_column(ForeignKey("charts_orm.id"), index=True)
    name: Mapped[str] = mapped_column(String(16))
    branch: Mapped[str] = mapped_column(String(2))
    position: Mapped[int] = mapped_column(Integer)
    ganzhi: Mapped[str | None] = mapped_column(String(4))
    is_ming_gong: Mapped[bool] = mapped_column(Boolean, default=False)
    is_shen_gong: Mapped[bool] = mapped_column(Boolean, default=False)
    stars_json: Mapped[dict | None] = mapped_column(JSON)
    transformations_json: Mapped[dict | None] = mapped_column(JSON)

    chart: Mapped["Chart"] = relationship(back_populates="palaces")


class StarRule(Base):
    """星曜元数据 / 安星规则索引。"""

    __tablename__ = "star_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    star_name: Mapped[str] = mapped_column(String(16), index=True)
    category: Mapped[str] = mapped_column(String(16))
    rule_type: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text)
    school: Mapped[str] = mapped_column(String(16), default="sanhe")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class FourHuaRuleModel(Base):
    """生年四化规则表。"""

    __tablename__ = "four_hua_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    year_gan: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    hua_lu: Mapped[str] = mapped_column(String(8))
    hua_quan: Mapped[str] = mapped_column(String(8))
    hua_ke: Mapped[str] = mapped_column(String(8))
    hua_ji: Mapped[str] = mapped_column(String(8))
    school: Mapped[str] = mapped_column(String(16), default="sanhe")


class AiReport(Base):
    __tablename__ = "ai_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    chart_id: Mapped[str] = mapped_column(ForeignKey("charts_orm.id"), index=True)
    analysis_type: Mapped[str] = mapped_column(String(16), default="overall")
    result_text: Mapped[str] = mapped_column(Text)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User | None"] = relationship(back_populates="ai_reports")
    chart: Mapped["Chart"] = relationship(back_populates="ai_reports")


class Membership(Base):
    __tablename__ = "membership"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    level: Mapped[str] = mapped_column(String(16), default="free")
    ai_quota: Mapped[int] = mapped_column(Integer, default=3)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="memberships")


class Order(Base):
    __tablename__ = "orders_orm"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    plan_id: Mapped[str] = mapped_column(String(16))
    amount_cents: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="orders")


def seed_four_hua_rules(db: Session) -> None:
    """写入十天干四化规则（幂等）。"""
    existing = db.scalar(select(FourHuaRuleModel).limit(1))
    if existing is not None:
        return
    for rule in DEFAULT_FOUR_HUA_RULES:
        db.add(FourHuaRuleModel(
            year_gan=rule.year_gan,
            hua_lu=rule.hua_lu,
            hua_quan=rule.hua_quan,
            hua_ke=rule.hua_ke,
            hua_ji=rule.hua_ji,
        ))


def persist_chart(db: Session, chart_data: dict, user_id: str | None = None) -> Chart:
    """将命盘 JSON 持久化到 ORM。"""
    chart = Chart(
        user_id=user_id,
        name=chart_data.get("name", "未命名"),
        chart_json=chart_data,
        engine_version=chart_data.get("engine_version", "1.0"),
    )
    db.add(chart)
    db.flush()

    for p in chart_data.get("chart", {}).get("palaces", []):
        db.add(PalaceRecord(
            chart_id=chart.id,
            name=p["name"],
            branch=p["branch"],
            position=p["position"],
            ganzhi=p.get("ganzhi"),
            is_ming_gong=p.get("is_ming_gong", False),
            is_shen_gong=p.get("is_shen_gong", False),
            stars_json={"stars": p.get("stars", [])},
            transformations_json={"transformations": p.get("transformations", [])},
        ))
    return chart
