"""V1.5 Phase 5 门禁 — 十四主星未达专业宣称前禁止扩展岁前/将前/长生/博士。"""

from __future__ import annotations

from app.ziwei.accuracy.fourteen_star_gate import (
    MISSING_STAR_GROUPS,
    can_expand_professional_aux_systems,
    missing_star_inventory,
)
from app.ziwei.rules.cache import clear_rules_cache
import pytest


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestPhase5Blocked:
    def test_aux_expansion_blocked(self):
        gate = can_expand_professional_aux_systems()
        assert gate["allowed"] is False
        assert gate["reason_code"] == "fourteen_stars_not_professionally_verified"

    def test_missing_groups_listed(self):
        inv = missing_star_inventory()
        for g in ("岁前十二神", "将前十二神", "长生十二神", "博士十二神"):
            assert g in inv["missing_groups"]
            assert g in MISSING_STAR_GROUPS
