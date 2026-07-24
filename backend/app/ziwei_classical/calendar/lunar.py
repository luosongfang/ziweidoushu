"""Classical calendar — 农历/干支/节气（复用现有历法引擎，输出可 trace）。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei_classical.validator.rule_trace import RuleTrace
from app.ziwei_engine.calendar.lunar_converter import LunarConverter


@dataclass
class ClassicalCalendarResult:
    solar_date: str
    birth_time: str
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool
    jie_qi: str
    month_ling: int  # 月令=农历月
    year_ganzhi: str
    month_ganzhi: str
    day_ganzhi: str
    hour_ganzhi: str
    year_stem: str
    year_branch: str
    shichen_name: str
    shichen_index: int
    used_true_solar: bool
    true_solar_iso: str
    longitude: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def convert_calendar(
    *,
    birth_date: str,
    birth_time: str,
    calendar_type: str = "solar",
    location: str | None = None,
    is_leap_month: bool = False,
    trace: RuleTrace | None = None,
) -> ClassicalCalendarResult:
    """出生资料 → 农历 + 四柱 + 节气。"""
    solar = birth_date
    if calendar_type == "lunar":
        solar = LunarConverter.lunar_to_solar(birth_date, is_leap=is_leap_month)

    longitude = LunarConverter.parse_location(location)
    lunar, true_dt = LunarConverter.convert(solar, birth_time, location)
    cal = CalendarEngine.convert(true_dt, longitude=longitude)

    result = ClassicalCalendarResult(
        solar_date=solar,
        birth_time=birth_time,
        lunar_year=cal.lunar_year,
        lunar_month=cal.lunar_month,
        lunar_day=cal.lunar_day,
        is_leap_month=cal.is_leap_month,
        jie_qi=getattr(cal, "jie_qi", "") or "",
        month_ling=cal.lunar_month,
        year_ganzhi=cal.year_ganzhi,
        month_ganzhi=cal.month_ganzhi,
        day_ganzhi=cal.day_ganzhi,
        hour_ganzhi=cal.hour_ganzhi,
        year_stem=cal.year_stem,
        year_branch=cal.year_branch,
        shichen_name=cal.shichen_name,
        shichen_index=cal.shichen_index,
        used_true_solar=cal.used_true_solar,
        true_solar_iso=true_dt.isoformat(),
        longitude=longitude,
    )
    if trace is not None:
        trace.add(
            step="calendar",
            rule="LunarConverter + CalendarEngine（节气换月、子初换日）",
            inputs={
                "birth_date": birth_date,
                "birth_time": birth_time,
                "calendar_type": calendar_type,
                "location": location,
            },
            outputs=result.to_dict(),
            source="ziwei_classical.calendar",
        )
    return result


# 模块别名文件将 re-export
def parse_datetime(birth_date: str, birth_time: str) -> datetime:
    h, m = birth_time.split(":")[:2]
    y, mo, d = birth_date.split("-")
    return datetime(int(y), int(mo), int(d), int(h), int(m))
