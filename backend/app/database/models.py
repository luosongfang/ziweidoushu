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


def ensure_db_user(db: Session, user_id: str | None, email: str | None = None) -> str | None:
    """确保 Supabase 登录用户在本地 users 表存在，避免 birth_profiles 外键失败。"""
    if not user_id:
        return None
    existing = db.get(User, user_id)
    if existing:
        return user_id
    db.add(User(id=user_id, email=email))
    db.flush()
    return user_id


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


class UserChart(Base):
    """V1.2 用户云端命盘 — migration 019_user_identity.sql"""

    __tablename__ = "user_charts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    chart_name: Mapped[str] = mapped_column(String(64), default="未命名命盘")
    birth_date: Mapped[str | None] = mapped_column(String(10))
    birth_time: Mapped[str | None] = mapped_column(String(8))
    birth_place: Mapped[str | None] = mapped_column(String(128))
    gender: Mapped[str | None] = mapped_column(String(8))
    chart_data: Mapped[dict] = mapped_column(JSON)
    birth_info: Mapped[dict] = mapped_column(JSON, default=dict)
    is_default: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # 兼容旧 API 字段名
    @property
    def name(self) -> str:
        return self.chart_name


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    chart_id: Mapped[str | None] = mapped_column(String(36), index=True)
    question: Mapped[str] = mapped_column(Text, default="")
    analysis_type: Mapped[str] = mapped_column(String(32), default="overview")
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class GrowthProfile(Base):
    __tablename__ = "growth_profile"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    interest_tags: Mapped[list] = mapped_column(JSON, default=list)
    career_focus: Mapped[str | None] = mapped_column(Text)
    decision_style: Mapped[str | None] = mapped_column(Text)
    growth_notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UserReport(Base):
    __tablename__ = "user_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    chart_id: Mapped[str | None] = mapped_column(String(36), index=True)
    report_type: Mapped[str] = mapped_column(String(32), default="life_profile")
    engine_version: Mapped[str] = mapped_column(String(16), default="5.6")
    report_json: Mapped[dict] = mapped_column(JSON, default=dict)
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UserGrowthGoal(Base):
    __tablename__ = "user_growth_goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    goal_type: Mapped[str] = mapped_column(String(32))
    goal_content: Mapped[str] = mapped_column(Text, default="")
    progress: Mapped[str] = mapped_column(String(32), default="planned")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ReportFeedback(Base):
    __tablename__ = "report_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    report_id: Mapped[str] = mapped_column(String(36), index=True)
    helpful: Mapped[bool] = mapped_column(default=True)
    feedback_type: Mapped[str] = mapped_column(String(32), default="general")
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


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


def _flatten_palace_stars(palace: dict) -> list[dict]:
    """兼容 V1 chart.palaces 与 V2 palace 星曜结构。"""
    if palace.get("stars"):
        return palace["stars"]

    stars: list[dict] = []
    for key, category in (
        ("main_stars", "main"),
        ("lucky_stars", "lucky"),
        ("sha_stars", "sha"),
        ("za_stars", "za"),
    ):
        for star in palace.get(key, []):
            entry = dict(star)
            entry.setdefault("category", category)
            stars.append(entry)
    return stars


def _extract_chart_meta(chart_data: dict) -> tuple[str, str, str, list[dict]]:
    """从 V1 或 V2 chart_data 提取命宫/身宫/五行局与宫位列表。"""
    if chart_data.get("schema_version") in ("2.0", "2.5"):
        meta = chart_data.get("meta", {})
        return (
            meta.get("mingGong", ""),
            meta.get("shenGong", ""),
            meta.get("wuxingJu", ""),
            chart_data.get("palaces", []),
        )

    chart_info = chart_data.get("chart", {})
    return (
        chart_info.get("ming_gong", ""),
        chart_info.get("shen_gong", ""),
        chart_info.get("five_element", ""),
        chart_info.get("palaces", []),
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
    ming_gong, shen_gong, five_element, palaces = _extract_chart_meta(chart_data)

    resolved_user_id = ensure_db_user(db, user_id)

    profile = BirthProfile(
        user_id=resolved_user_id,
        solar_date=solar_date,
        lunar_date=birth.get("lunar"),
        birth_time=birth_time,
        location=location,
        gender=chart_data.get("gender", "male"),
    )
    db.add(profile)
    db.flush()

    payload = dict(chart_data)
    payload.setdefault("schema_version", "2.5")

    chart = ZiweiChart(
        user_id=resolved_user_id,
        birth_profile_id=profile.id,
        ming_gong=ming_gong,
        shen_gong=shen_gong,
        five_element=five_element,
        chart_json=payload,
    )
    db.add(chart)
    db.flush()

    for palace in palaces:
        position = palace.get("branch") or str(palace.get("position", ""))
        transformations = palace.get("transformations", [])
        db.add(
            ChartPalace(
                chart_id=chart.id,
                palace_name=palace.get("name", ""),
                position=position,
                stars=_flatten_palace_stars(palace),
                transformations=transformations,
            )
        )

    return chart
