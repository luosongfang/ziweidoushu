"""紫微斗数专业星曜数据库 V1 — 知识资产层（不参与排盘计算）。"""

from __future__ import annotations

from typing import Any

from app.ziwei_data.stars.auspicious_stars import AUSPICIOUS_STAR_DATABASE
from app.ziwei_data.stars.evil_stars import EVIL_STAR_DATABASE
from app.ziwei_data.stars.main_stars import MAIN_STAR_DATABASE
from app.ziwei_data.stars.minor_stars import MINOR_STAR_DATABASE
from app.ziwei_data.stars.star_strength import STAR_STRENGTH_DATABASE, get_star_strength
from app.ziwei_data.stars.transformations import FOUR_TRANSFORMATIONS

# 统一检索索引（主星优先覆盖同名）
STAR_DATABASE: dict[str, dict[str, Any]] = {}
STAR_DATABASE.update(MINOR_STAR_DATABASE)
STAR_DATABASE.update(EVIL_STAR_DATABASE)
STAR_DATABASE.update(AUSPICIOUS_STAR_DATABASE)
STAR_DATABASE.update(MAIN_STAR_DATABASE)


def get_star(name: str) -> dict[str, Any] | None:
    """按星名查询知识条目；不存在返回 None。"""
    key = (name or "").strip()
    if not key:
        return None
    entry = STAR_DATABASE.get(key)
    if entry is None:
        return None
    return dict(entry)


def get_star_public(name: str) -> dict[str, Any] | None:
    """API 对外字段：name / type / traditional / modern / keywords。"""
    entry = get_star(name)
    if entry is None:
        return None
    return {
        "name": entry.get("name", name),
        "type": entry.get("type", ""),
        "traditional": entry.get("traditional", entry.get("meaning", "")),
        "modern": entry.get("modern", ""),
        "keywords": list(entry.get("keywords") or []),
        "strengths": list(entry.get("strengths") or []),
        "challenges": list(entry.get("challenges") or []),
        "category": entry.get("category", ""),
    }


def star_meaning_line(name: str) -> str:
    """供 AI 引用的一句现代释义。"""
    entry = get_star(name)
    if not entry:
        return ""
    modern = (entry.get("modern") or "").strip()
    if modern:
        # 取首句，控制提示词长度
        for sep in ("。", "；", ".", ";"):
            if sep in modern:
                return modern.split(sep, 1)[0].strip()
        return modern[:40]
    kws = entry.get("keywords") or []
    if kws:
        return "、".join(str(k) for k in kws[:3])
    return (entry.get("meaning") or entry.get("traditional") or "")[:40]


def build_star_analysis(star_names: list[str]) -> list[dict[str, str]]:
    """命盘星曜 → star_analysis 列表（去重保序）。"""
    seen: set[str] = set()
    rows: list[dict[str, str]] = []
    for raw in star_names:
        name = (raw or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        meaning = star_meaning_line(name)
        if not meaning:
            continue
        rows.append({"star": name, "meaning": meaning})
    return rows


def knowledge_coverage() -> dict[str, Any]:
    """知识库完成度快照。"""
    return {
        "main_stars": len(MAIN_STAR_DATABASE),
        "main_stars_target": 14,
        "auspicious_stars": len(AUSPICIOUS_STAR_DATABASE),
        "auspicious_stars_target": 6,
        "evil_stars": len(EVIL_STAR_DATABASE),
        "evil_stars_target": 6,
        "minor_stars": len(MINOR_STAR_DATABASE),
        "minor_stars_target": 11,
        "strength_entries": len(STAR_STRENGTH_DATABASE),
        "transformations_stems": len(FOUR_TRANSFORMATIONS),
        "transformations_target": 10,
        "total_indexed": len(STAR_DATABASE),
        "version": "ziwei_data_v1",
    }


__all__ = [
    "STAR_DATABASE",
    "MAIN_STAR_DATABASE",
    "AUSPICIOUS_STAR_DATABASE",
    "EVIL_STAR_DATABASE",
    "MINOR_STAR_DATABASE",
    "STAR_STRENGTH_DATABASE",
    "FOUR_TRANSFORMATIONS",
    "get_star",
    "get_star_public",
    "get_star_strength",
    "star_meaning_line",
    "build_star_analysis",
    "knowledge_coverage",
]
