"""Build life fortune timeline from major limits + stages (no LLM)."""

from __future__ import annotations

from typing import Any

from app.knowledge.lifecycle.cycle_calculator import CycleCalculator
from app.knowledge.lifecycle.stage_analyzer import StageAnalyzer


class FortuneTimeline:
    """Generate a structured life timeline for advisor consumption."""

    @classmethod
    def build(
        cls,
        *,
        age: int | None,
        bureau_number: int = 4,
        gender: str | None = None,
        yin_yang: str | None = None,
        chart: dict[str, Any] | None = None,
        question_type: str | None = None,
        limit_count: int = 8,
    ) -> dict[str, Any]:
        profile_age = age if age is not None else 35
        limits = CycleCalculator.major_limits(
            bureau_number=bureau_number,
            gender=gender,
            yin_yang=yin_yang,
            chart=chart,
        )
        current = CycleCalculator.current_major_limit(
            profile_age,
            bureau_number=bureau_number,
            gender=gender,
            yin_yang=yin_yang,
            chart=chart,
        )
        stage = StageAnalyzer.analyze(
            profile_age, major_limit=current, question_type=question_type
        )

        # annotate nearby limits with stage names
        timeline: list[dict[str, Any]] = []
        for lim in limits[:limit_count]:
            mid = (lim["age_start"] + lim["age_end"]) // 2
            st = StageAnalyzer.match(mid)
            timeline.append(
                {
                    **lim,
                    "life_stage": st["stage_name"],
                    "focus": st["focus"],
                    "is_current": bool(
                        current
                        and lim.get("age_start") == current.get("age_start")
                        and lim.get("palace") == current.get("palace")
                    ),
                }
            )

        return {
            "age": profile_age,
            "current_major_limit": current,
            "current_stage": stage,
            "timeline": timeline,
            "bureau_number": CycleCalculator.extract_profile(chart, {"age": profile_age}).get(
                "bureau_number", bureau_number
            ),
            "direction": (current or {}).get("direction"),
            "traditional_basis": [
                "大限十年一宫，起运年龄依五行局（水二木三金四土五火六）。",
                "阳男阴女顺行，阴男阳女逆行。",
                "大限描述阶段性主题重心，不作绝对事件预测。",
            ],
            "sources": [
                (current or {}).get("source") or {"type": "fortune_cycle_rule"},
                stage.get("source") or {"type": "life_stage_model"},
            ],
        }
