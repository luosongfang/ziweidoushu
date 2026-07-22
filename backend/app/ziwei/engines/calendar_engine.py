"""历法引擎：公历转农历、四柱、真太阳时、时辰。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lunar_python import Lunar, Solar

from app.ziwei.constants import (
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    SHICHEN_NAMES,
    SHICHEN_RANGES,
)
from app.ziwei.engines.true_solar import apply_true_solar_time


@dataclass(frozen=True)
class CalendarResult:
    """历法引擎输出。"""

    # 输入
    clock_datetime: datetime
    timezone: str = "Asia/Shanghai"
    longitude: float | None = None

    # 真太阳时
    true_solar_datetime: datetime = field(default_factory=datetime.now)
    correction_meta: dict[str, float] = field(default_factory=dict)
    used_true_solar: bool = False

    # 农历
    lunar_year: int = 0
    lunar_month: int = 0
    lunar_day: int = 0
    is_leap_month: bool = False
    lunar_year_cn: str = ""
    lunar_month_cn: str = ""
    lunar_day_cn: str = ""

    # 四柱
    year_stem: str = ""
    year_branch: str = ""
    month_stem: str = ""
    month_branch: str = ""
    day_stem: str = ""
    day_branch: str = ""
    hour_stem: str = ""
    hour_branch: str = ""
    year_ganzhi: str = ""
    month_ganzhi: str = ""
    day_ganzhi: str = ""
    hour_ganzhi: str = ""

    # 时辰
    shichen_index: int = 0
    shichen_name: str = ""
    shichen_range: str = ""

    # 节气（Sprint 2）
    jie_qi: str = ""
    is_before_li_chun: bool = False

    @property
    def solar_datetime(self) -> datetime:
        """向后兼容：返回用于排盘的实际时间。"""
        return self.true_solar_datetime


class CalendarEngine:
    """
    Calendar Engine — Sprint 2 完整实现。

    规则（lunar_python）：
    - 年以立春为界
    - 月以节气为界
    - 时柱按真太阳时（有经度时）或钟面时间计算
    - 含早/晚子时处理
    """

    @staticmethod
    def convert(
        dt: datetime,
        longitude: float | None = None,
        timezone: str = "Asia/Shanghai",
        use_true_solar: bool = True,
    ) -> CalendarResult:
        """
        公历日期时间 → 农历 + 四柱 + 时辰。

        Parameters
        ----------
        dt : 出生地钟面时间（地方平太阳时）
        longitude : 出生地经度（东经），提供且 use_true_solar 时启用真太阳时
        timezone : IANA 时区，用于确定标准经度
        use_true_solar : 是否应用真太阳时修正
        """
        correction_meta: dict[str, Any] = {}
        used_true_solar = False

        if longitude is not None and use_true_solar:
            true_dt, correction_meta = apply_true_solar_time(dt, longitude, timezone)
            used_true_solar = True
        else:
            true_dt = dt

        solar = Solar.fromYmdHms(
            true_dt.year, true_dt.month, true_dt.day,
            true_dt.hour, true_dt.minute, true_dt.second,
        )
        lunar: Lunar = solar.getLunar()
        shichen_index = EARTHLY_BRANCHES.index(lunar.getTimeZhi())

        # 立春判断（以排盘所用时刻 vs 当年立春交节时刻）
        jie_qi = lunar.getJieQi() or ""
        li_chun_solar = lunar.getJieQiTable().get("立春")
        is_before_li_chun = False
        if li_chun_solar is not None:
            li_chun_dt = datetime(
                li_chun_solar.getYear(),
                li_chun_solar.getMonth(),
                li_chun_solar.getDay(),
                li_chun_solar.getHour(),
                li_chun_solar.getMinute(),
                li_chun_solar.getSecond(),
            )
            is_before_li_chun = true_dt < li_chun_dt

        return CalendarResult(
            clock_datetime=dt,
            timezone=timezone,
            longitude=longitude,
            true_solar_datetime=true_dt,
            correction_meta=correction_meta,
            used_true_solar=used_true_solar,
            lunar_year=lunar.getYear(),
            lunar_month=abs(lunar.getMonth()),
            lunar_day=lunar.getDay(),
            is_leap_month=lunar.getMonth() < 0,
            lunar_year_cn=lunar.getYearInChinese(),
            lunar_month_cn=lunar.getMonthInChinese(),
            lunar_day_cn=lunar.getDayInChinese(),
            year_stem=lunar.getYearGan(),
            year_branch=lunar.getYearZhi(),
            month_stem=lunar.getMonthGan(),
            month_branch=lunar.getMonthZhi(),
            day_stem=lunar.getDayGan(),
            day_branch=lunar.getDayZhi(),
            hour_stem=lunar.getTimeGan(),
            hour_branch=lunar.getTimeZhi(),
            year_ganzhi=lunar.getYearInGanZhi(),
            month_ganzhi=lunar.getMonthInGanZhi(),
            day_ganzhi=lunar.getDayInGanZhi(),
            hour_ganzhi=lunar.getTimeInGanZhi(),
            shichen_index=shichen_index,
            shichen_name=SHICHEN_NAMES[shichen_index],
            shichen_range=SHICHEN_RANGES[shichen_index],
            jie_qi=jie_qi,
            is_before_li_chun=is_before_li_chun,
        )


def hour_to_shichen(hour: int, minute: int = 0) -> tuple[int, str, str]:
    """
    24 小时制 → 时辰索引（辅助函数）。

    注意：排盘时柱以 CalendarEngine + lunar_python 为准（含真太阳时与早/晚子时）。
    """
    total_minutes = hour * 60 + minute
    if total_minutes >= 23 * 60 or total_minutes < 1 * 60:
        index = 0
    else:
        index = ((hour - 1) // 2) + 1
        if index > 11:
            index = 11
    return index, SHICHEN_NAMES[index], SHICHEN_RANGES[index]


def stem_branch_at_palace(year_stem: str, branch_index: int) -> str:
    """五虎遁：年干 + 宫位地支 → 宫位干支。"""
    from app.ziwei.constants import YEAR_STEM_TO_YIN_MONTH_STEM, YIN_BRANCH_INDEX

    yin_stem = YEAR_STEM_TO_YIN_MONTH_STEM[year_stem]
    yin_stem_index = HEAVENLY_STEMS.index(yin_stem)
    offset = (branch_index - YIN_BRANCH_INDEX + 12) % 12
    palace_stem = HEAVENLY_STEMS[(yin_stem_index + offset) % 10]
    return palace_stem + EARTHLY_BRANCHES[branch_index]


# 向后兼容
LunarInfo = CalendarResult


def solar_to_lunar(dt: datetime, longitude: float | None = None) -> CalendarResult:
    return CalendarEngine.convert(dt, longitude=longitude)
