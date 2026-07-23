"""Data models / aliases for theory dispatch optimization (no LLM)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Canonical weight-table names (API / theory_dispatch_weights)
_WEIGHT_ALIASES = {
    "三合": "sanhe",
    "三合派": "sanhe",
    "sanhe": "sanhe",
    "四化": "four_transform",
    "sihua": "four_transform",
    "four_transform": "four_transform",
    "飞星": "feixing",
    "feixing": "feixing",
    "古诀": "classic_formula",
    "格局": "classic_formula",
    "classic_formula": "classic_formula",
}

# Map weight-table name → TheoryDispatcher theory_type
_DISPATCH_TYPE = {
    "sanhe": "sanhe",
    "four_transform": "sihua",
    "feixing": "feixing",
    "classic_formula": "classic_formula",
}

# Map dispatcher / stats name → weight-table name
_FROM_DISPATCH = {
    "sanhe": "sanhe",
    "sihua": "four_transform",
    "four_transform": "four_transform",
    "feixing": "feixing",
    "classic_formula": "classic_formula",
}

_SCENARIO_ALIASES = {
    "career": "career",
    "career_switch": "career",
    "entrepreneurship": "entrepreneurship",
    "wealth": "wealth",
    "investment_decision": "wealth",
    "relationship": "relationship",
    "relationship_choice": "relationship",
    "marriage": "relationship",
    "study": "study",
    "life_stage": "life_transition",
    "life_transition": "life_transition",
    "personality": "career",
    "general": "career",
}

WEIGHT_MIN = 0.1
WEIGHT_MAX = 1.0
FEEDBACK_NEUTRAL = 50.0
VERSION = "5.6.0"


def normalize_theory(name: str) -> str:
    key = (name or "").strip()
    return _WEIGHT_ALIASES.get(key, _WEIGHT_ALIASES.get(key.lower(), key or "sanhe"))


def to_dispatch_type(weight_name: str) -> str:
    return _DISPATCH_TYPE.get(normalize_theory(weight_name), normalize_theory(weight_name))


def from_dispatch_type(theory_type: str) -> str:
    key = (theory_type or "").strip().lower()
    return _FROM_DISPATCH.get(key, normalize_theory(theory_type))


def normalize_scenario(name: str) -> str:
    key = (name or "").strip()
    return _SCENARIO_ALIASES.get(key, key or "career")


def clamp_weight(value: float) -> float:
    return max(WEIGHT_MIN, min(WEIGHT_MAX, float(value)))


@dataclass
class TheoryWeight:
    scenario: str
    theory_system: str
    base_weight: float
    dynamic_weight: float
    success_count: int = 0
    feedback_score: float = FEEDBACK_NEUTRAL
    version: str = VERSION
    id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "scenario": self.scenario,
            "theory_system": self.theory_system,
            "base_weight": self.base_weight,
            "dynamic_weight": self.dynamic_weight,
            "success_count": self.success_count,
            "feedback_score": self.feedback_score,
            "version": self.version,
        }


@dataclass
class DynamicRoute:
    scenario: str
    theories: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"scenario": self.scenario, "theories": self.theories}
