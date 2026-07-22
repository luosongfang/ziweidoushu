"""出生信息输入模型（Final Architecture）。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class BirthLocation(BaseModel):
    country: str = "China"
    province: Optional[str] = None
    city: Optional[str] = None
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)


class BirthInput(BaseModel):
    """标准出生信息输入。"""

    name: str = Field(default="未命名命盘")
    gender: Literal["male", "female"]
    calendar_type: Literal["solar", "lunar"] = "solar"
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field(..., description="HH:mm")
    location: BirthLocation = Field(default_factory=BirthLocation)
    timezone: str = Field(default="Asia/Shanghai")

    @field_validator("time")
    @classmethod
    def validate_time_format(cls, value: str) -> str:
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("time 格式必须为 HH:mm")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("time 数值无效")
        return value

    def to_datetime(self) -> datetime:
        year, month, day = map(int, self.date.split("-"))
        hour, minute = map(int, self.time.split(":"))
        return datetime(year, month, day, hour, minute, 0)


class ChartGenerateRequest(BaseModel):
    """排盘 API 请求（兼容 ISO datetime 与 BirthInput 两种形式）。"""

    birth_datetime: datetime = Field(..., description="出生日期时间 ISO 8601")
    gender: Literal["male", "female"]
    calendar_type: Literal["solar", "lunar"] = "solar"
    timezone: str = "Asia/Shanghai"
    name: str = "未命名命盘"
    location: Optional[BirthLocation] = None

    @classmethod
    def from_birth_input(cls, birth: BirthInput) -> "ChartGenerateRequest":
        return cls(
            birth_datetime=birth.to_datetime(),
            gender=birth.gender,
            calendar_type=birth.calendar_type,
            timezone=birth.timezone,
            name=birth.name,
            location=birth.location,
        )
