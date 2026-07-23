"""Synthesize multi-theory results into decision advice (no LLM)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.multitheory.theory_registry import TheoryRegistry

_FALLBACK_RULES: dict[str, dict[str, Any]] = {
    "entrepreneurship": {
        "input_theories": ["三合", "四化", "格局"],
        "synthesis_logic": "结构资源(三合) + 节奏风险(四化) + 格局条件(古诀) → 优势/风险/建议",
        "output_template": {
            "sections": ["优势", "风险", "建议"],
            "advice_prefix": "创业场景下，建议把多理论对照为能力与风险管理清单",
        },
    },
    "career": {
        "input_theories": ["三合", "四化", "格局"],
        "synthesis_logic": "宫位结构 + 四化节奏 + 格局条件",
        "output_template": {
            "sections": ["优势", "风险", "建议"],
            "advice_prefix": "事业路径宜结合结构优势与阶段节奏",
        },
    },
    "wealth": {
        "input_theories": ["三合", "四化"],
        "synthesis_logic": "财帛结构 + 四化资源波动",
        "output_template": {
            "sections": ["优势", "风险", "建议"],
            "advice_prefix": "财富规划强调安全垫与可验证配置",
        },
    },
    "relationship": {
        "input_theories": ["三合", "四化"],
        "synthesis_logic": "互动模式 + 动态变化",
        "output_template": {
            "sections": ["优势", "风险", "建议"],
            "advice_prefix": "关系议题以沟通与边界管理为主",
        },
    },
    "default": {
        "input_theories": ["三合"],
        "synthesis_logic": "多视角对照后输出学习型建议",
        "output_template": {
            "sections": ["优势", "风险", "建议"],
            "advice_prefix": "综合传统理论视角，服务自我认知与人生规划参考",
        },
    },
}

_SCENARIO_ALIAS = {
    "entrepreneurship": "entrepreneurship",
    "career": "career",
    "career_switch": "career",
    "wealth": "wealth",
    "relationship": "relationship",
    "marriage": "relationship",
    "study": "default",
    "family": "default",
    "personality": "default",
    "life_stage": "default",
}


class SynthesisEngine:
    """Merge multi-theory outputs into common / difference / advice."""

    @classmethod
    @lru_cache(maxsize=16)
    def _load_rule(cls, scenario: str) -> dict[str, Any]:
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT scenario, input_theories, synthesis_logic, output_template
                    FROM public.decision_synthesis_rules
                    WHERE scenario = :s
                    LIMIT 1
                    """
                ),
                {"s": scenario},
            ).mappings().first()
            if row:
                data = dict(row)
                import json

                for k in ("input_theories", "output_template"):
                    v = data.get(k)
                    if isinstance(v, str):
                        data[k] = json.loads(v)
                return data
        except Exception:
            pass
        finally:
            db.close()
        return dict(_FALLBACK_RULES.get(scenario) or _FALLBACK_RULES["default"])

    @classmethod
    def refresh(cls) -> None:
        cls._load_rule.cache_clear()

    @classmethod
    def rule_for_question(cls, question_type: str) -> dict[str, Any]:
        scenario = _SCENARIO_ALIAS.get(question_type or "", "default")
        return cls._load_rule(scenario)

    @classmethod
    def synthesize(
        cls,
        results: dict[str, dict[str, Any]],
        *,
        question_type: str,
        conflicts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        rule = cls.rule_for_question(question_type)
        template = rule.get("output_template") or {}
        prefix = str(template.get("advice_prefix") or "综合多理论视角")

        all_strengths: list[str] = []
        all_challenges: list[str] = []
        all_suggestions: list[str] = []
        by_theory_strength: dict[str, set[str]] = {}

        for t, r in results.items():
            name = TheoryRegistry.display(t)
            strengths = [str(x) for x in (r.get("strengths") or []) if x]
            challenges = [str(x) for x in (r.get("challenges") or []) if x]
            suggestions = [str(x) for x in (r.get("suggestions") or []) if x]
            by_theory_strength[name] = set(strengths)
            all_strengths.extend(strengths)
            all_challenges.extend(challenges)
            all_suggestions.extend(suggestions)

        # common: appear in >=2 theories (substring soft match) or top shared markers
        common_points = cls._common_points(by_theory_strength, all_strengths)
        different_views = cls._different_views(results, conflicts or [])

        advice_parts = [
            prefix,
            "优势侧：" + ("；".join(list(dict.fromkeys(all_strengths))[:3]) or "先盘点既有资源与可验证能力"),
            "风险侧：" + ("；".join(list(dict.fromkeys(all_challenges))[:3]) or "关注节奏与风险管理"),
            "行动侧：" + ("；".join(list(dict.fromkeys(all_suggestions))[:3]) or "小步验证、定期复盘"),
        ]
        if conflicts:
            advice_parts.append(
                "理论差异提示：" + (conflicts[0].get("guidance") or conflicts[0].get("reason") or "")
            )
        advice_parts.append("以上为传统文化分析视角，仅供学习与人生规划参考，不作绝对预测。")

        common_text = "；".join(common_points) if common_points else "各理论均强调结合宫位结构做自我认知，而非吉凶判决。"
        diff_text = "；".join(different_views) if different_views else "主要差异在观察角度（结构/节奏/格局），可并行参考。"

        return {
            "common_points": common_points,
            "different_views": different_views,
            "decision_advice": advice_parts,
            "common": common_text,
            "difference": diff_text,
            "advice": " ".join(advice_parts),
            "input_theories": [
                TheoryRegistry.display(t) for t in results.keys()
            ],
            "synthesis_logic": rule.get("synthesis_logic") or "",
            "scenario": _SCENARIO_ALIAS.get(question_type or "", "default"),
            "sections": {
                "优势": list(dict.fromkeys(all_strengths))[:6],
                "风险": list(dict.fromkeys(all_challenges))[:6],
                "建议": list(dict.fromkeys(all_suggestions))[:6],
            },
        }

    @classmethod
    def _common_points(
        cls,
        by_theory: dict[str, set[str]],
        all_strengths: list[str],
    ) -> list[str]:
        if len(by_theory) < 2:
            return list(dict.fromkeys(all_strengths))[:3]
        shared: list[str] = []
        names = list(by_theory.keys())
        base = list(by_theory[names[0]])
        for s in base:
            hits = 1
            for other in names[1:]:
                if any(cls._soft_match(s, o) for o in by_theory[other]):
                    hits += 1
            if hits >= 2:
                shared.append(s)
        if shared:
            return list(dict.fromkeys(shared))[:5]
        # fallback thematic commons
        return [
            "重视宫位与资源结构的可观察依据",
            "强调阶段节奏与风险管理",
            "输出学习型建议而非绝对预测",
        ]

    @classmethod
    def _different_views(
        cls,
        results: dict[str, dict[str, Any]],
        conflicts: list[dict[str, Any]],
    ) -> list[str]:
        views: list[str] = []
        for c in conflicts:
            level = c.get("level") or "difference"
            views.append(f"[{level}] {c.get('theory_a')} vs {c.get('theory_b')}：{c.get('reason')}")
        if not views:
            summaries = [
                f"{TheoryRegistry.display(t)}侧重：{(r.get('summary') or '')[:60]}"
                for t, r in results.items()
            ]
            views.extend(summaries[:4])
        return views[:6]

    @classmethod
    def _soft_match(cls, a: str, b: str) -> bool:
        if not a or not b:
            return False
        if a == b or a in b or b in a:
            return True
        return len(set(a) & set(b)) >= min(4, min(len(a), len(b)) // 2)
