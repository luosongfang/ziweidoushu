"""Pattern reasoning from Knowledge Core."""

from __future__ import annotations

from typing import Any

from app.knowledge.knowledge_service import KnowledgeService
from app.knowledge.reasoning.schemas import ReasoningResult


class PatternReasoning:
    @classmethod
    def analyze(cls, chart: dict[str, Any], dimension: str) -> ReasoningResult:
        stars = KnowledgeService.extract_stars_from_chart(chart)
        patterns = KnowledgeService.match_patterns(stars)
        trace = [f"extract_stars:{','.join(stars)}", f"match_patterns:{len(patterns)}"]
        obs: list[str] = []
        trad: list[str] = []
        strengths: list[str] = []
        challenges: list[str] = []
        suggestions: list[str] = []
        sources: list[dict[str, Any]] = []

        if not patterns:
            obs.append("未命中已入库的核心格局模板；以下基于宫位星曜知识推理。")
        for p in patterns:
            sources.append(
                {"type": "pattern", "name": p.get("pattern_name"), "version": p.get("version")}
            )
            obs.append(f"识别格局：{p.get('pattern_name')}")
            if p.get("traditional_meaning"):
                trad.append(str(p["traditional_meaning"]))
            strengths.extend(p.get("advantages") or [])
            challenges.extend(p.get("challenges") or [])
            if dimension in {"career", "entrepreneurship", "career_switch"} and p.get(
                "career_analysis"
            ):
                suggestions.append(str(p["career_analysis"]))
            if dimension == "wealth" and p.get("wealth_analysis"):
                suggestions.append(str(p["wealth_analysis"]))
            if dimension in {"relationship", "marriage"} and p.get("relationship_analysis"):
                suggestions.append(str(p["relationship_analysis"]))
            if p.get("growth_advice"):
                suggestions.append(str(p["growth_advice"]))
            trace.append(f"pattern:{p.get('pattern_name')}")

        return ReasoningResult(
            dimension=f"{dimension}:patterns",
            observations=obs,
            traditional_basis=list(dict.fromkeys(trad)),
            strengths=list(dict.fromkeys(strengths))[:8],
            challenges=list(dict.fromkeys(challenges))[:8],
            suggestions=list(dict.fromkeys(suggestions))[:8],
            sources=sources,
            call_trace=trace,
        )
