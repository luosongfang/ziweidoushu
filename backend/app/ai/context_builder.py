"""从 Chart JSON 构建 AI 分析上下文（规则 DB 驱动）。"""

from __future__ import annotations

from typing import Any

from app.models.chart import ChartOutput
from app.ziwei.rules.loader import RulesLoader


def _collect_star_names(chart: ChartOutput) -> list[str]:
    names: list[str] = []
    for palace in chart.palaces:
        for star in palace.mainStars + palace.auxStars + palace.shaStars + palace.zaStars:
            if star.name not in names:
                names.append(star.name)
    return names


def _find_palace(chart: ChartOutput, palace_name: str):
    for palace in chart.palaces:
        if palace.name == palace_name:
            return palace
    return None


class ContextBuilder:
    """提取命盘结构化上下文，并注入规则库 ai_prompt。"""

    PROMPT_VERSION = "v1"

    @classmethod
    def build(
        cls,
        chart: ChartOutput,
        analysis_type: str,
        palace_name: str | None = None,
    ) -> dict[str, Any]:
        star_names = _collect_star_names(chart)
        star_prompts = cls._star_prompts(star_names)
        combination_context = cls._combination_context(chart)
        palace_context = cls._palace_context(chart, palace_name)

        ctx: dict[str, Any] = {
            "prompt_version": cls.PROMPT_VERSION,
            "analysis_type": analysis_type,
            "meta": {
                "name": chart.meta.name,
                "gender": chart.meta.gender,
                "mingGong": chart.meta.mingGong,
                "shenGong": chart.meta.shenGong,
                "mingGongGanZhi": chart.meta.mingGongGanZhi,
                "wuxingJu": chart.meta.wuxingJu,
                "mingZhu": chart.meta.mingZhu,
                "shenZhu": chart.meta.shenZhu,
            },
            "birth": {
                "solar": chart.birth.solar,
                "lunar": chart.birth.lunar,
                "ganzhi": chart.birth.ganzhi.model_dump(),
                "shichen": chart.birth.shichen.name,
            },
            "four_transform": cls._four_transform_context(chart),
            "combinations": combination_context,
            "palaces": palace_context,
            "fortune": cls._fortune_context(chart),
            "star_prompts": star_prompts,
            "rag_queries": cls._rag_queries(chart, analysis_type, palace_name),
        }
        return ctx

    @classmethod
    def _star_prompts(cls, star_names: list[str]) -> list[dict[str, str]]:
        prompts: list[dict[str, str]] = []
        for name in star_names:
            meta = RulesLoader.get_star_metadata(name)
            if meta and meta.get("ai_prompt"):
                prompts.append({"star": name, "prompt": meta["ai_prompt"]})
        return prompts

    @classmethod
    def _combination_context(cls, chart: ChartOutput) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for pattern in chart.combinations.patterns:
            items.append({
                "name": pattern.name,
                "category": pattern.category,
                "stars": pattern.stars,
                "palaces": pattern.palaces,
                "tags": pattern.tags,
                "ai_prompt": pattern.ai_prompt_ref or "",
            })
        return items

    @classmethod
    def _palace_context(
        cls,
        chart: ChartOutput,
        focus_palace: str | None,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for palace in chart.palaces:
            meaning = RulesLoader.get_palace_meaning(palace.name)
            all_stars = (
                [s.name for s in palace.mainStars]
                + [s.name for s in palace.auxStars]
                + [s.name for s in palace.shaStars]
                + [s.name for s in palace.zaStars]
            )
            items.append({
                "name": palace.name,
                "branch": palace.branch,
                "ganzhi": palace.ganzhi,
                "isMingGong": palace.isMingGong,
                "isShenGong": palace.isShenGong,
                "stars": all_stars,
                "mainStars": [s.name for s in palace.mainStars],
                "tags": palace.analysis_tags.tags,
                "meaning": meaning["meaning"] if meaning else "",
                "ai_prompt": meaning["ai_prompt"] if meaning else "",
                "daxian": palace.daxian.model_dump(),
                "focused": palace.name == focus_palace,
            })
        return items

    @classmethod
    def _four_transform_context(cls, chart: ChartOutput) -> dict[str, Any] | None:
        s = chart.fourTransformSummary
        if not s:
            return None
        return {
            "yearStem": s.yearStem,
            "lu": {"star": s.lu.star, "palace": s.lu.palace},
            "quan": {"star": s.quan.star, "palace": s.quan.palace},
            "ke": {"star": s.ke.star, "palace": s.ke.palace},
            "ji": {"star": s.ji.star, "palace": s.ji.palace},
        }

    @classmethod
    def _fortune_context(cls, chart: ChartOutput) -> dict[str, Any]:
        f = chart.fortune
        return {
            "daxianDirection": f.daxianDirection,
            "currentDaxian": f.currentDaxian,
            "annualFortune": f.annualFortune,
            "monthlyFortune": f.monthlyFortune,
        }

    @classmethod
    def _rag_queries(
        cls,
        chart: ChartOutput,
        analysis_type: str,
        palace_name: str | None,
    ) -> list[str]:
        queries: list[str] = []
        if analysis_type == "palace" and palace_name:
            queries.append(palace_name)
            palace = _find_palace(chart, palace_name)
            if palace:
                for star in palace.mainStars:
                    queries.append(star.name)
        elif analysis_type == "daxian":
            queries.extend(["大限", "运限"])
            if chart.fortune.currentDaxian:
                queries.append(chart.fortune.currentDaxian.get("palace", ""))
        elif analysis_type == "liunian":
            queries.extend(["流年", "太岁"])
            if chart.fortune.annualFortune:
                queries.append(chart.fortune.annualFortune.get("palace", ""))
        else:
            queries.extend(["命宫", "格局", "四化"])

        for pattern in chart.combinations.patterns[:5]:
            queries.append(pattern.name)

        ming = _find_palace(chart, "命宫")
        if ming:
            for star in ming.mainStars[:3]:
                queries.append(star.name)

        return [q for q in queries if q]
