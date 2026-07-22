"""公历转农历 — 基于 lunar_python。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.ziwei.engines.calendar_engine import CalendarEngine


@dataclass(frozen=True)
class LunarDate:
    """农历日期结构。"""

    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap: bool
    lunar_text: str = ""


class LunarConverter:
    """公历 → 农历转换器。"""

    # 常用城市经度（东经），用于真太阳时
    CITY_LONGITUDE: dict[str, float] = {
        "北京": 116.4074,
        "上海": 121.4737,
        "广州": 113.2644,
        "深圳": 114.0579,
        "成都": 104.0665,
        "杭州": 120.1551,
    }

    @classmethod
    def parse_location(cls, location: str | None) -> float | None:
        if not location:
            return None
        location = location.strip()
        for city, lon in cls.CITY_LONGITUDE.items():
            if city in location:
                return lon
        return None

    @classmethod
    def convert(
        cls,
        solar_date: str,
        time: str,
        location: str | None = None,
        timezone: str = "Asia/Shanghai",
    ) -> tuple[LunarDate, datetime]:
        """
        转换公历日期时间。

        Parameters
        ----------
        solar_date : YYYY-MM-DD
        time : HH:mm
        location : 城市名或地址，用于真太阳时经度
        """
        year, month, day = map(int, solar_date.split("-"))
        hour, minute = map(int, time.split(":"))
        dt = datetime(year, month, day, hour, minute, 0)
        longitude = cls.parse_location(location)

        result = CalendarEngine.convert(dt, longitude=longitude, timezone=timezone)
        lunar = LunarDate(
            lunar_year=result.lunar_year,
            lunar_month=result.lunar_month,
            lunar_day=result.lunar_day,
            is_leap=result.is_leap_month,
            lunar_text=f"{result.lunar_year_cn}年{result.lunar_month_cn}{result.lunar_day_cn}",
        )
        return lunar, result.true_solar_datetime
