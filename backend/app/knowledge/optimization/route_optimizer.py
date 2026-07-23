"""Optimize theory selection order from dynamic weights (no LLM)."""

from __future__ import annotations

from typing import Any

from app.knowledge.optimization.optimization_models import (
    DynamicRoute,
    from_dispatch_type,
    normalize_scenario,
    to_dispatch_type,
)
from app.knowledge.optimization.weight_optimizer import WeightOptimizer

# Chinese labels for API readability (scenario codes stay English in DB)
_SCENARIO_LABELS = {
    "entrepreneurship": "创业",
    "career": "事业",
    "wealth": "财富",
    "relationship": "感情",
    "study": "学习",
    "life_transition": "人生转折",
}


class RouteOptimizer:
    """Order theories by dynamic_weight for a scenario."""

    @classmethod
    def scenario_label(cls, scenario: str) -> str:
        scen = normalize_scenario(scenario)
        return _SCENARIO_LABELS.get(scen, scen)

    @classmethod
    def get_ordered_theories(cls, scenario: str) -> list[dict[str, Any]]:
        scen = normalize_scenario(scenario)
        weights = WeightOptimizer.list_weights(scen)
        if not weights:
            # fallback defaults when migration not applied
            defaults = {
                "entrepreneurship": [
                    ("sanhe", 0.8),
                    ("four_transform", 0.6),
                    ("feixing", 0.3),
                ],
                "wealth": [("four_transform", 0.8), ("sanhe", 0.5)],
                "relationship": [("four_transform", 0.7), ("sanhe", 0.5)],
                "career": [("sanhe", 0.75), ("four_transform", 0.55)],
            }
            pairs = defaults.get(scen, [("sanhe", 0.5)])
            return [
                {
                    "name": name,
                    "weight": w,
                    "dispatch_type": to_dispatch_type(name),
                    "base_weight": w,
                }
                for name, w in pairs
            ]

        out = []
        for w in sorted(weights, key=lambda x: (-x.dynamic_weight, -x.base_weight)):
            out.append(
                {
                    "name": w.theory_system,
                    "weight": round(w.dynamic_weight, 4),
                    "dispatch_type": to_dispatch_type(w.theory_system),
                    "base_weight": round(w.base_weight, 4),
                    "success_count": w.success_count,
                    "feedback_score": w.feedback_score,
                }
            )
        return out

    @classmethod
    def build_route(cls, scenario: str, *, use_chinese_label: bool = False) -> DynamicRoute:
        scen = normalize_scenario(scenario)
        theories = [
            {"name": t["name"], "weight": t["weight"]}
            for t in cls.get_ordered_theories(scen)
        ]
        label = cls.scenario_label(scen) if use_chinese_label else scen
        return DynamicRoute(scenario=label, theories=theories)

    @classmethod
    def reorder_dispatch_rows(
        cls,
        question_type: str,
        dispatch_rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Attach dynamic weights and sort fixed dispatch rows (rules unchanged)."""
        ordered = cls.get_ordered_theories(question_type)
        weight_map = {
            t["dispatch_type"]: t["weight"] for t in ordered
        }
        # also key by weight-table name
        for t in ordered:
            weight_map[t["name"]] = t["weight"]

        enriched: list[dict[str, Any]] = []
        for row in dispatch_rows:
            item = dict(row)
            ttype = str(item.get("theory_type") or "")
            wname = from_dispatch_type(ttype)
            item["weight"] = float(
                weight_map.get(ttype, weight_map.get(wname, 0.5))
            )
            item["weight_name"] = wname
            enriched.append(item)

        enriched.sort(key=lambda r: (-float(r.get("weight") or 0), int(r.get("priority") or 99)))
        return enriched
