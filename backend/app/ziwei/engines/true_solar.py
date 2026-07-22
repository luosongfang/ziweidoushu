"""真太阳时计算。"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

# 常用时区标准经度（东经）
TIMEZONE_MERIDIAN: dict[str, float] = {
    "Asia/Shanghai": 120.0,
    "Asia/Hong_Kong": 120.0,
    "Asia/Taipei": 120.0,
    "Asia/Urumqi": 90.0,
    "UTC": 0.0,
}

DEFAULT_MERIDIAN = 120.0  # 北京时间 UTC+8


def get_standard_meridian(timezone: str = "Asia/Shanghai") -> float:
    """获取时区采用的平太阳时标准经度（东经）。"""
    return TIMEZONE_MERIDIAN.get(timezone, DEFAULT_MERIDIAN)


def equation_of_time_minutes(day_of_year: int) -> float:
    """
    均时差（Equation of Time），单位：分钟。

    近似公式（ NOAA 简化模型），精度满足排盘需求。
    """
    b = 2 * math.pi * (day_of_year - 81) / 365.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def longitude_correction_minutes(longitude: float, standard_meridian: float) -> float:
    """
    经度时差修正：每差 1° 对应 4 分钟。
    真太阳时偏早（经度小于标准经度）为负。
    """
    return (longitude - standard_meridian) * 4.0


def apply_true_solar_time(
    dt: datetime,
    longitude: float,
    timezone: str = "Asia/Shanghai",
) -> tuple[datetime, dict[str, float]]:
    """
    平太阳时 → 真太阳时。

    公式：真太阳时 = 地方平太阳时 + 经度修正 + 均时差
    """
    standard_meridian = get_standard_meridian(timezone)
    lon_corr = longitude_correction_minutes(longitude, standard_meridian)
    eot = equation_of_time_minutes(dt.timetuple().tm_yday)
    total_minutes = lon_corr + eot

    true_dt = dt + timedelta(minutes=total_minutes)
    meta = {
        "standard_meridian": standard_meridian,
        "longitude": longitude,
        "longitude_correction_minutes": round(lon_corr, 2),
        "equation_of_time_minutes": round(eot, 2),
        "total_correction_minutes": round(total_minutes, 2),
    }
    return true_dt, meta
