"""Pytest fixtures — reduce remote DB noise/latency in tests."""

from __future__ import annotations

import logging

import pytest


@pytest.fixture(scope="session", autouse=True)
def _quiet_sqlalchemy():
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    try:
        from app.database import database as dbmod

        dbmod.engine.echo = False
    except Exception:
        pass
