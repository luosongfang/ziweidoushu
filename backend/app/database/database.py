"""数据库连接与会话管理 — SQLAlchemy 2.0 + Supabase PostgreSQL。"""

from __future__ import annotations

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """ORM 基类。"""


def _build_engine():
    url = settings.database_url
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


def init_db() -> None:
    """启动时写入四化种子数据（表结构由 Alembic 管理）。"""
    from app.database.models import seed_four_hua_rules

    if not check_database_connection():
        logger.warning("数据库不可用，跳过种子数据初始化")
        return

    db = SessionLocal()
    try:
        seed_four_hua_rules(db)
        db.commit()
        logger.info("四化规则种子数据已就绪")
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning("种子数据初始化失败（可能尚未执行迁移）：%s", exc)
    finally:
        db.close()
