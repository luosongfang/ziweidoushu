"""Knowledge Core V4.1 — Dynamic Life Cycle Engine package."""

from app.knowledge.lifecycle.annual_engine import AnnualEngine
from app.knowledge.lifecycle.cycle_calculator import CycleCalculator
from app.knowledge.lifecycle.fortune_timeline import FortuneTimeline
from app.knowledge.lifecycle.lifecycle_advisor import LifecycleAdvisor
from app.knowledge.lifecycle.stage_analyzer import StageAnalyzer

__all__ = [
    "CycleCalculator",
    "FortuneTimeline",
    "AnnualEngine",
    "StageAnalyzer",
    "LifecycleAdvisor",
    "LifeCycleEngine",
]


class LifeCycleEngine:
    """Facade: profile → major limits → stage → annual → timeline → advice."""

    @classmethod
    def analyze(
        cls,
        chart: dict | None = None,
        *,
        question_type: str = "personality",
        user_context: dict | None = None,
        year: int | None = None,
    ) -> dict:
        from typing import Any

        chart = chart or {}
        user_context = user_context or {}
        profile = CycleCalculator.extract_profile(chart, user_context)
        age = profile.get("age")
        timeline = FortuneTimeline.build(
            age=age,
            bureau_number=int(profile.get("bureau_number") or 4),
            gender=profile.get("gender"),
            yin_yang=profile.get("yin_yang"),
            chart=chart,
            question_type=question_type,
        )
        major = timeline.get("current_major_limit")
        stage = timeline.get("current_stage") or StageAnalyzer.analyze(age)
        annual = AnnualEngine.analyze(
            year=year if year is not None else user_context.get("year"),
            question_type=question_type,
            major_palace=(major or {}).get("palace"),
        )
        advice = LifecycleAdvisor.advise(
            question_type=question_type,
            stage=stage,
            major_limit=major,
            annual=annual,
            timeline=timeline,
        )
        result: dict[str, Any] = {
            "profile": profile,
            "timeline": timeline,
            "major_limit": major,
            "stage": stage,
            "annual": annual,
            "advisor": advice,
            "life_timeline": advice.get("life_timeline"),
            "call_trace": [
                "lifecycle:engine",
                f"lifecycle:age={age}",
                f"lifecycle:bureau={profile.get('bureau_number')}",
                f"lifecycle:stage={(stage or {}).get('stage_name')}",
                f"lifecycle:palace={(major or {}).get('palace')}",
                *list((advice or {}).get("call_trace") or []),
            ],
        }
        return result
