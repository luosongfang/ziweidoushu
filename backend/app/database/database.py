"""数据库连接与会话管理 — SQLAlchemy 2.0。"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """ORM 基类。"""


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """创建所有表并写入四化种子。"""
    from app.database import models  # noqa: F401 — 注册模型
    from app.database.models import seed_four_hua_rules

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_four_hua_rules(db)
        db.commit()
    finally:
        db.close()
