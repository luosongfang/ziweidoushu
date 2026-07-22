"""命盘 Chart JSON Final 模型。"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from app.models.birth import BirthLocation
from app.models.palace import PalaceOutput
from app.models.star import FourTransformSummary


class ChartMetaOutput(BaseModel):
    name: str
    gender: Literal["male", "female"]
    mingGong: str
    shenGong: str
    mingGongGanZhi: str
    wuxingJu: str
    bureauNumber: int
    mingZhu: str
    shenZhu: str
    nayinElement: str


class LunarDetail(BaseModel):
    year: int
    month: int
    day: int
    isLeap: bool


class ShichenInfo(BaseModel):
    name: str
    range: str
    branch: str


class GanzhiInfo(BaseModel):
    year: str
    month: str
    day: str
    hour: str


class BirthInfoOutput(BaseModel):
    solar: str
    trueSolarTime: Optional[str] = None
    lunar: str
    lunarDetail: LunarDetail
    shichen: ShichenInfo
    ganzhi: GanzhiInfo
    location: Optional[BirthLocation] = None


class CombinationPattern(BaseModel):
    name: str
    category: str
    stars: list[str] = Field(default_factory=list)
    palaces: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    ai_prompt_ref: Optional[str] = None


class CombinationOutput(BaseModel):
    patterns: list[CombinationPattern] = Field(default_factory=list)


class FortuneOutput(BaseModel):
    daxianDirection: Literal["forward", "backward"]
    currentDaxian: Optional[dict[str, Any]] = None
    annualFortune: Optional[dict[str, Any]] = None
    monthlyFortune: Optional[dict[str, Any]] = None


class FeixingOutput(BaseModel):
    enabled: bool = False


class TraceOutput(BaseModel):
    traceId: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    rulesVersion: str = "2026.07.22"


class ChartOutput(BaseModel):
    """Chart JSON V1.0 Final — 与前端及 AI 引擎对齐。"""

    version: str = "1.0-final"
    school: str = "sanhe"
    rulesVersion: str = "2026.07.22"
    meta: ChartMetaOutput
    birth: BirthInfoOutput
    palaces: list[PalaceOutput]
    fourTransformSummary: Optional[FourTransformSummary] = None
    combinations: CombinationOutput = Field(default_factory=CombinationOutput)
    fortune: FortuneOutput
    feixing: FeixingOutput = Field(default_factory=FeixingOutput)
    trace: Optional[TraceOutput] = None


# 向后兼容：旧 API 使用的扁平 meta 结构
class LegacyChartMetaOutput(BaseModel):
    name: str
    gender: Literal["male", "female"]
    birthDate: str
    birthTime: str
    calendar: Literal["solar", "lunar"]
    lunarDate: str
    yearStemBranch: str
    monthStemBranch: str
    dayStemBranch: str
    hourStemBranch: str
    wuxingJu: str
    mingZhu: str
    shenZhu: str
    mingGong: str
    shenGong: str
    mingGongGanZhi: str
    nayinElement: str
    bureauNumber: int


class LegacyChartOutput(BaseModel):
    """Phase 1 兼容输出，供现有测试过渡。"""

    meta: LegacyChartMetaOutput
    palaces: list[PalaceOutput]
