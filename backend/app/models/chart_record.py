"""命盘持久化模型（Sprint 8）。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.birth import BirthInput
from app.models.chart import ChartOutput


class ChartSaveRequest(BaseModel):
    """保存命盘请求。"""

    birth: BirthInput
    reference_date: Optional[str] = None
    chart: Optional[ChartOutput] = None


class ChartRecordSummary(BaseModel):
    id: UUID
    name: str
    birth_datetime: datetime
    gender: Literal["male", "female"]
    ming_gong: str
    wuxing_ju: str
    created_at: datetime


class ChartRecordOutput(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    birth_datetime: datetime
    gender: Literal["male", "female"]
    calendar_type: Literal["solar", "lunar"]
    timezone: str
    chart_data: ChartOutput
    created_at: datetime
    updated_at: datetime


class AnalysisRecordSummary(BaseModel):
    id: UUID
    chart_id: UUID
    analysis_type: str
    palace_name: Optional[str] = None
    preview: str = Field(description="解读摘要，前 120 字")
    created_at: datetime


class AnalysisRecordOutput(BaseModel):
    id: UUID
    user_id: UUID
    chart_id: UUID
    analysis_type: str
    palace_name: Optional[str] = None
    prompt_version: str
    result_text: str
    tokens_used: int
    created_at: datetime


class PersistAnalysisRequest(BaseModel):
    """持久化 AI 解读请求。"""

    chart_id: UUID
    analysis_type: str = "overall"
    palace_name: Optional[str] = None
    reference_date: Optional[str] = None
    mode: str = "auto"
