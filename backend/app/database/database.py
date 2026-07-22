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
