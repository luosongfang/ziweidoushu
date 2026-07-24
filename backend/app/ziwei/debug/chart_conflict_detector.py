"""chart_conflict_detector — 同一出生资料双盘冲突分析（不改算法）。"""

from __future__ import annotations

from typing import Any

from app.ziwei.accuracy.chart_diff_engine import ChartDiffEngine, normalize_chart
from app.ziwei.accuracy.root_cause_analyzer import analyze_root_cause


def _birth_key(chart: dict[str, Any]) -> dict[str, Any]:
    birth = chart.get("birth") or {}
    return {
        "solar": birth.get("solar") or birth.get("solar_date") or "",
        "time": birth.get("time") or "",
        "gender": birth.get("gender") or chart.get("gender") or "",
        "location": birth.get("location") or chart.get("location"),
        "true_solar_time": birth.get("true_solar_time", chart.get("true_solar_time")),
    }


def _same_birth(a: dict[str, Any], b: dict[str, Any]) -> bool:
    ka, kb = _birth_key(a), _birth_key(b)
    return (
        ka["solar"] == kb["solar"]
        and ka["time"] == kb["time"]
        and (not ka["gender"] or not kb["gender"] or ka["gender"] == kb["gender"])
    )


def detect_chart_conflict(chart_a: Any, chart_b: Any) -> dict[str, Any]:
    """比较两盘，归类差异类型并给出可能原因（启发式，非定论）。"""
    na = normalize_chart(chart_a)
    nb = normalize_chart(chart_b)
    raw_a = chart_a if isinstance(chart_a, dict) else {}
    raw_b = chart_b if isinstance(chart_b, dict) else {}
    same = _same_birth(raw_a, raw_b)

    diff_result = ChartDiffEngine(compare_aux=True, compare_fortune=True).compare(na, nb)
    by = diff_result.by_impact()
    fields = [d.field for d in diff_result.diffs]

    difference_type: list[str] = []
    if any(any(x in f for x in ("四柱", "农历", "干支")) for f in fields):
        difference_type.append("calendar")
    if any(any(x in f for x in ("命宫", "身宫", "五行局", "宫.")) for f in fields):
        difference_type.append("palace")
    if any(any(x in f for x in ("星曜", "主星", "紫微", "十四")) for f in fields):
        difference_type.append("stars")
    if any("四化" in f for f in fields):
        difference_type.append("transform")
    if any(any(x in f for x in ("运限", "大限", "流年", "小限")) for f in fields):
        difference_type.append("fortune")

    ba, bb = _birth_key(raw_a), _birth_key(raw_b)
    possible_reason: list[str] = []
    if ba.get("true_solar_time") != bb.get("true_solar_time") or (
        bool(ba.get("location")) != bool(bb.get("location"))
    ):
        possible_reason.append("true_solar_time")
    if "calendar" in difference_type:
        possible_reason.append("calendar_rule")
    if "stars" in difference_type and "palace" not in difference_type:
        possible_reason.append("school_difference")
    if same and difference_type:
        possible_reason.append("algorithm_error")

    root = analyze_root_cause(
        {
            "critical_difference": by["critical"],
            "major_difference": by["major"],
            "minor_difference": by["minor"],
        }
    )

    return {
        "same_birth": same,
        "difference_type": difference_type,
        "possible_reason": possible_reason,
        "diff_count": len(diff_result.diffs),
        "accuracy_score": diff_result.accuracy_score(),
        "root_cause": root,
        "critical_difference": by["critical"],
        "major_difference": by["major"],
        "minor_difference": by["minor"],
    }
