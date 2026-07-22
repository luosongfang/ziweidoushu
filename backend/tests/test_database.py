"""Supabase PostgreSQL 连接测试 — Phase 2.5。"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import inspect, text

from app.config import settings
from app.database.database import check_database_connection, engine


def _is_real_postgres() -> bool:
    url = os.getenv("DATABASE_URL", settings.database_url)
    return url.startswith("postgresql") and "[YOUR-PASSWORD]" not in url


@pytest.mark.skipif(not _is_real_postgres(), reason="未配置有效的 Supabase DATABASE_URL")
class TestSupabaseConnection:
    def test_database_connection(self) -> None:
        assert check_database_connection() is True

    def test_select_one(self) -> None:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS ok")).scalar_one()
        assert result == 1

    def test_expected_tables_exist(self) -> None:
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        expected = {
            "users",
            "birth_profiles",
            "ziwei_charts",
            "chart_palaces",
            "star_rules",
            "four_hua_rules",
            "ai_reports",
            "memberships",
            "orders",
            "alembic_version",
        }
        missing = expected - tables
        assert not missing, f"缺少数据表: {missing}"
