"""coverage_report — 黄金盘覆盖度（防同质化）。"""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.ziwei.debug.reference_manager import list_charts, load_chart


def _yin_yang_from_year_ganzhi(ganzhi_year: str) -> str:
    """年干阴阳：甲丙戊庚壬阳，乙丁己辛癸阴。"""
    if not ganzhi_year:
        return "unknown"
    stem = ganzhi_year[0]
    if stem in "甲丙戊庚壬":
        return "yang"
    if stem in "乙丁己辛癸":
        return "yin"
    return "unknown"


def _bureau_bucket(wuxing_ju: str) -> str | None:
    mapping = {
        "水": "water",
        "木": "wood",
        "金": "metal",
        "火": "fire",
        "土": "earth",
    }
    for zh, en in mapping.items():
        if zh in (wuxing_ju or ""):
            return en
    return None


def _hour_label(time_str: str) -> str:
    if not time_str or ":" not in time_str:
        return "unknown"
    try:
        h = int(time_str.split(":")[0])
    except ValueError:
        return "unknown"
    # 时辰粗分
    buckets = [
        (23, 1, "子"),
        (1, 3, "丑"),
        (3, 5, "寅"),
        (5, 7, "卯"),
        (7, 9, "辰"),
        (9, 11, "巳"),
        (11, 13, "午"),
        (13, 15, "未"),
        (15, 17, "申"),
        (17, 19, "酉"),
        (19, 21, "戌"),
        (21, 23, "亥"),
    ]
    for start, end, name in buckets:
        if start > end:  # 子时跨日
            if h >= start or h < end:
                return name
        elif start <= h < end:
            return name
    return "unknown"


def build_coverage_report(directory=None) -> dict[str, Any]:
    """统计数据集覆盖；含 pending 快照以便观察多样性缺口。"""
    charts = list_charts(directory)
    verified = [c for c in charts if c.get("verification_level") == "verified_professional"]
    # 覆盖统计：优先用有 expected/meta 的全部案例（含 pending 引擎快照）
    gender_yy = Counter()
    five = Counter({k: 0 for k in ("water", "wood", "metal", "fire", "earth")})
    hours: Counter[str] = Counter()
    levels = Counter()

    for c in charts:
        levels[c.get("verification_level") or "pending"] += 1
        birth = c.get("birth") or {}
        gender = birth.get("gender") or c.get("gender") or "unknown"
        cal = c.get("calendar") or {}
        ganzhi = cal.get("ganzhi") or {}
        year_gz = ganzhi.get("year") or ""
        yy = _yin_yang_from_year_ganzhi(year_gz)
        key = f"{gender}_{yy}"
        gender_yy[key] += 1

        meta = c.get("meta") or {}
        ju = meta.get("wuxingju") or meta.get("wuxing_ju") or ""
        bucket = _bureau_bucket(ju)
        if bucket:
            five[bucket] += 1

        time_str = birth.get("time") or ""
        hours[_hour_label(time_str)] += 1

    def _flag(count: int) -> str:
        if count <= 0:
            return "missing"
        if count == 1:
            return "thin"
        return "ok"

    coverage = {
        "male_yang": _flag(gender_yy.get("male_yang", 0)),
        "male_yin": _flag(gender_yy.get("male_yin", 0)),
        "female_yang": _flag(gender_yy.get("female_yang", 0)),
        "female_yin": _flag(gender_yy.get("female_yin", 0)),
        "male_yang_count": gender_yy.get("male_yang", 0),
        "male_yin_count": gender_yy.get("male_yin", 0),
        "female_yang_count": gender_yy.get("female_yang", 0),
        "female_yin_count": gender_yy.get("female_yin", 0),
        "five_element": {
            "water": five["water"],
            "wood": five["wood"],
            "metal": five["metal"],
            "fire": five["fire"],
            "earth": five["earth"],
        },
        "hour_distribution": dict(sorted(hours.items())),
        "gender_yy_raw": dict(gender_yy),
    }

    gaps = []
    for k in ("male_yang", "male_yin", "female_yang", "female_yin"):
        if coverage[k] == "missing":
            gaps.append(k)
    for k, v in coverage["five_element"].items():
        if v == 0:
            gaps.append(f"five_element.{k}")

    return {
        "total_cases": len(charts),
        "verified_cases": len(verified),
        "verified_professional": len(verified),
        "levels": dict(levels),
        "coverage": coverage,
        "gaps": gaps,
        "homogeneous_risk": len(gaps) >= 3 or max(five.values(), default=0) >= max(len(charts) - 2, 1),
    }


def coverage_for_chart_id(chart_id: str, directory=None) -> dict[str, Any]:
    return load_chart(chart_id, directory)
