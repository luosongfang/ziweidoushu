"""紫微规则分析引擎 — 基于命盘与知识库生成参考分析。"""

from __future__ import annotations

from typing import Any

from app.ziwei_ai.knowledge_base import (
    extract_keywords_section,
    gather_context,
    load_pattern,
    load_star,
)
from app.ziwei_ai.schemas import PalaceFocus, RuleAnalysis
from app.ziwei_data import build_star_analysis, get_star


def _as_dict(chart_data: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(chart_data, str):
        return {"summary_text": chart_data}
    return chart_data or {}


def _normalize_palace_name(name: str) -> str:
    name = (name or "").strip()
    if name and not name.endswith("宫") and name not in {"大限", "流年"}:
        # 兼容「官禄」→「官禄宫」
        if name in {"命", "财帛", "官禄", "夫妻", "福德", "田宅", "迁移"}:
            return f"{name}宫" if name != "命" else "命宫"
        if name == "命宫" or name.endswith("宫"):
            return name
    if name == "命":
        return "命宫"
    return name


def extract_palace_stars(chart: dict[str, Any]) -> dict[str, list[str]]:
    """从多种命盘 JSON 形态提取 宫位→星曜。"""
    result: dict[str, list[str]] = {}

    # 形态 A：{ "命宫": {"stars":[...]}, ... }
    for key, value in chart.items():
        if key in {"chart", "birth", "name", "gender", "summary_text"}:
            continue
        if isinstance(value, dict) and "stars" in value:
            stars = value.get("stars") or []
            names = [
                s if isinstance(s, str) else str(s.get("name", ""))
                for s in stars
            ]
            names = [n for n in names if n]
            if names:
                result[_normalize_palace_name(key)] = names

    # 形态 B：ChartCreateResponse / chart.palaces
    inner = chart.get("chart") if isinstance(chart.get("chart"), dict) else chart
    palaces = inner.get("palaces") if isinstance(inner, dict) else None
    if isinstance(palaces, list):
        for p in palaces:
            if not isinstance(p, dict):
                continue
            pname = _normalize_palace_name(str(p.get("name", "")))
            stars_raw = p.get("stars") or []
            names = [
                s if isinstance(s, str) else str(s.get("name", ""))
                for s in stars_raw
            ]
            # V2：main_stars / lucky_stars 等
            for bucket in ("main_stars", "lucky_stars", "sha_stars", "za_stars"):
                for s in p.get(bucket) or []:
                    n = s if isinstance(s, str) else str(s.get("name", ""))
                    if n:
                        names.append(n)
            names = list(dict.fromkeys(n for n in names if n))
            if pname and names:
                result[pname] = names

    # 形态 C：简要文本 summary_text
    summary = chart.get("summary_text")
    if isinstance(summary, str) and summary.strip():
        for line in summary.splitlines():
            line = line.strip()
            if "：" in line or ":" in line:
                sep = "：" if "：" in line else ":"
                left, right = line.split(sep, 1)
                pname = _normalize_palace_name(left.strip())
                stars = [
                    x.strip()
                    for x in right.replace("，", "、").replace(",", "、").split("、")
                    if x.strip()
                ]
                if pname and stars:
                    result[pname] = stars

    return result


def _detect_patterns(palace_stars: dict[str, list[str]]) -> list[str]:
    all_stars = {s for stars in palace_stars.values() for s in stars}
    patterns: list[str] = []
    ming = set(palace_stars.get("命宫") or [])
    if {"紫微", "天府"} <= ming or ({"紫微", "天府"} <= all_stars and "紫微" in ming):
        patterns.append("紫府")
    if {"七杀", "破军", "贪狼"} <= all_stars:
        patterns.append("杀破狼")
    return patterns


def _knowledge_snippets_from_star_db(star_names: list[str]) -> list[str]:
    """把 ziwei_data 条目转成可供 Prompt 引用的文本块。"""
    blocks: list[str] = []
    for name in dict.fromkeys(star_names):
        entry = get_star(name)
        if not entry:
            continue
        kws = "、".join(entry.get("keywords") or [])
        strengths = "、".join(entry.get("strengths") or [])
        challenges = "、".join(entry.get("challenges") or [])
        traditional = entry.get("traditional") or entry.get("meaning") or ""
        modern = entry.get("modern") or ""
        blocks.append(
            "\n".join(
                [
                    f"## 星曜知识库 · {name}",
                    f"类型：{entry.get('type', '')}",
                    f"传统：{traditional}",
                    f"现代：{modern}",
                    f"关键词：{kws}" if kws else "",
                    f"优势倾向：{strengths}" if strengths else "",
                    f"可能挑战：{challenges}" if challenges else "",
                ]
            ).strip()
        )
    return blocks


def analyze_chart(
    chart_data: dict[str, Any] | str,
    related_palaces: list[str],
) -> RuleAnalysis:
    chart = _as_dict(chart_data)
    palace_stars = extract_palace_stars(chart)

    focuses: list[PalaceFocus] = []
    focus_stars: list[str] = []
    for pname in related_palaces:
        if pname in {"大限", "流年"}:
            continue
        stars = palace_stars.get(pname) or palace_stars.get(
            pname.replace("宫", "") + "宫"
        ) or []
        focuses.append(PalaceFocus(name=pname, stars=stars))
        focus_stars.extend(stars)

    # 若相关宫位无数据，回退命宫/官禄/财帛
    if not any(f.stars for f in focuses):
        for fallback in ("命宫", "官禄宫", "财帛宫"):
            stars = palace_stars.get(fallback) or []
            if stars:
                focuses.append(PalaceFocus(name=fallback, stars=stars))
                focus_stars.extend(stars)

    patterns = _detect_patterns(palace_stars)
    luck_topics = [p for p in related_palaces if p in {"大限", "流年"}]

    # Markdown 旧知识库 + 结构化星曜库
    knowledge = gather_context(
        stars=list(dict.fromkeys(focus_stars)),
        palaces=[f.name for f in focuses],
        patterns=patterns,
        luck=luck_topics,
    )
    knowledge.extend(_knowledge_snippets_from_star_db(focus_stars))

    star_analysis = build_star_analysis(focus_stars)

    # 关键词摘要：优先结构化库
    kw_bits: list[str] = []
    for s in dict.fromkeys(focus_stars):
        entry = get_star(s)
        if entry and entry.get("keywords"):
            kw_bits.extend(list(entry["keywords"])[:4])
        else:
            kw_bits.extend(extract_keywords_section(load_star(s))[:4])

    pattern_notes = []
    for pt in patterns:
        text = load_pattern(pt)
        if text:
            pattern_notes.append(pt)

    star_desc = "、".join(dict.fromkeys(focus_stars)) or "（相关星曜信息不足）"
    palace_desc = "、".join(f.name for f in focuses) or "命盘整体"

    traditional = (
        f"就「{palace_desc}」相关配置来看，主要星曜包括{star_desc}。"
        "在传统紫微理论中，此类组合常被用来描述性格倾向、能力侧重与处事风格的象征意义，"
        "宜作为自我观察的参考框架，而非对具体事件的断定。"
    )
    if pattern_notes:
        traditional += f" 格局线索上，可见与「{'、'.join(pattern_notes)}」相关的象征组合。"
    if star_analysis:
        bits = "；".join(f"{x['star']}（{x['meaning']}）" for x in star_analysis[:6])
        traditional += f" 知识库提示：{bits}。"

    modern_parts = [
        "现实中可以理解为：更适合从组织协调、专业深耕或资源整合等方向认识自身优势；",
        "具体选择仍需结合兴趣、能力积累与现实环境。",
    ]
    if kw_bits:
        modern_parts.insert(
            0,
            f"相关象征关键词包括：{'、'.join(list(dict.fromkeys(kw_bits))[:8])}。",
        )

    strengths = list(dict.fromkeys(kw_bits))[:6]
    if not strengths:
        strengths = ["规划意识", "执行能力", "自我觉察"]
    for item in star_analysis[:4]:
        entry = get_star(item["star"])
        if entry:
            for s in entry.get("strengths") or []:
                if s not in strengths:
                    strengths.append(s)
                if len(strengths) >= 8:
                    break

    return RuleAnalysis(
        traditional_analysis=traditional,
        modern_interpretation="".join(modern_parts),
        strengths=strengths[:8],
        focused_palaces=focuses,
        knowledge_snippets=knowledge,
        star_analysis=star_analysis,
    )
