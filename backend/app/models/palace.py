"""宫位数据模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.star import StarOutput


class DaXianOutput(BaseModel):
    startAge: int
    endAge: int


class PalaceAnalysisTags(BaseModel):
    stars: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PalaceFourTransform(BaseModel):
    incoming: list[str] = Field(default_factory=list)
    outgoing: list[str] = Field(default_factory=list)


class PalaceOutput(BaseModel):
    name: str
    branch: str
    ganzhi: str = ""
    position: int = Field(ge=1, le=12)
    opposite: str = ""
    sanhe: list[str] = Field(default_factory=list)
    isMingGong: bool = False
    isShenGong: bool = False
    mainStars: list[StarOutput] = Field(default_factory=list)
    auxStars: list[StarOutput] = Field(default_factory=list)
    shaStars: list[StarOutput] = Field(default_factory=list)
    zaStars: list[StarOutput] = Field(default_factory=list)
    fourTransform: PalaceFourTransform = Field(default_factory=PalaceFourTransform)
    daxian: DaXianOutput
    analysis_tags: PalaceAnalysisTags = Field(default_factory=PalaceAnalysisTags)
