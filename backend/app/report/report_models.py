"""Report API schemas — V1.3。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReportCreateRequest(BaseModel):
    chart_id: str
    report_type: str = Field(default="life_profile", pattern="^(life_profile|six_dimension|stage_growth)$")


class ReportCreateResponse(BaseModel):
    report_id: str
    summary: str
    report_sections: dict[str, Any]
    knowledge_trace: dict[str, Any] | None = None
    safety_notice: str = ""


class ReportSummaryItem(BaseModel):
    id: str
    chart_id: str | None = None
    report_type: str
    summary: str
    engine_version: str
    created_at: str


class ReportDetailResponse(BaseModel):
    id: str
    chart_id: str | None = None
    report_type: str
    engine_version: str
    summary: str
    report_sections: dict[str, Any]
    knowledge_trace: dict[str, Any] | None = None
    safety_notice: str = ""
    created_at: str


class ReportFeedbackRequest(BaseModel):
    report_id: str
    helpful: bool = True
    feedback_type: str = "general"
    comment: str = ""


class ReportFeedbackResponse(BaseModel):
    id: str
    success: bool = True


class GrowthProfileResponse(BaseModel):
    history: list[dict[str, Any]] = Field(default_factory=list)
    focus_topics: list[str] = Field(default_factory=list)
    goals: list[dict[str, Any]] = Field(default_factory=list)
    advisor_suggestions: list[str] = Field(default_factory=list)
    continuity_message: str = ""
