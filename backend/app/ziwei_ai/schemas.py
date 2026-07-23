"""紫微AI 数据结构。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QuestionRoute(BaseModel):
    type: str
    related_palaces: list[str] = Field(default_factory=list)
    keywords_hit: list[str] = Field(default_factory=list)


class PalaceFocus(BaseModel):
    name: str
    stars: list[str] = Field(default_factory=list)
    transformations: list[str] = Field(default_factory=list)


class RuleAnalysis(BaseModel):
    traditional_analysis: str
    modern_interpretation: str
    strengths: list[str] = Field(default_factory=list)
    focused_palaces: list[PalaceFocus] = Field(default_factory=list)
    knowledge_snippets: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    chartData: dict[str, Any] | str = Field(
        ...,
        description="命盘 JSON 对象，或简要文本摘要",
    )
    question: str = Field(..., min_length=1, description="用户问题")


class AnalyzeResponse(BaseModel):
    success: bool
    category: str | None = None
    related_palaces: list[str] = Field(default_factory=list)
    report: str | None = None
    model: str | None = None
    error: str | None = None
