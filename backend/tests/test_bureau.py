"""Sprint 3 — Bureau Engine 测试。"""

from __future__ import annotations

import pytest

from app.ziwei.constants import ELEMENT_TO_JU_NAME, NAYIN_TO_BUREAU
from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei.rules.loader import RulesLoader


class TestBureauFromMingGong:
    def test_bingxu_tu_wuju(self):
        result = BureauEngine.compute("庚", 10)
        assert result.ming_gong_ganzhi == "丙戌"
        assert result.bureau_name == "土五局"
        assert result.nayin == "屋上土"
        assert result.nayin_element == "土"
        assert result.bureau_number == 5

    def test_dinghai_tu_wuju(self):
        """REF-04：1985-03-08 06:00 女。"""
        result = BureauEngine.compute("乙", 11)
        assert result.ming_gong_ganzhi == "丁亥"
        assert result.bureau_name == "土五局"
        assert result.nayin == "屋上土"

    def test_guichou_mu_sanju(self):
        """REF-05：1992-06-15 10:00 男。"""
        result = BureauEngine.compute("壬", 1)
        assert result.ming_gong_ganzhi == "癸丑"
        assert result.bureau_name == "木三局"
        assert result.nayin == "桑柘木"

    def test_compute_for_ganzhi(self):
        result = BureauEngine.compute_for_ganzhi("甲子")
        assert result.bureau_name == "金四局"
        assert result.nayin == "海中金"


class TestAllFiveBureaus:
    @pytest.mark.parametrize(
        "ganzhi,expected_name,expected_number",
        [
            ("丙子", "水二局", 2),
            ("戊辰", "木三局", 3),
            ("甲子", "金四局", 4),
            ("丙戌", "土五局", 5),
            ("丙寅", "火六局", 6),
        ],
    )
    def test_five_elements(self, ganzhi, expected_name, expected_number):
        result = BureauEngine.compute_for_ganzhi(ganzhi)
        assert result.bureau_name == expected_name
        assert result.bureau_number == expected_number


class TestNayinRulesConsistency:
    """确保 RulesLoader 与 constants 纳音表一致。"""

    def test_all_nayin_rules_match_constants(self):
        cache = RulesLoader._cache()
        for row in cache["nayin_rules"]:
            ganzhi = row["heavenly_stem"] + row["earthly_branch"]
            assert ganzhi in NAYIN_TO_BUREAU
            element, number = NAYIN_TO_BUREAU[ganzhi]
            assert row["element"] == element
            assert row["bureau_number"] == number
            assert ELEMENT_TO_JU_NAME[element] == RulesLoader.get_bureau(
                row["heavenly_stem"], row["earthly_branch"]
            )[2]

    def test_sixty_nayin_complete(self):
        assert len(RulesLoader._cache()["nayin_rules"]) == 60

    def test_rules_version_in_result(self):
        result = BureauEngine.compute("庚", 10)
        assert result.rules_version == "2026.07.22"
