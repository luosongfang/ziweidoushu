"""Theory dispatcher — select which theories to run for a question (no LLM)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.intelligence.theory_router import TheoryRouter
from app.knowledge.multitheory.theory_registry import TheoryRegistry

# Fallback: question_type → theory types + palace focus
_FALLBACK_DISPATCH: dict[str, list[dict[str, Any]]] = {
    "career": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["命宫", "官禄宫", "财帛宫", "迁移宫"],
            "required_stars": [],
            "required_patterns": ["紫府同宫", "杀破狼"],
            "priority": 10,
        },
        {
            "theory_type": "sihua",
            "required_palaces": ["官禄宫", "财帛宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 20,
        },
        {
            "theory_type": "classic_formula",
            "required_palaces": ["命宫", "官禄宫"],
            "required_stars": [],
            "required_patterns": ["紫府同宫", "杀破狼", "机月同梁"],
            "priority": 30,
        },
    ],
    "entrepreneurship": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["命宫", "官禄宫", "财帛宫", "迁移宫", "福德宫"],
            "required_stars": [],
            "required_patterns": ["杀破狼", "紫府同宫"],
            "priority": 10,
            "example": "创业：三合看结构资源",
        },
        {
            "theory_type": "sihua",
            "required_palaces": ["官禄宫", "财帛宫", "福德宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 15,
            "example": "创业：四化看节奏与风险",
        },
        {
            "theory_type": "classic_formula",
            "required_palaces": ["命宫", "官禄宫"],
            "required_stars": [],
            "required_patterns": ["杀破狼", "紫府同宫"],
            "priority": 25,
            "example": "创业：格局对照",
        },
        {
            "theory_type": "feixing",
            "required_palaces": ["命宫", "官禄宫", "迁移宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 35,
        },
    ],
    "career_switch": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["命宫", "官禄宫", "迁移宫"],
            "required_stars": ["破军"],
            "required_patterns": ["杀破狼"],
            "priority": 10,
        },
        {
            "theory_type": "sihua",
            "required_palaces": ["官禄宫", "迁移宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 20,
        },
    ],
    "wealth": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["财帛宫", "田宅宫", "官禄宫"],
            "required_stars": ["武曲", "天府", "禄存"],
            "required_patterns": [],
            "priority": 10,
        },
        {
            "theory_type": "sihua",
            "required_palaces": ["财帛宫", "官禄宫"],
            "required_stars": ["武曲", "禄存"],
            "required_patterns": [],
            "priority": 15,
        },
        {
            "theory_type": "classic_formula",
            "required_palaces": ["财帛宫"],
            "required_stars": ["武曲", "天府"],
            "required_patterns": [],
            "priority": 30,
        },
    ],
    "relationship": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["夫妻宫", "福德宫", "命宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 10,
        },
        {
            "theory_type": "sihua",
            "required_palaces": ["夫妻宫", "福德宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 20,
        },
    ],
    "marriage": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["夫妻宫", "福德宫", "田宅宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 10,
        },
        {
            "theory_type": "classic_formula",
            "required_palaces": ["夫妻宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 30,
        },
    ],
    "study": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["父母宫", "官禄宫", "命宫"],
            "required_stars": ["文昌", "文曲"],
            "required_patterns": [],
            "priority": 10,
        },
        {
            "theory_type": "classic_formula",
            "required_palaces": ["父母宫", "命宫"],
            "required_stars": ["文昌", "文曲"],
            "required_patterns": [],
            "priority": 20,
        },
    ],
    "family": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["父母宫", "子女宫", "福德宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 10,
        }
    ],
    "personality": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["命宫", "福德宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 10,
        },
        {
            "theory_type": "feixing",
            "required_palaces": ["命宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 20,
        },
    ],
    "life_stage": [
        {
            "theory_type": "sanhe",
            "required_palaces": ["命宫", "迁移宫", "官禄宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 10,
        },
        {
            "theory_type": "sihua",
            "required_palaces": ["命宫", "官禄宫"],
            "required_stars": [],
            "required_patterns": [],
            "priority": 20,
        },
    ],
}


class TheoryDispatcher:
    """Choose theory systems for a question type."""

    @classmethod
    @lru_cache(maxsize=32)
    def _db_mappings(cls, question_type: str) -> tuple[dict[str, Any], ...] | None:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT ts.type AS theory_type, ts.name AS theory_name,
                           m.required_palaces, m.required_stars, m.required_patterns,
                           m.priority, m.example
                    FROM public.theory_rules_mapping m
                    JOIN public.theory_systems ts ON ts.id = m.theory_id
                    WHERE m.question_type = :qtype AND ts.active IS TRUE
                    ORDER BY m.priority ASC
                    """
                ),
                {"qtype": question_type},
            ).mappings().all()
            if not rows:
                return None
            out = []
            for r in rows:
                item = dict(r)
                for k in ("required_palaces", "required_stars", "required_patterns"):
                    v = item.get(k)
                    if isinstance(v, str):
                        import json

                        item[k] = json.loads(v)
                    item[k] = list(item.get(k) or [])
                item["theory_type"] = TheoryRegistry.normalize_type(
                    str(item.get("theory_type") or "")
                )
                out.append(item)
            return tuple(out)
        except Exception:
            return None
        finally:
            db.close()

    @classmethod
    def refresh(cls) -> None:
        cls._db_mappings.cache_clear()

    @classmethod
    def dispatch(cls, question_type: str) -> list[dict[str, Any]]:
        qtype = question_type or "personality"
        db_rows = cls._db_mappings(qtype)
        if db_rows:
            out = [dict(r) for r in db_rows]
        else:
            fallback = _FALLBACK_DISPATCH.get(qtype) or _FALLBACK_DISPATCH["personality"]
            # enrich from TheoryRouter palaces if missing
            route = TheoryRouter.route(qtype)
            out = []
            for item in fallback:
                row = dict(item)
                if not row.get("required_palaces"):
                    row["required_palaces"] = list(route.get("required_palaces") or [])
                row["theory_name"] = TheoryRegistry.display(row["theory_type"])
                out.append(row)

        # V5.6: reorder by dynamic weights (rules/content unchanged)
        try:
            from app.knowledge.optimization.route_optimizer import RouteOptimizer

            out = RouteOptimizer.reorder_dispatch_rows(qtype, out)
        except Exception:
            pass
        return out

    @classmethod
    def get_dynamic_theory_route(cls, question_type: str) -> dict[str, Any]:
        """
        Return scenario + weighted theory list for Multi-Theory dispatch.

        Example:
          {"scenario": "创业", "theories": [{"name": "sanhe", "weight": 0.85}, ...]}
        """
        from app.knowledge.optimization.optimization_service import OptimizationService

        return OptimizationService.get_route(question_type or "personality", use_chinese_label=True)

    @classmethod
    def theory_types(cls, question_type: str) -> list[str]:
        return [r["theory_type"] for r in cls.dispatch(question_type)]

    @classmethod
    def union_palaces(cls, question_type: str) -> list[str]:
        palaces: list[str] = []
        for r in cls.dispatch(question_type):
            for p in r.get("required_palaces") or []:
                if p not in palaces:
                    palaces.append(p)
        return palaces
