"""Build unified decision context from memory / lifecycle / multitheory / graph."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.decision.decision_models import (
    DECISION_SCENARIOS,
    DIMENSION_RULES,
    PROCESS_STEPS,
)
from app.knowledge.knowledge_service import KnowledgeService


class DecisionContextBuilder:
    """Assemble inputs for Decision Engine (rule-based, no LLM)."""

    @classmethod
    def classify_scenario(cls, question: str, question_type: str | None = None) -> dict[str, Any]:
        text_q = question or ""
        best = None
        best_hits = 0
        for sc in cls.list_scenarios():
            kws = list(sc.get("keywords") or [])
            hits = sum(1 for k in kws if k in text_q)
            # soft boost from question_type
            st = sc.get("scenario_type") or ""
            if question_type:
                if question_type in {"entrepreneurship"} and sc["scenario_name"] == "entrepreneurship":
                    hits += 3
                elif question_type in {"career_switch"} and sc["scenario_name"] == "career_change":
                    hits += 3
                elif question_type == "wealth" and sc["scenario_name"] == "investment_decision":
                    hits += 3
                elif question_type in {"relationship", "marriage"} and sc[
                    "scenario_name"
                ] == "relationship_choice":
                    hits += 3
                elif question_type == "study" and sc["scenario_name"] == "education_path":
                    hits += 2
                elif question_type == "life_stage" and sc["scenario_name"] == "life_transition":
                    hits += 2
                elif question_type == "career" and st == "career" and hits == 0:
                    hits += 1
            if hits > best_hits:
                best_hits = hits
                best = sc
        if best is None:
            # default by question_type
            mapping = {
                "entrepreneurship": "entrepreneurship",
                "career_switch": "career_change",
                "career": "career_change",
                "wealth": "investment_decision",
                "relationship": "relationship_choice",
                "marriage": "relationship_choice",
                "study": "education_path",
                "life_stage": "life_transition",
            }
            name = mapping.get(question_type or "", "life_transition")
            best = cls.get_scenario(name) or DECISION_SCENARIOS[-1]
        return dict(best)

    @classmethod
    @lru_cache(maxsize=1)
    def list_scenarios(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT scenario_name, scenario_type, description,
                           required_palaces, required_stars, required_patterns,
                           required_cycles, decision_dimensions, risk_dimensions,
                           growth_dimensions, safety_level, version
                    FROM public.decision_models
                    """
                )
            ).mappings().all()
            if rows:
                import json

                out = []
                for r in rows:
                    item = dict(r)
                    for k in (
                        "required_palaces",
                        "required_stars",
                        "required_patterns",
                        "required_cycles",
                        "decision_dimensions",
                        "risk_dimensions",
                        "growth_dimensions",
                    ):
                        v = item.get(k)
                        if isinstance(v, str):
                            item[k] = json.loads(v)
                        item[k] = list(item.get(k) or [])
                    # attach keywords from fallback
                    for fb in DECISION_SCENARIOS:
                        if fb["scenario_name"] == item["scenario_name"]:
                            item["keywords"] = fb.get("keywords") or []
                            break
                    out.append(item)
                return tuple(out)
        except Exception:
            pass
        finally:
            db.close()
        return tuple(DECISION_SCENARIOS)

    @classmethod
    def get_scenario(cls, name: str) -> dict[str, Any] | None:
        for s in cls.list_scenarios():
            if s.get("scenario_name") == name:
                return dict(s)
        return None

    @classmethod
    def refresh(cls) -> None:
        cls.list_scenarios.cache_clear()
        cls.list_dimension_rules.cache_clear()
        cls.list_process_steps.cache_clear()

    @classmethod
    @lru_cache(maxsize=1)
    def list_dimension_rules(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT dimension, traditional_factor, positive_expression,
                           challenge_expression, growth_direction, source_reference
                    FROM public.decision_dimension_rules
                    """
                )
            ).mappings().all()
            if rows:
                return tuple(dict(r) for r in rows)
        except Exception:
            pass
        finally:
            db.close()
        return tuple(DIMENSION_RULES)

    @classmethod
    @lru_cache(maxsize=1)
    def list_process_steps(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT scenario, step_order, title, content_template, safety_expression
                    FROM public.decision_process_templates
                    ORDER BY step_order
                    """
                )
            ).mappings().all()
            if rows:
                return tuple(dict(r) for r in rows)
        except Exception:
            pass
        finally:
            db.close()
        # generic steps for all scenarios
        return tuple({**s, "scenario": "default"} for s in PROCESS_STEPS)

    @classmethod
    def match_dimension_rules(
        cls,
        *,
        chart: dict[str, Any],
        scenario: dict[str, Any],
        patterns: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        stars = KnowledgeService.extract_stars_from_chart(chart)
        star_set = set(stars)
        pattern_names = [p.get("pattern_name") or "" for p in (patterns or [])]
        # also detect classic patterns by stars
        if {"紫微", "天府"}.issubset(star_set):
            pattern_names.append("紫府同宫")
        if {"七杀", "破军", "贪狼"}.issubset(star_set) or (
            len({"七杀", "破军", "贪狼"} & star_set) >= 2
        ):
            pattern_names.append("杀破狼")

        factors = set(stars) | set(pattern_names)
        factors.update(scenario.get("required_palaces") or [])
        factors.add("大限")
        factors.add("命宫")
        if "财帛宫" in (scenario.get("required_palaces") or []):
            factors.add("财帛宫")
        if "夫妻宫" in (scenario.get("required_palaces") or []):
            factors.add("夫妻宫")
        if "官禄宫" in (scenario.get("required_palaces") or []):
            factors.add("官禄宫")

        wanted_dims = set(scenario.get("decision_dimensions") or []) | set(
            scenario.get("risk_dimensions") or []
        ) | set(scenario.get("growth_dimensions") or [])

        hits: list[dict[str, Any]] = []
        for rule in cls.list_dimension_rules():
            factor = str(rule.get("traditional_factor") or "")
            dim = str(rule.get("dimension") or "")
            if factor not in factors and not any(factor in f for f in factors):
                continue
            if wanted_dims and dim not in wanted_dims and dim not in {
                "decision",
                "personality",
            }:
                # still allow career/wealth matches tightly related
                if dim not in {"career", "wealth", "relationship", "learning"}:
                    continue
            hits.append(dict(rule))
        return hits

    @classmethod
    def build(
        cls,
        *,
        question: str,
        question_type: str,
        chart: dict[str, Any],
        theory_analysis: dict[str, Any] | None = None,
        life_timeline: dict[str, Any] | None = None,
        user_memory: dict[str, Any] | None = None,
        selected_knowledge: list[dict[str, Any]] | None = None,
        patterns: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        scenario = cls.classify_scenario(question, question_type)
        patterns = patterns or KnowledgeService.match_patterns(
            KnowledgeService.extract_stars_from_chart(chart)
        )
        dimension_hits = cls.match_dimension_rules(
            chart=chart, scenario=scenario, patterns=patterns
        )
        steps = [
            s
            for s in cls.list_process_steps()
            if s.get("scenario") in {scenario["scenario_name"], "default", "*"}
            or s.get("scenario") is None
        ]
        if not steps:
            steps = [{**s, "scenario": scenario["scenario_name"]} for s in PROCESS_STEPS]

        # knowledge citations
        sources: list[dict[str, Any]] = []
        for ch in (selected_knowledge or [])[:5]:
            sources.append(
                {
                    "type": "knowledge_chunk",
                    "book": ch.get("book_name") or ch.get("book_source") or ch.get("book"),
                    "page": ch.get("page_number") or ch.get("page"),
                    "chapter": ch.get("chapter"),
                }
            )
        for hit in dimension_hits[:6]:
            sources.append(
                {
                    "type": "decision_dimension_rule",
                    "source_reference": hit.get("source_reference"),
                    "factor": hit.get("traditional_factor"),
                }
            )

        return {
            "scenario": scenario,
            "dimension_hits": dimension_hits,
            "process_steps": steps,
            "patterns": [
                {
                    "pattern_name": p.get("pattern_name"),
                    "traditional_meaning": p.get("traditional_meaning"),
                    "advantages": p.get("advantages"),
                    "challenges": p.get("challenges"),
                    "growth_advice": p.get("growth_advice"),
                    "source_reference": p.get("source_reference"),
                }
                for p in patterns
            ],
            "theory_analysis": theory_analysis or {},
            "life_timeline": life_timeline or {},
            "user_memory": user_memory or {},
            "sources": sources,
            "stars": KnowledgeService.extract_stars_from_chart(chart),
        }
