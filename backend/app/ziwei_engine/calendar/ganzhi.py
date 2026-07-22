"""干支计算 — 年/月/日/时四柱。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.ziwei.engines.calendar_engine import CalendarEngine


@dataclass(frozen=True)
class GanzhiResult:
    """四柱干支结果。"""

    year_gan: str
    year_zhi: str
    month_gan: str
    month_zhi: str
    day_gan: str
    day_zhi: str
    hour_gan: str
    hour_zhi: str

    @property
    def year_ganzhi(self) -> str:
        return f"{self.year_gan}{self.year_zhi}"

    @property
    def month_ganzhi(self) -> str:
        return f"{self.month_gan}{self.month_zhi}"

    @property
    def day_ganzhi(self) -> str:
        return f"{self.day_gan}{self.day_zhi}"

    @property
    def hour_ganzhi(self) -> str:
        return f"{self.hour_gan}{self.hour_zhi}"

    def to_dict(self) -> dict[str, str]:
        return {
            "year_gan": self.year_gan,
            "year_zhi": self.year_zhi,
            "month_gan": self.month_gan,
            "month_zhi": self.month_zhi,
            "day_gan": self.day_gan,
            "day_zhi": self.day_zhi,
            "hour_gan": self.hour_gan,
            "hour_zhi": self.hour_zhi,
        }


class GanzhiCalculator:
    """干支计算器 — 封装 CalendarEngine 四柱输出。"""

    @classmethod
    def calculate(
        cls,
        dt: datetime,
        longitude: float | None = None,
        timezone: str = "Asia/Shanghai",
    ) -> GanzhiResult:
        cal = CalendarEngine.convert(dt, longitude=longitude, timezone=timezone)
        return GanzhiResult(
            year_gan=cal.year_stem,
            year_zhi=cal.year_branch,
            month_gan=cal.month_stem,
            month_zhi=cal.month_branch,
            day_gan=cal.day_stem,
            day_zhi=cal.day_branch,
            hour_gan=cal.hour_stem,
            hour_zhi=cal.hour_branch,
        )
