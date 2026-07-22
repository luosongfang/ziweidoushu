"""Sprint 2 — Calendar Engine 测试。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from app.models.birth import BirthLocation, ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.engines.calendar_engine import CalendarEngine, hour_to_shichen
from app.ziwei.engines.true_solar import (
    apply_true_solar_time,
    equation_of_time_minutes,
    get_standard_meridian,
    longitude_correction_minutes,
)

FIXTURES = Path(__file__).parent / "fixtures" / "reference_charts.json"


class TestTrueSolarMath:
    def test_standard_meridian_shanghai(self):
        assert get_standard_meridian("Asia/Shanghai") == 120.0

    def test_longitude_correction_shenzhen(self):
        corr = longitude_correction_minutes(114.0579, 120.0)
        assert corr == pytest.approx(-23.77, abs=0.01)

    def test_equation_of_time_range(self):
        for day in (1, 81, 172, 365):
            eot = equation_of_time_minutes(day)
            assert -20 <= eot <= 20

    def test_apply_true_solar_shenzhen(self):
        dt = datetime(1990, 5, 15, 14, 30, 0)
        true_dt, meta = apply_true_solar_time(dt, 114.0579)
        assert meta["longitude_correction_minutes"] == pytest.approx(-23.77, abs=0.01)
        assert true_dt < dt
        assert true_dt.hour == 14
        assert true_dt.minute < 30


class TestShichen:
    def test_wei_hour(self):
        idx, name, _ = hour_to_shichen(14, 30)
        assert idx == 7
        assert name == "未时"

    def test_zi_hour_late(self):
        idx, name, _ = hour_to_shichen(23, 30)
        assert idx == 0
        assert name == "子时"

    def test_zi_hour_early(self):
        idx, name, _ = hour_to_shichen(0, 30)
        assert idx == 0
        assert name == "子时"


class TestLunarConversion:
    def test_solar_to_lunar_1990(self):
        result = CalendarEngine.convert(datetime(1990, 5, 15, 14, 30))
        assert result.lunar_month == 4
        assert result.lunar_day == 21
        assert result.hour_branch == "未"
        assert result.year_ganzhi == "庚午"
        assert result.month_ganzhi == "辛巳"
        assert result.day_ganzhi == "庚辰"
        assert result.hour_ganzhi == "癸未"

    def test_without_longitude_no_correction(self):
        result = CalendarEngine.convert(datetime(1990, 5, 15, 14, 30))
        assert result.used_true_solar is False
        assert result.true_solar_datetime == result.clock_datetime

    def test_with_longitude_applies_correction(self):
        result = CalendarEngine.convert(
            datetime(1990, 5, 15, 14, 30),
            longitude=114.0579,
        )
        assert result.used_true_solar is True
        assert result.true_solar_datetime < result.clock_datetime
        assert result.correction_meta["total_correction_minutes"] < 0
        # 真太阳时修正后时柱不变（仍属未时）
        assert result.hour_ganzhi == "癸未"


class TestLiChunBoundary:
    """REF-02：立春节气与月柱边界。"""

    def test_month_before_li_chun_day(self):
        """1984-02-03 — 立春前一日，月柱乙丑。"""
        result = CalendarEngine.convert(datetime(1984, 2, 3, 12, 0))
        assert result.month_ganzhi == "乙丑"

    def test_month_on_li_chun_day(self):
        """1984-02-04 08:00 — 立春日，月柱丙寅。"""
        result = CalendarEngine.convert(datetime(1984, 2, 4, 8, 0))
        assert result.month_ganzhi == "丙寅"
        assert result.jie_qi == "立春"

    def test_is_before_li_chun_moment(self):
        """1984-02-04 08:00 — 在立春交节时刻之前。"""
        result = CalendarEngine.convert(datetime(1984, 2, 4, 8, 0))
        assert result.is_before_li_chun is True

    def test_ref02_female_chart(self):
        chart = ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(1984, 2, 4, 8, 0),
            gender="female",
        ))
        assert chart.birth.ganzhi.year == "甲子"
        assert chart.birth.ganzhi.month == "丙寅"
        assert chart.birth.ganzhi.day == "戊辰"
        assert chart.birth.ganzhi.hour == "丙辰"


class TestZiHourBoundary:
    """REF-03 / REF-06：子时边界。"""

    def test_ref03_late_zi_before_li_chun(self):
        """1984-02-03 23:30 — 立春前晚子时。"""
        result = CalendarEngine.convert(datetime(1984, 2, 3, 23, 30))
        assert result.year_ganzhi == "甲子"
        assert result.month_ganzhi == "乙丑"
        assert result.day_ganzhi == "丁卯"
        assert result.hour_branch == "子"
        assert result.hour_ganzhi == "壬子"
        assert result.shichen_name == "子时"

    def test_ref06_millennium_zi_hour(self):
        """2000-01-01 00:00 — 千禧早子时。"""
        result = CalendarEngine.convert(datetime(2000, 1, 1, 0, 0))
        assert result.year_ganzhi == "己卯"
        assert result.month_ganzhi == "丙子"
        assert result.day_ganzhi == "戊午"
        assert result.hour_branch == "子"
        assert result.hour_ganzhi == "壬子"
        assert result.shichen_name == "子时"

    def test_ref06_late_zi_previous_day(self):
        """2000-01-01 00:30 — 仍属子时。"""
        result = CalendarEngine.convert(datetime(2000, 1, 1, 0, 30))
        assert result.hour_branch == "子"
        assert result.hour_ganzhi == "壬子"


class TestReferenceCharts:
    """从 fixtures/reference_charts.json 加载基准盘。"""

    @pytest.fixture(scope="class")
    def ref_data(self):
        with open(FIXTURES, encoding="utf-8") as f:
            return json.load(f)

    @pytest.mark.parametrize("ref_id", ["REF-01", "REF-02", "REF-03", "REF-04", "REF-05", "REF-06"])
    def test_reference_chart(self, ref_data, ref_id):
        chart_spec = next(c for c in ref_data["charts"] if c["id"] == ref_id)
        inp = chart_spec["input"]
        exp = chart_spec["expected"]

        y, m, d = map(int, inp["date"].split("-"))
        hh, mm = map(int, inp["time"].split(":"))

        location = None
        if inp.get("longitude") is not None:
            location = BirthLocation(longitude=inp["longitude"])

        chart = ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(y, m, d, hh, mm),
            gender=inp["gender"],
            name=inp.get("name", "测试"),
            location=location,
            timezone=inp.get("timezone", "Asia/Shanghai"),
        ))

        if "ganzhi" in exp:
            assert chart.birth.ganzhi.year == exp["ganzhi"]["year"]
            assert chart.birth.ganzhi.month == exp["ganzhi"]["month"]
            assert chart.birth.ganzhi.day == exp["ganzhi"]["day"]
            assert chart.birth.ganzhi.hour == exp["ganzhi"]["hour"]

        if "mingGong" in exp:
            assert chart.meta.mingGong == exp["mingGong"]
        if "shenGong" in exp:
            assert chart.meta.shenGong == exp["shenGong"]
        if "wuxingJu" in exp:
            assert chart.meta.wuxingJu == exp["wuxingJu"]
        if "mingGongGanZhi" in exp:
            assert chart.meta.mingGongGanZhi == exp["mingGongGanZhi"]
        if "palaceBranches" in exp:
            assert [p.branch for p in chart.palaces] == exp["palaceBranches"]
        if "mingSanhe" in exp:
            assert chart.palaces[0].sanhe == exp["mingSanhe"]
        if "ziweiBranch" in exp:
            step = next(s for s in chart.trace.steps if s["engine"] == "star_placement")
            assert step["output"]["ziweiBranch"] == exp["ziweiBranch"]
        if "mainStarsByPalace" in exp:
            for palace, stars in exp["mainStarsByPalace"].items():
                p = next(x for x in chart.palaces if x.name == palace)
                assert [s.name for s in p.mainStars] == stars
        for field, attr in (
            ("auxStarsByPalace", "auxStars"),
            ("shaStarsByPalace", "shaStars"),
            ("zaStarsByPalace", "zaStars"),
        ):
            if field in exp:
                for palace, stars in exp[field].items():
                    p = next(x for x in chart.palaces if x.name == palace)
                    assert [s.name for s in getattr(p, attr)] == stars
        if "fourTransform" in exp:
            ft = chart.fourTransformSummary
            assert ft is not None
            assert ft.yearStem == exp["fourTransform"]["yearStem"]
            assert ft.lu.star == exp["fourTransform"]["lu"]["star"]
            assert ft.lu.palace == exp["fourTransform"]["lu"]["palace"]
            assert ft.ji.star == exp["fourTransform"]["ji"]["star"]
            assert ft.ji.palace == exp["fourTransform"]["ji"]["palace"]
        if "daxianDirection" in exp:
            assert chart.fortune.daxianDirection == exp["daxianDirection"]
        if "combinationNames" in exp:
            actual = sorted(p.name for p in chart.combinations.patterns)
            assert actual == exp["combinationNames"]

    def test_ref01_true_solar_time_recorded(self, ref_data):
        chart_spec = next(c for c in ref_data["charts"] if c["id"] == "REF-01")
        inp = chart_spec["input"]
        y, m, d = map(int, inp["date"].split("-"))
        hh, mm = map(int, inp["time"].split(":"))

        chart = ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(y, m, d, hh, mm),
            gender=inp["gender"],
            location=BirthLocation(longitude=inp["longitude"]),
        ))
        assert chart.birth.solar != chart.birth.trueSolarTime
