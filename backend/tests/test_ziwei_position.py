"""紫微定位校准 — 仅 verified_professional。"""

from __future__ import annotations

import pytest

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.debug.classical_audit import run_classical_audit
from app.ziwei.debug.reference_manager import list_auto_test_charts
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.rules.loader import RulesLoader
from app.ziwei.rules.seed_generator import calc_ziwei_branch_index


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestZiweiPosition:
    def test_ref01_day21_bureau5(self):
        """土五局 + 廿一 → 巳（与 REF-01 / SC-C01 一致）。"""
        idx = calc_ziwei_branch_index(21, 5)
        assert EARTHLY_BRANCHES[idx] == "巳"
        assert RulesLoader.get_ziwei_position(5, 21) == "巳"

    @pytest.mark.parametrize("case", list_auto_test_charts(), ids=lambda c: c["id"])
    def test_verified_ziwei(self, case):
        birth = case["birth"]
        audit = run_classical_audit(
            birth_date=birth["solar"],
            birth_time=birth["time"],
            gender=case["gender"],
            location=case.get("location") or birth.get("location"),
        )
        meta = case["meta"]
        assert audit.ziwei_position == meta["ziwei_position"]
        assert audit.tianfu_position == meta["tianfu_position"]
