"""Advisor V2.1 schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AdvisorResult(BaseModel):
    dimension: str = ""
    strengths: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    growth: str = ""
    suggestions: list[str] = Field(default_factory=list)
    reflection_questions: list[str] = Field(default_factory=list)
    safety_notice: str = ""
    life_dimension: str = ""
    growth_direction: list[str] = Field(default_factory=list)
    action_plan: list[str] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    call_trace: list[str] = Field(default_factory=list)

    def as_advisor_analysis(self) -> dict[str, Any]:
        return {
            "life_dimension": self.life_dimension or self.dimension,
            "strengths": self.strengths,
            "challenges": self.challenges,
            "growth_direction": self.growth_direction or ([self.growth] if self.growth else []),
            "action_plan": self.action_plan or self.suggestions,
            "reflection_questions": self.reflection_questions,
            "safety_notice": self.safety_notice,
        }
