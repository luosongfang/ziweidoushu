"""Classical Rule Engine V1.0 测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_classical import ClassicalAccuracyGate, ClassicalEngine, DualEngineCompare
from app.ziwei_classical.bureau.five_element import calc_five_element_bureau
from app.ziwei_classical.engine import ClassicalEngineConfig
from app.ziwei_classical.stars.ziwei_system import load_ziwei_table, lookup_ziwei_branch
from app.ziwei.debug.reference_manager import load_chart


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


SC_C01 = {
    "solar": "1990-05-15",
    "time": "14:30",
    "gender": "male",
    "location": "深圳",
}


class TestSC_C01:
    def test_sc_c01_core_100(self):
        eng = ClassicalEngine()
        chart = eng.compute(
            birth_date=SC_C01["solar"],
            birth_time=SC_C01["time"],
            gender=SC_C01["gender"],
            location=SC_C01["location"],
        )
        assert chart.ming_gong["branch"] == "戌"
        assert chart.shen_gong["branch"] == "子"
        assert chart.bureau["bureau_name"] == "土五局"
        assert chart.ziwei["branch"] == "巳"
        assert chart.tianfu["branch"] == "亥"
        assert chart.fourteen_stars["紫微"] == "巳"
        assert chart.fourteen_stars["天府"] == "亥"
        assert chart.fourteen_stars["七杀"] == "巳"
        # 与黄金盘
        gold = load_chart("SC-C01")
        for star, info in (gold.get("fourteen_stars") or {}).items():
            br = info["branch"] if isinstance(info, dict) else info
            assert chart.fourteen_stars[star] == br, star

    def test_sc_c01_dual_engine_match(self):
        rep = DualEngineCompare().compare(
            birth_date=SC_C01["solar"],
            birth_time=SC_C01["time"],
            gender=SC_C01["gender"],
            location=SC_C01["location"],
        )
        assert rep["matched"] is True
        assert rep["ziwei"] == "PASS"
        assert rep["fourteen_stars"] == "PASS"


class TestZiweiTable:
    def test_table_150(self):
        table = load_ziwei_table()
        total = sum(len(b["days"]) for b in table["bureaus"].values())
        assert total == 150

    def test_lookup_not_formula_in_engine(self):
        # Classical 必须走表：土五局廿一 → 巳
        assert lookup_ziwei_branch(5, 21) == "巳"

    @pytest.mark.parametrize("bureau", [2, 3, 4, 5, 6])
    def test_all_days_present(self, bureau):
        for d in range(1, 31):
            assert lookup_ziwei_branch(bureau, d) in list("子丑寅卯辰巳午未申酉戌亥")


class TestFourteenAndBureau:
    def test_bureau_water_to_fire_names(self):
        # 命宫干支纳音 → 局名存在
        # 用 SC-C01 命戌 + 庚年 → 土五
        b = calc_five_element_bureau("庚", 10)  # 戌=10
        assert "局" in b["bureau_name"]

    def test_fourteen_count(self):
        chart = ClassicalEngine().compute(
            birth_date=SC_C01["solar"],
            birth_time=SC_C01["time"],
            location=SC_C01["location"],
        )
        assert len(chart.fourteen_stars) == 14
        assert len(chart.trace) >= 10


class TestEmptyPalace:
    def test_empty_ming_palace_allowed(self):
        chart = ClassicalEngine().compute(
            birth_date=SC_C01["solar"],
            birth_time=SC_C01["time"],
            location=SC_C01["location"],
        )
        ming = next(p for p in chart.palaces if p["is_ming_gong"])
        # SC-C01 命宫无主星
        assert ming["main_stars"] == []


class TestAuxStars:
    def test_lucky_evil_minor_present(self):
        chart = ClassicalEngine().compute(
            birth_date=SC_C01["solar"],
            birth_time=SC_C01["time"],
            location=SC_C01["location"],
        )
        for name in ("左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存"):
            assert name in chart.lucky_stars
            assert chart.lucky_stars[name].get("branch")
        for name in ("擎羊", "陀罗", "地空", "地劫"):
            assert name in chart.evil_stars
        for name in ("红鸾", "天喜", "天姚", "天刑", "孤辰", "寡宿", "华盖"):
            assert name in chart.minor_stars

    def test_trace_has_rule_fields(self):
        chart = ClassicalEngine().compute(
            birth_date=SC_C01["solar"],
            birth_time=SC_C01["time"],
            location=SC_C01["location"],
        )
        steps = {s["step"] for s in chart.trace}
        assert "ziwei_position" in steps
        assert "tianfu_position" in steps
        assert "lucky.左辅" in steps


class TestTianfuSchoolConfig:
    def test_opposite_differs_except_si_hai(self):
        eng_m = ClassicalEngine(ClassicalEngineConfig(tianfu_rule="yin_shen_mirror"))
        eng_o = ClassicalEngine(ClassicalEngineConfig(tianfu_rule="opposite"))
        # 紫微巳时镜像=对宫=亥，两派相同
        c1 = eng_m.compute(birth_date=SC_C01["solar"], birth_time=SC_C01["time"], location=SC_C01["location"])
        c2 = eng_o.compute(birth_date=SC_C01["solar"], birth_time=SC_C01["time"], location=SC_C01["location"])
        assert c1.tianfu["branch"] == c2.tianfu["branch"] == "亥"


class TestClassicalGate:
    def test_block_below_98(self):
        gate = ClassicalAccuracyGate(min_score=98)
        out = gate.evaluate(accuracy_score=90)
        assert out["allowed_for_ai"] is False
        assert "校准" in (out["message"] or "")

    def test_pass_at_100(self):
        out = ClassicalAccuracyGate().evaluate(accuracy_score=100)
        assert out["allowed_for_ai"] is True
