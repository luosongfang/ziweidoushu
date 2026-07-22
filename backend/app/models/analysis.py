"""AI 分析请求/响应模型（Sprint 7）。"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.models.birth import BirthInput
from app.models.chart import ChartOutput


AnalysisType = Literal["overall", "palace", "daxian", "liunian"]
AnalysisMode = Literal["auto", "rules", "llm"]


class AnalysisGenerateRequest(BaseModel):
    """AI 分析请求 — 提供 chart 或 birth 之一。"""

    analysis_type: AnalysisType = "overall"
    palace_name: Optional[str] = Field(
        default=None,
        description="analysis_type=palace 时必填，如「命宫」",
    )
    chart: Optional[ChartOutput] = None
    birth: Optional[BirthInput] = None
    reference_date: Optional[str] = Field(
        default=None,
        description="运限参考日期 YYYY-MM-DD，默认当天",
    )
    mode: AnalysisMode = "auto"

    @model_validator(mode="after")
    def validate_input(self) -> "AnalysisGenerateRequest":
        if self.chart is None and self.birth is None:
            raise ValueError("必须提供 chart 或 birth 之一")
        if self.analysis_type == "palace" and not self.palace_name:
            raise ValueError("palace 分析必须指定 palace_name")
        return self


class AnalysisSection(BaseModel):
    title: str
    content: str
    sources: list[str] = Field(default_factory=list)


class RagChunkRef(BaseModel):
    id: str
    source: str
    category: str
    title: Optional[str] = None
    content: str
    score: float = 0.0


class AnalysisOutput(BaseModel):
    """AI 分析结果。"""

    version: str = "1.0"
    prompt_version: str = "v1"
    analysis_type: AnalysisType
    mode: Literal["rules", "llm"]
    sections: list[AnalysisSection] = Field(default_factory=list)
    result_text: str
    input_context: dict[str, Any] = Field(default_factory=dict)
    rag_chunks: list[RagChunkRef] = Field(default_factory=list)
    tokens_used: int = 0
    chart_summary: dict[str, Any] = Field(default_factory=dict)
