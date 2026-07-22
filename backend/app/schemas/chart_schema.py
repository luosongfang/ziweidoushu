"""Phase 2 命盘 API Schema。"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ChartCreateRequest(BaseModel):
    """POST /api/chart/create 请求体。"""

    name: str = Field(default="测试用户", max_length=64)
    gender: Literal["male", "female"] = "male"
    solar_date: str = Field(..., description="YYYY-MM-DD", examples=["1990-05-20"])
    time: str = Field(..., description="HH:mm", examples=["14:30"])
    location: Optional[str] = Field(default=None, examples=["北京"])
    persist: bool = Field(default=True, description="是否写入 Supabase 数据库")
    user_id: Optional[str] = Field(default=None, description="关联用户 ID（登录后传入）")
    reference_year: Optional[int] = None

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("time 格式必须为 HH:mm")
        return value


class BirthInfo(BaseModel):
    solar: str
    lunar: str
    lunar_detail: dict[str, Any]
    year_gan: str
    year_zhi: str
    ganzhi: dict[str, str]
    shichen: str


class ChartInfo(BaseModel):
    ming_gong: str
    shen_gong: str
    five_element: str
    five_element_detail: dict[str, Any]
    ming_zhu: str
    shen_zhu: str
    ziwei: dict[str, Any]
    tianfu: dict[str, Any]
    main_stars: list[dict[str, Any]]
    lucky_stars: list[dict[str, Any]]
    evil_stars: list[dict[str, Any]]
    four_hua: dict[str, Any]
    daxian_direction: str
    daxian_ranges: list[dict[str, Any]]
    liu_nian: dict[str, Any]
    palaces: list[dict[str, Any]]


class ChartCreateResponse(BaseModel):
    """Phase 2 标准命盘响应。"""

    name: str
    gender: str
    birth: BirthInfo
    chart: ChartInfo
    engine_version: str = "1.0"
    rules_version: str
    chart_id: Optional[str] = None
    birth_profile_id: Optional[str] = None
