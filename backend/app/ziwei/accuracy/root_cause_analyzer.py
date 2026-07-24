"""root_cause_analyzer — 根据 chart_diff 定位可疑引擎模块（不改算法）。"""

from __future__ import annotations

from typing import Any


def _fields(diff: dict[str, Any] | list | None) -> list[str]:
    if not diff:
        return []
    if isinstance(diff, list):
        return [str(d.get("field") or "") for d in diff if isinstance(d, dict)]
    # DiffResult-like
    if isinstance(diff, dict):
        out: list[str] = []
        for key in ("critical_difference", "major_difference", "minor_difference", "diffs"):
            for d in diff.get(key) or []:
                if isinstance(d, dict):
                    out.append(str(d.get("field") or ""))
        return out
    return []


def _has(fields: list[str], *needles: str) -> bool:
    for f in fields:
        for n in needles:
            if n in f:
                return True
    return False


def analyze_root_cause(chart_diff: dict[str, Any] | list) -> dict[str, Any]:
    """按优先级判断差异根因模块。"""
    fields = _fields(chart_diff)
    if not fields:
        return {
            "cause": "none",
            "confidence": "high",
            "matched_rule": 0,
            "evidence": [],
            "message": "无差异",
        }

    ming_diff = _has(fields, "命宫", "ming_gong", "minggong")
    star_diff = _has(fields, "十四主星", "星曜.紫微", "星曜.天机", "星曜.太阳", "星曜.武曲",
                     "星曜.天同", "星曜.廉贞", "星曜.天府", "星曜.太阴", "星曜.贪狼",
                     "星曜.巨门", "星曜.天相", "星曜.天梁", "星曜.七杀", "星曜.破军",
                     "紫微位置", "天府位置", "宫.", "主星")
    # refine: 宫.X.主星 counts as star
    transform_diff = _has(fields, "四化")
    aux_diff = _has(fields, "辅星", "煞星", "杂曜", "左辅", "右弼", "文昌", "文曲",
                    "天魁", "天钺", "擎羊", "陀罗", "火星", "铃星", "地空", "地劫",
                    "天姚", "红鸾", "天喜", "天刑", "孤辰", "寡宿", "华盖", "天哭", "天虚")
    fortune_diff = _has(fields, "运限", "大限", "流年", "小限")
    calendar_diff = _has(fields, "四柱", "农历", "干支")

    # Rule 1
    if ming_diff or (calendar_diff and ming_diff):
        return {
            "cause": "calendar_or_palace_engine",
            "confidence": "high" if ming_diff else "medium",
            "matched_rule": 1,
            "evidence": [f for f in fields if any(x in f for x in ("命宫", "四柱", "农历", "身宫"))],
            "message": "命宫或历法不一致 → 优先检查 CalendarEngine / PalaceEngine",
        }

    # If calendar differs but ming same — still calendar risk before stars
    if calendar_diff and not star_diff:
        return {
            "cause": "calendar_or_palace_engine",
            "confidence": "medium",
            "matched_rule": 1,
            "evidence": [f for f in fields if any(x in f for x in ("四柱", "农历"))],
            "message": "历法四柱差异",
        }

    # Rule 2
    if (not ming_diff) and star_diff:
        return {
            "cause": "star_position_engine",
            "confidence": "high",
            "matched_rule": 2,
            "evidence": [f for f in fields if any(x in f for x in ("星曜", "主星", "紫微", "天府", "十四"))],
            "message": "命宫一致但十四主星不同 → StarPlacement / ZiweiPlacement",
        }

    # Rule 3
    if (not star_diff) and transform_diff:
        return {
            "cause": "four_transform_engine",
            "confidence": "high",
            "matched_rule": 3,
            "evidence": [f for f in fields if "四化" in f],
            "message": "主星一致但四化不同 → FourTransform",
        }

    # Rule 4
    if (not star_diff) and aux_diff:
        return {
            "cause": "minor_star_engine",
            "confidence": "high",
            "matched_rule": 4,
            "evidence": [f for f in fields if any(x in f for x in ("辅", "煞", "杂", "左辅", "擎羊", "天姚"))],
            "message": "主星一致但辅/煞/杂不同 → Auxiliary / MinorStar",
        }

    # Rule 5
    if fortune_diff:
        return {
            "cause": "fortune_engine",
            "confidence": "high" if not (ming_diff or star_diff) else "medium",
            "matched_rule": 5,
            "evidence": [f for f in fields if any(x in f for x in ("运限", "大限", "流年", "小限"))],
            "message": "大限/流年/小限差异 → FortuneEngine",
        }

    # star + transform both
    if star_diff and transform_diff:
        return {
            "cause": "star_position_engine",
            "confidence": "medium",
            "matched_rule": 2,
            "evidence": fields[:10],
            "message": "主星与四化均有差异，优先主星定位",
        }

    return {
        "cause": "unknown",
        "confidence": "low",
        "matched_rule": 0,
        "evidence": fields[:20],
        "message": "未匹配已知规则",
    }
