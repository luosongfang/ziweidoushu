"""命宫身宫校准测试 — 仅 verified_professional。"""

from __future__ import annotations

import pytest

from app.ziwei.debug.classical_audit import run_classical_audit
from app.ziwei.debug.reference_manager import list_auto_test_charts
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.rules.cache import clear_rules_cache


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestMingShenFormula:
    def test_formula_doc_april_wei(self):
        """ALGORITHM 示例：农历四月未时 → 命戌身子。"""
        month = PalaceEngine.calc_month_palace_branch(4)
        assert month == 5  # 巳
        assert PalaceEngine.calc_ming_gong_branch(4, 7) == 10  # 戌
        assert PalaceEngine.calc_shen_gong_branch(4, 7) == 0  # 子

    @pytest.mark.parametrize("case", list_auto_test_charts(), ids=lambda c: c["id"])
    def test_verified_ming_shen(self, case):
        birth = case["birth"]
        audit = run_classical_audit(
            birth_date=birth["solar"],
            birth_time=birth["time"],
            gender=case["gender"],
            location=case.get("location") or birth.get("location"),
        )
        meta = case["meta"]
        assert audit.minggong == meta["minggong"]
        assert audit.shengong == meta["shengong"]
