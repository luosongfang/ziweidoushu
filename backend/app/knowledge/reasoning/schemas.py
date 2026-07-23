"""Reasoning schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReasoningResult(BaseModel):
    dimension: str
    observations: list[str] = Field(default_factory=list)
    traditional_basis: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    call_trace: list[str] = Field(default_factory=list)


class PipelineResult(BaseModel):
    question_type: str
    traditional_analysis: list[str] = Field(default_factory=list)
    reasoning: list[ReasoningResult] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    safety_notice: str = ""
    prompt_preview: str = ""
    call_trace: list[str] = Field(default_factory=list)
    # V2 extensions (optional, backward compatible)
    scenario_name: str | None = None
    life_advisor: dict[str, Any] | None = None
    matrix_summary: dict[str, Any] | None = None
    engine_version: str = "1.1"
    # V2.1 advisor layer
    advisor_analysis: dict[str, Any] | None = None
    reflection_questions: list[str] = Field(default_factory=list)
    traditional_analysis_structured: dict[str, Any] | None = None
    # V3.2 intelligence layer
    theory_used: list[str] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    theory_route: dict[str, Any] | None = None
    selected_knowledge: list[dict[str, Any]] | None = None
    # V3.3 growth memory
    user_context: dict[str, Any] | None = None
    # V4.0 multi-theory
    theory_analysis: dict[str, Any] | None = None
    theory_conflicts: list[dict[str, Any]] | None = None
    theory_synthesis: dict[str, Any] | None = None
    # V4.1 life cycle
    life_timeline: dict[str, Any] | None = None
    # V5.0 decision intelligence
    decision_analysis: dict[str, Any] | None = None
    # V5.1 feedback / paths / citation
    decision_paths: dict[str, Any] | None = None
    knowledge_trace: dict[str, Any] | None = None
    decision_history_id: str | None = None


class LifeAdvisorResult(BaseModel):
    traditional_view: str = ""
    modern_view: str = ""
    strengths: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    growth_direction: list[str] = Field(default_factory=list)
    reflection_questions: list[str] = Field(default_factory=list)
    safety_notice: str = ""
    sources: list[dict[str, Any]] = Field(default_factory=list)
    call_trace: list[str] = Field(default_factory=list)
