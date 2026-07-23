"""Theory effectiveness statistics from usage + feedback (no LLM)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal

_THEORY_ALIASES = {
    "三合": "sanhe",
    "三合派": "sanhe",
    "sanhe": "sanhe",
    "四化": "sihua",
    "sihua": "sihua",
    "four_transform": "sihua",
    "飞星": "feixing",
    "feixing": "feixing",
    "古诀": "classic_formula",
    "格局": "classic_formula",
    "classic_formula": "classic_formula",
    "大限": "dalimit",
    "流年": "annual",
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
}


class TheoryStatistics:
    """Aggregate which theories users find helpful by scenario."""

    @classmethod
    def normalize_theory(cls, name: str) -> str:
        key = (name or "").strip()
        return _THEORY_ALIASES.get(key, _THEORY_ALIASES.get(key.lower(), key or "sanhe"))

    @classmethod
    def normalize_scenario(cls, name: str) -> str:
        key = (name or "").strip()
        return _SCENARIO_ALIASES.get(key, key or "general")

    @classmethod
    def record_usage(
        cls,
        *,
        theory_system: str,
        scenario: str,
        feedback_type: str | None = None,
    ) -> dict[str, Any]:
        theory = cls.normalize_theory(theory_system)
        scen = cls.normalize_scenario(scenario)
        helpful = neutral = not_helpful = 0
        if feedback_type == "helpful":
            helpful = 1
        elif feedback_type == "not_helpful":
            not_helpful = 1
        elif feedback_type in {"partially_helpful", "future_check"}:
            neutral = 1

        db = SessionLocal()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO public.theory_effectiveness_stats
                        (theory_system, scenario, usage_count, helpful_count,
                         neutral_count, not_helpful_count, effectiveness_score, updated_at)
                    VALUES
                        (:theory, :scenario, 1, :h, :n, :nh, :eff, NOW())
                    ON CONFLICT (theory_system, scenario) DO UPDATE SET
                        usage_count = public.theory_effectiveness_stats.usage_count + 1,
                        helpful_count = public.theory_effectiveness_stats.helpful_count + :h,
                        neutral_count = public.theory_effectiveness_stats.neutral_count + :n,
                        not_helpful_count = public.theory_effectiveness_stats.not_helpful_count + :nh,
                        effectiveness_score = CASE
                            WHEN (public.theory_effectiveness_stats.usage_count + 1) > 0 THEN
                                ROUND((
                                    (public.theory_effectiveness_stats.helpful_count + :h) * 1.0
                                    + (public.theory_effectiveness_stats.neutral_count + :n) * 0.5
                                ) / (public.theory_effectiveness_stats.usage_count + 1) * 100.0, 2)
                            ELSE 0
                        END,
                        updated_at = NOW()
                    """
                ),
                {
                    "theory": theory,
                    "scenario": scen,
                    "h": helpful,
                    "n": neutral,
                    "nh": not_helpful,
                    "eff": round((helpful * 1.0 + neutral * 0.5) * 100, 2),
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return cls.get_one(theory, scen) or {}

    @classmethod
    def record_from_analysis(
        cls,
        *,
        theory_used: list[str] | None,
        scenario: str,
        feedback_type: str | None = None,
    ) -> list[dict[str, Any]]:
        theories = theory_used or ["三合派"]
        # also pull from theory_analysis keys
        out = []
        seen = set()
        for t in theories:
            key = cls.normalize_theory(str(t))
            if key in seen:
                continue
            seen.add(key)
            out.append(cls.record_usage(theory_system=key, scenario=scenario, feedback_type=feedback_type))
        return out

    @classmethod
    def get_one(cls, theory: str, scenario: str) -> dict[str, Any] | None:
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT theory_system, scenario, usage_count, helpful_count,
                           neutral_count, not_helpful_count, effectiveness_score, updated_at
                    FROM public.theory_effectiveness_stats
                    WHERE theory_system = :t AND scenario = :s
                    """
                ),
                {"t": cls.normalize_theory(theory), "s": cls.normalize_scenario(scenario)},
            ).mappings().first()
            if not row:
                return None
            item = dict(row)
            if item.get("updated_at"):
                item["updated_at"] = item["updated_at"].isoformat()
            return item
        finally:
            db.close()

    @classmethod
    def list_stats(cls, *, scenario: str | None = None) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            if scenario:
                rows = db.execute(
                    text(
                        """
                        SELECT theory_system, scenario, usage_count, helpful_count,
                               neutral_count, not_helpful_count, effectiveness_score, updated_at
                        FROM public.theory_effectiveness_stats
                        WHERE scenario = :s
                        ORDER BY effectiveness_score DESC, usage_count DESC
                        """
                    ),
                    {"s": cls.normalize_scenario(scenario)},
                ).mappings().all()
            else:
                rows = db.execute(
                    text(
                        """
                        SELECT theory_system, scenario, usage_count, helpful_count,
                               neutral_count, not_helpful_count, effectiveness_score, updated_at
                        FROM public.theory_effectiveness_stats
                        ORDER BY scenario, effectiveness_score DESC
                        """
                    )
                ).mappings().all()
            out = []
            for r in rows:
                item = dict(r)
                if item.get("updated_at"):
                    item["updated_at"] = item["updated_at"].isoformat()
                out.append(item)
            return out
        finally:
            db.close()

    @classmethod
    def ranking_summary(cls) -> dict[str, Any]:
        """Human-readable role hints per scenario (rule + stats)."""
        stats = cls.list_stats()
        by_scenario: dict[str, list[dict[str, Any]]] = {}
        for row in stats:
            by_scenario.setdefault(row["scenario"], []).append(row)

        # default pedagogical roles when sparse data
        defaults = {
            "entrepreneurship": [
                {"theory_system": "sanhe", "role": "高", "note": "结构与资源整合主视角"},
                {"theory_system": "sihua", "role": "辅助", "note": "节奏与风险管理"},
                {"theory_system": "feixing", "role": "补充", "note": "星曜互动补充观察"},
            ],
            "career": [
                {"theory_system": "sanhe", "role": "高", "note": "宫位事业结构"},
                {"theory_system": "sihua", "role": "辅助", "note": "阶段变化"},
            ],
            "wealth": [
                {"theory_system": "sihua", "role": "高", "note": "资源节奏"},
                {"theory_system": "sanhe", "role": "辅助", "note": "财帛结构"},
            ],
            "relationship": [
                {"theory_system": "feixing", "role": "补充", "note": "互动张力"},
                {"theory_system": "sanhe", "role": "高", "note": "夫妻/福德宫结构"},
            ],
        }

        result = {}
        for scen, rows in {**{k: [] for k in defaults}, **by_scenario}.items():
            if rows:
                ranked = sorted(rows, key=lambda x: (-(x.get("effectiveness_score") or 0), -(x.get("usage_count") or 0)))
                roles = []
                for i, r in enumerate(ranked[:5]):
                    role = "高" if i == 0 else ("辅助" if i == 1 else "补充")
                    roles.append(
                        {
                            "theory_system": r["theory_system"],
                            "role": role,
                            "effectiveness_score": r.get("effectiveness_score"),
                            "usage_count": r.get("usage_count"),
                        }
                    )
                result[scen] = roles
            else:
                result[scen] = defaults.get(scen, [])
        return result

    @classmethod
    def seed_baseline(cls) -> int:
        """Seed minimal usage rows so theory-stats API is never empty."""
        baselines = [
            ("sanhe", "entrepreneurship", 10, 7, 2, 1),
            ("sihua", "entrepreneurship", 8, 4, 3, 1),
            ("feixing", "entrepreneurship", 5, 2, 2, 1),
            ("sanhe", "career", 12, 8, 3, 1),
            ("sihua", "career", 6, 3, 2, 1),
            ("sihua", "wealth", 9, 5, 3, 1),
            ("sanhe", "wealth", 7, 4, 2, 1),
            ("sanhe", "relationship", 8, 5, 2, 1),
            ("feixing", "relationship", 4, 2, 1, 1),
        ]
        n = 0
        db = SessionLocal()
        try:
            for theory, scen, usage, h, neu, nh in baselines:
                eff = round((h * 1.0 + neu * 0.5) / usage * 100, 2) if usage else 0
                db.execute(
                    text(
                        """
                        INSERT INTO public.theory_effectiveness_stats
                            (theory_system, scenario, usage_count, helpful_count,
                             neutral_count, not_helpful_count, effectiveness_score, updated_at)
                        VALUES
                            (:t, :s, :u, :h, :n, :nh, :eff, NOW())
                        ON CONFLICT (theory_system, scenario) DO UPDATE SET
                            usage_count = GREATEST(public.theory_effectiveness_stats.usage_count, EXCLUDED.usage_count),
                            helpful_count = GREATEST(public.theory_effectiveness_stats.helpful_count, EXCLUDED.helpful_count),
                            neutral_count = GREATEST(public.theory_effectiveness_stats.neutral_count, EXCLUDED.neutral_count),
                            not_helpful_count = GREATEST(public.theory_effectiveness_stats.not_helpful_count, EXCLUDED.not_helpful_count),
                            effectiveness_score = EXCLUDED.effectiveness_score,
                            updated_at = NOW()
                        """
                    ),
                    {"t": theory, "s": scen, "u": usage, "h": h, "n": neu, "nh": nh, "eff": eff},
                )
                n += 1
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return n
