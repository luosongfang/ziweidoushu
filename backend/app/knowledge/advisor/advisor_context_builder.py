"""Convert traditional Ziwei phrasing into life-advisor context language."""

from __future__ import annotations

from typing import Any

from app.knowledge.advisor.advisor_safety import AdvisorSafety
from app.knowledge.knowledge_loader import KnowledgeLoader
from app.knowledge.knowledge_service import KnowledgeService


# Deterministic phrase remaps (Knowledge-driven tone, not LLM)
_PHRASE_MAP: list[tuple[str, str]] = [
    (
        "七杀入命，杀气重",
        "传统理论中认为七杀代表行动力、突破性和面对变化的能力，同时也提示需要学习规划和节奏管理。",
    ),
    (
        "杀气重",
        "行动锋芒较明显，需要配套规划与节奏管理。",
    ),
    (
        "破军动荡",
        "传统上破军象征变革与推陈出新，现代解读为变化适应力强，需用里程碑约束节奏。",
    ),
    (
        "紫微坐命必贵",
        "传统以紫微象征统筹与中枢调度；现代解读为领导与规划倾向，结果仍取决于现实行动。",
    ),
    (
        "财帛落空",
        "提示关注资源管理、风险控制和财务规划。",
    ),
    (
        "夫妻宫凶",
        "关系模式中可能存在需要沟通改善的地方。",
    ),
]


class AdvisorContextBuilder:
    """把传统紫微结果转换成人生导师上下文。"""

    @classmethod
    def rewrite_text(cls, text: str) -> str:
        out = text or ""
        for src, dst in _PHRASE_MAP:
            if src in out:
                out = out.replace(src, dst)
        return AdvisorSafety.apply(out)

    @classmethod
    def rewrite_list(cls, items: list[str]) -> list[str]:
        return [cls.rewrite_text(x) for x in items if x]

    @classmethod
    def build_from_reasoning(
        cls,
        chart_data: dict[str, Any],
        question: str,
        reasoning_parts: list[Any] | None = None,
    ) -> dict[str, Any]:
        stars = KnowledgeService.extract_stars_from_chart(chart_data)
        star_ctx = []
        for name in stars:
            row = KnowledgeLoader.get_star(name)
            if not row:
                continue
            # convert traditional to advisor tone
            basic = row.get("basic_meaning") or ""
            trad = row.get("traditional_description") or ""
            growth = row.get("growth_advice") or ""
            star_ctx.append(
                {
                    "star": name,
                    "advisor_view": cls.rewrite_text(
                        f"传统理论中，{name}常被理解为{basic}"
                        + (f"；{trad}" if trad else "")
                        + (f"。成长方向：{growth}" if growth else "")
                    ),
                    "positive": row.get("personality_positive") or [],
                    "challenge": row.get("personality_challenge") or [],
                }
            )

        rewritten_obs: list[str] = []
        rewritten_trad: list[str] = []
        for part in reasoning_parts or []:
            obs = getattr(part, "observations", None) or (
                part.get("observations") if isinstance(part, dict) else []
            )
            trad = getattr(part, "traditional_basis", None) or (
                part.get("traditional_basis") if isinstance(part, dict) else []
            )
            rewritten_obs.extend(cls.rewrite_list(list(obs or [])))
            rewritten_trad.extend(cls.rewrite_list(list(trad or [])))

        return {
            "question": question,
            "stars": stars,
            "star_advisor_context": star_ctx,
            "rewritten_observations": list(dict.fromkeys(rewritten_obs))[:12],
            "rewritten_traditional": list(dict.fromkeys(rewritten_trad))[:12],
        }
