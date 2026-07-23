"""Palace-focused reasoning from Knowledge Core."""

from __future__ import annotations

from typing import Any

from app.knowledge.knowledge_loader import KnowledgeLoader
from app.knowledge.reasoning.schemas import ReasoningResult

# 三方四正：本宫 + 对宫 + 三合两宫（简化标准表）
SANFANG_SIZHENG: dict[str, list[str]] = {
    "命宫": ["命宫", "财帛宫", "官禄宫", "迁移宫"],
    "兄弟宫": ["兄弟宫", "疾厄宫", "田宅宫", "仆役宫"],
    "夫妻宫": ["夫妻宫", "迁移宫", "福德宫", "官禄宫"],
    "子女宫": ["子女宫", "仆役宫", "父母宫", "田宅宫"],
    "财帛宫": ["财帛宫", "官禄宫", "命宫", "迁移宫"],
    "疾厄宫": ["疾厄宫", "田宅宫", "兄弟宫", "仆役宫"],
    "迁移宫": ["迁移宫", "命宫", "官禄宫", "财帛宫"],
    "仆役宫": ["仆役宫", "兄弟宫", "疾厄宫", "田宅宫"],
    "官禄宫": ["官禄宫", "迁移宫", "命宫", "财帛宫"],
    "田宅宫": ["田宅宫", "仆役宫", "兄弟宫", "疾厄宫"],
    "福德宫": ["福德宫", "父母宫", "夫妻宫", "子女宫"],
    "父母宫": ["父母宫", "福德宫", "子女宫", "夫妻宫"],
}


def expand_sanfang_sizheng(palaces: list[str]) -> list[str]:
    """Expand required palaces with 三方四正 related set (deduped, order preserved)."""
    out: list[str] = []
    for p in palaces:
        for x in SANFANG_SIZHENG.get(p, [p]):
            if x not in out:
                out.append(x)
    return out


def _palace_stars(chart: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for key, val in chart.items():
        if isinstance(val, dict) and "stars" in val:
            names = [s if isinstance(s, str) else str(s.get("name", "")) for s in val.get("stars") or []]
            result[key if key.endswith("宫") or key in {"命宫"} else key] = [n for n in names if n]
    inner = chart.get("chart") if isinstance(chart.get("chart"), dict) else None
    if inner and isinstance(inner.get("palaces"), list):
        for p in inner["palaces"]:
            pname = str(p.get("name", ""))
            names = [s if isinstance(s, str) else str(s.get("name", "")) for s in p.get("stars") or []]
            if pname:
                result[pname] = [n for n in names if n]
    return result


class PalaceReasoning:
    @classmethod
    def analyze(
        cls,
        chart: dict[str, Any],
        palaces: list[str],
        dimension: str,
    ) -> ReasoningResult:
        trace: list[str] = []
        obs: list[str] = []
        trad: list[str] = []
        strengths: list[str] = []
        challenges: list[str] = []
        suggestions: list[str] = []
        sources: list[dict[str, Any]] = []

        palace_stars = _palace_stars(chart)
        expanded = expand_sanfang_sizheng(palaces)
        trace.append(f"sanfang_sizheng:{','.join(expanded)}")
        for pname in expanded:
            pk = KnowledgeLoader.get_palace(pname)
            trace.append(f"load_palace:{pname}")
            if not pk:
                continue
            sources.append({"type": "palace", "name": pname, "version": pk.get("version")})
            stars = palace_stars.get(pname) or []
            obs.append(f"{pname}关注「{pk.get('modern_interpretation') or pk.get('basic_meaning')}」；当前星曜：{'、'.join(stars) or '未标注'}")
            if pk.get("traditional_description") or pk.get("basic_meaning"):
                trad.append(f"{pname}：{pk.get('basic_meaning')}")
            if pk.get("positive_expression"):
                strengths.append(str(pk["positive_expression"]))
            if pk.get("challenge_expression"):
                challenges.append(str(pk["challenge_expression"]))
            if pk.get("development_advice") or pk.get("development_direction"):
                suggestions.append(
                    str(pk.get("development_advice") or pk.get("development_direction"))
                )

            for sname in stars:
                sk = KnowledgeLoader.get_star(sname)
                trace.append(f"load_star:{sname}@ {pname}")
                if not sk:
                    continue
                sources.append({"type": "star", "name": sname, "version": sk.get("version")})
                if sk.get("traditional_description"):
                    trad.append(f"{sname}：{sk['traditional_description']}")
                strengths.extend(sk.get("personality_positive") or [])
                strengths.extend(sk.get("career_strength") or [] if dimension in {"career", "entrepreneurship", "career_switch"} else [])
                challenges.extend(sk.get("personality_challenge") or [])
                challenges.extend(sk.get("career_risk") or [] if dimension in {"career", "entrepreneurship", "career_switch"} else [])
                if sk.get("growth_advice"):
                    suggestions.append(str(sk["growth_advice"]))

        return ReasoningResult(
            dimension=dimension,
            observations=list(dict.fromkeys(obs)),
            traditional_basis=list(dict.fromkeys(trad)),
            strengths=list(dict.fromkeys(strengths))[:8],
            challenges=list(dict.fromkeys(challenges))[:8],
            suggestions=list(dict.fromkeys(suggestions))[:8],
            sources=sources,
            call_trace=trace,
        )
