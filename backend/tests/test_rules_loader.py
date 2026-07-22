"""Sprint 1 规则加载器测试。"""

import pytest

from app.ziwei.exceptions import RuleNotFoundError
from app.ziwei.rules.loader import RulesLoader
from app.ziwei.rules.seed_generator import build_all_rules, calc_ziwei_branch_index
from app.ziwei.constants import EARTHLY_BRANCHES


class TestRulesCache:
    def test_build_all_rules_complete(self):
        rules = build_all_rules()
        assert len(rules["nayin_rules"]) == 60
        assert len(rules["ziwei_position_rules"]) == 180  # 6×30
        assert len(rules["four_transform_rules"]) == 10
        assert len(rules["daxian_rules"]) == 4
        assert len(rules["brightness_rules"]) == 168  # 14×12
        assert len(rules["star_combination_rules"]) >= 20
        assert len(rules["palace_meaning_rules"]) == 12
        assert len(rules["star_lookup_rules"]) >= 5

    def test_rules_version(self):
        assert RulesLoader.rules_version() == "2026.07.22"


class TestNayinRules:
    def test_bingxu_tu_wuju(self):
        rule = RulesLoader.get_nayin("丙", "戌")
        assert rule.nayin == "屋上土"
        assert rule.element == "土"
        assert rule.bureau_number == 5

    def test_get_bureau(self):
        element, number, name = RulesLoader.get_bureau("丙", "戌")
        assert element == "土"
        assert number == 5
        assert name == "土五局"

    def test_invalid_ganzhi_raises(self):
        with pytest.raises(RuleNotFoundError):
            RulesLoader.get_nayin("X", "戌")


class TestFourTransformRules:
    def test_geng_year(self):
        rule = RulesLoader.get_four_transform("庚")
        assert rule.lu_star == "太阳"
        assert rule.quan_star == "武曲"
        assert rule.ke_star == "太阴"
        assert rule.ji_star == "天同"

    def test_all_stems(self):
        stems = "甲乙丙丁戊己庚辛壬癸"
        for stem in stems:
            rule = RulesLoader.get_four_transform(stem)
            assert rule.lu_star and rule.ji_star


class TestDaxianRules:
    def test_yang_male_forward(self):
        rule = RulesLoader.get_daxian_rule("male", "庚")
        assert rule.direction == "forward"

    def test_yin_male_backward(self):
        rule = RulesLoader.get_daxian_rule("male", "乙")
        assert rule.direction == "backward"

    def test_yin_female_forward(self):
        rule = RulesLoader.get_daxian_rule("female", "乙")
        assert rule.direction == "forward"


class TestZiweiPositionRules:
    def test_day21_bureau5(self):
        branch = RulesLoader.get_ziwei_position(5, 21)
        idx = EARTHLY_BRANCHES.index(branch)
        expected_idx = calc_ziwei_branch_index(21, 5)
        assert idx == expected_idx

    def test_all_bureaus_30_days(self):
        for bureau in (2, 3, 4, 5, 6):
            for day in range(1, 31):
                branch = RulesLoader.get_ziwei_position(bureau, day)
                assert branch in EARTHLY_BRANCHES


class TestBrightnessRules:
    def test_ziwei_miao_at_wu(self):
        b = RulesLoader.get_brightness("紫微", "午")
        assert b == "庙"

    def test_taiyang_xian_at_zi(self):
        b = RulesLoader.get_brightness("太阳", "子")
        assert b == "陷"


class TestStarPlacementRules:
    def test_star_placement_rules_count(self):
        rules = RulesLoader.get_star_placement_rules("main_star")
        assert len(rules) == 14
        aux = RulesLoader.get_star_placement_rules("aux_star")
        assert len(aux) == 7
        sha = RulesLoader.get_star_placement_rules("sha_star")
        assert len(sha) == 6

    def test_star_lookup_rules(self):
        lookup = RulesLoader.get_star_lookup("禄存")
        assert lookup is not None
        assert lookup["mapping"]["庚"] == "申"

    def test_tianji_relative_to_ziwei(self):
        rules = RulesLoader.get_star_placement_rules("main_star")
        tianji = next(r for r in rules if r["star_name"] == "天机")
        assert tianji["base_star"] == "紫微"
        assert tianji["direction"] == "backward"
        assert tianji["offset"] == 1


class TestCombinationRules:
    def test_has_zifu_combo(self):
        combos = RulesLoader.get_star_combinations()
        names = [c["combination_name"] for c in combos]
        assert "紫府同宫" in names
        assert "杀破狼" in names


class TestPalaceMeaningRules:
    def test_ming_gong(self):
        row = RulesLoader.get_palace_meaning("命宫")
        assert row is not None
        assert row["keyword"] == "自我"
