"""标准命盘对比运行器 — Sprint 6 支持组合/运限验证。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models.birth import BirthLocation, ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator

FIXTURES_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "reference_charts.json"


def load_reference_charts() -> dict:
    if not FIXTURES_PATH.exists():
        return {"charts": []}
    return json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))


def _parse_input(inp: dict) -> ChartGenerateRequest:
    y, m, d = map(int, inp["date"].split("-"))
    hh, mm = map(int, inp["time"].split(":"))
    location = None
    if inp.get("longitude") is not None:
        location = BirthLocation(longitude=inp["longitude"])
    return ChartGenerateRequest(
        birth_datetime=datetime(y, m, d, hh, mm),
        gender=inp["gender"],
        name=inp.get("name", "测试"),
        location=location,
        timezone=inp.get("timezone", "Asia/Shanghai"),
    )


def chart_to_expected_view(chart) -> dict[str, Any]:
    """将 ChartOutput 转为与 fixtures expected 可比对的扁平结构。"""
    view: dict[str, Any] = {
        "ganzhi": chart.birth.ganzhi.model_dump(),
        "mingGong": chart.meta.mingGong,
        "shenGong": chart.meta.shenGong,
        "wuxingJu": chart.meta.wuxingJu,
        "mingGongGanZhi": chart.meta.mingGongGanZhi,
        "palaceBranches": [p.branch for p in chart.palaces],
        "daxianDirection": chart.fortune.daxianDirection,
    }
    if chart.palaces[0].sanhe:
        view["mingSanhe"] = chart.palaces[0].sanhe

    star_step = next(
        (s for s in chart.trace.steps if s["engine"] == "star_placement"), None
    )
    if star_step:
        view["ziweiBranch"] = star_step["output"]["ziweiBranch"]

    main_by_palace = {
        p.name: [s.name for s in p.mainStars] for p in chart.palaces if p.mainStars
    }
    if main_by_palace:
        view["mainStarsByPalace"] = main_by_palace

    for field, attr in (
        ("auxStarsByPalace", "auxStars"),
        ("shaStarsByPalace", "shaStars"),
        ("zaStarsByPalace", "zaStars"),
    ):
        by_palace = {
            p.name: [s.name for s in getattr(p, attr)]
            for p in chart.palaces
            if getattr(p, attr)
        }
        if by_palace:
            view[field] = by_palace

    if chart.fourTransformSummary:
        s = chart.fourTransformSummary
        view["fourTransform"] = {
            "yearStem": s.yearStem,
            "lu": {"star": s.lu.star, "palace": s.lu.palace},
            "quan": {"star": s.quan.star, "palace": s.quan.palace},
            "ke": {"star": s.ke.star, "palace": s.ke.palace},
            "ji": {"star": s.ji.star, "palace": s.ji.palace},
        }

    if chart.combinations.patterns:
        view["combinationNames"] = sorted(p.name for p in chart.combinations.patterns)

    return view


def verify_reference_chart(chart_spec: dict) -> list[str]:
    from app.ziwei.verification.diff_detector import detect_diff

    request = _parse_input(chart_spec["input"])
    chart = ChartGenerator.generate(request)
    return detect_diff(chart_spec.get("expected", {}), chart_to_expected_view(chart))


def verify_all_reference_charts() -> dict[str, list[str]]:
    data = load_reference_charts()
    results: dict[str, list[str]] = {}
    for spec in data.get("charts", []):
        diffs = verify_reference_chart(spec)
        if diffs:
            results[spec["id"]] = diffs
    return results
