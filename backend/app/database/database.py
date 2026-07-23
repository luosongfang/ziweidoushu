"""数据库连接与会话管理 — SQLAlchemy 2.0 + Supabase PostgreSQL。"""

from __future__ import annotations

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

REQUIRED_TABLES = frozenset(
    {
        "users",
        "birth_profiles",
        "ziwei_charts",
        "chart_palaces",
        "four_hua_rules",
        "user_charts",
        "analysis_history",
        "growth_profile",
        "user_reports",
        "user_growth_goals",
        "report_feedback",
    }
)


class Base(DeclarativeBase):
    """ORM 基类。"""


def _normalize_database_url(url: str) -> str:
    """为 Supabase PostgreSQL 补全 SSL 参数。"""
    if not url.startswith("postgresql"):
        return url
    if "sslmode=" in url:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}sslmode=require"


def _build_engine():
    url = _normalize_database_url(settings.database_url)
    is_sqlite = url.startswith("sqlite")

    kwargs: dict = {
        "echo": settings.debug,
        "pool_pre_ping": True,
    }

    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs.update(
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_timeout=30,
        )

    return create_engine(url, **kwargs)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def is_database_ready() -> bool:
    """数据库是否已配置且可连接。"""
    if settings.is_postgres and not settings.database_is_configured:
        return False
    return check_database_connection()


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as exc:
        logger.exception("数据库会话异常：%s", exc)
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection() -> bool:
    """测试数据库连接是否可用。"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as exc:
        logger.error("数据库连接失败：%s", exc)
        return False


def ensure_schema() -> None:
    """确保核心表存在（Alembic 未执行时的兜底建表）。"""
    from app.database import models  # noqa: F401

    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    missing = REQUIRED_TABLES - existing
    if not missing:
        return

    logger.warning("缺少数据表 %s，正在自动创建…", ", ".join(sorted(missing)))
    Base.metadata.create_all(bind=engine)


def _apply_v12_identity_patches() -> None:
    """V1.2 列级迁移（Alembic 未覆盖时的兜底）。"""
    patches = [
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS chart_name TEXT NOT NULL DEFAULT '未命名命盘'",
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS birth_date TEXT",
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS birth_time TEXT",
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS birth_place TEXT",
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS gender TEXT",
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS birth_info JSON DEFAULT '{}'",
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS is_default BOOLEAN NOT NULL DEFAULT false",
        "ALTER TABLE user_charts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP",
    ]
    if settings.is_postgres:
        patches = [p.replace("JSON DEFAULT", "JSONB DEFAULT") for p in patches]
    try:
        with engine.begin() as conn:
            for sql in patches:
                try:
                    conn.execute(text(sql))
                except SQLAlchemyError:
                    pass
    except SQLAlchemyError as exc:
        logger.warning("V1.2 列迁移跳过：%s", exc)


def _apply_membership_schema() -> None:
    """V1.2 会员表兜底（migration 018 未执行时）。"""
    if not settings.is_postgres:
        return
    statements = [
        """
        CREATE TABLE IF NOT EXISTS public.user_membership (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            plan_id TEXT NOT NULL DEFAULT 'free',
            status TEXT NOT NULL DEFAULT 'active',
            started_at TIMESTAMPTZ DEFAULT NOW(),
            expires_at TIMESTAMPTZ,
            analysis_used INTEGER DEFAULT 0,
            analysis_quota INTEGER,
            advisor_enabled BOOLEAN DEFAULT FALSE,
            knowledge_access TEXT DEFAULT 'none',
            metadata JSONB DEFAULT '{}'::jsonb,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS public.user_points (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            balance INTEGER NOT NULL DEFAULT 0,
            lifetime_earned INTEGER NOT NULL DEFAULT 0,
            lifetime_spent INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS public.user_points_ledger (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            delta INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            reason TEXT NOT NULL,
            ref_type TEXT,
            ref_id UUID,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_up_user ON public.user_points(user_id)",
    ]
    try:
        with engine.begin() as conn:
            for sql in statements:
                conn.execute(text(sql))
    except SQLAlchemyError as exc:
        logger.warning("会员表迁移跳过：%s", exc)


def _apply_v13_report_schema() -> None:
    """V1.3 报告与成长中心表兜底。"""
    if not settings.is_postgres:
        return
    statements = [
        """
        CREATE TABLE IF NOT EXISTS public.user_reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            chart_id UUID,
            report_type VARCHAR(32) NOT NULL DEFAULT 'life_profile',
            engine_version VARCHAR(16) NOT NULL DEFAULT '5.6',
            report_json JSONB NOT NULL DEFAULT '{}'::jsonb,
            summary TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS public.user_growth_goals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            goal_type VARCHAR(32) NOT NULL,
            goal_content TEXT NOT NULL DEFAULT '',
            progress VARCHAR(32) NOT NULL DEFAULT 'planned',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS public.report_feedback (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            report_id UUID NOT NULL,
            helpful BOOLEAN NOT NULL DEFAULT true,
            feedback_type VARCHAR(32) NOT NULL DEFAULT 'general',
            comment TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON public.user_reports(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_growth_goals_user_id ON public.user_growth_goals(user_id)",
    ]
    try:
        with engine.begin() as conn:
            for sql in statements:
                conn.execute(text(sql))
    except SQLAlchemyError as exc:
        logger.warning("V1.3 报告表迁移跳过：%s", exc)


def init_db() -> None:
    """启动时建表（如需）并写入四化种子数据。"""
    from app.database.models import seed_four_hua_rules

    if settings.is_postgres and not settings.database_is_configured:
        logger.error(
            "DATABASE_URL 仍为占位符，请在 backend/.env 填入 Supabase 密码后重启后端"
        )
        return

    if not check_database_connection():
        logger.warning("数据库不可用，跳过初始化")
        return

    try:
        ensure_schema()
        _apply_v12_identity_patches()
        _apply_membership_schema()
        _apply_v13_report_schema()
    except SQLAlchemyError as exc:
        logger.exception("自动建表失败：%s", exc)
        return

    db = SessionLocal()
    try:
        seed_four_hua_rules(db)
        db.commit()
        logger.info("数据库初始化完成（表结构 + 四化种子）")
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning("种子数据初始化失败：%s", exc)
    finally:
        db.close()


def database_status() -> dict[str, str | bool]:
    """供 health 接口返回的数据库状态。"""
    configured = settings.database_is_configured
    connected = check_database_connection() if configured else False
    return {
        "driver": "postgresql" if settings.is_postgres else "sqlite",
        "configured": configured,
        "connected": connected,
        "ready": configured and connected,
    }
