"""庙旺平陷知识/查询层 V1.3 — 十四主星完整；辅煞可扩展。"""

from __future__ import annotations

from typing import Any

from app.ziwei.rules.seed_generator import MAIN_STAR_BRIGHTNESS

# 将 branch→亮度 转为 亮度→[branch]
def _invert_brightness(table: dict[str, str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {
        "庙": [], "旺": [], "得": [], "利": [], "平": [], "陷": [], "不得": [],
    }
    for branch, level in table.items():
        buckets.setdefault(level, []).append(branch)
    return {k: v for k, v in buckets.items() if v}


STAR_STRENGTH_DATABASE: dict[str, dict[str, Any]] = {
    name: {
        **_invert_brightness(branches),
        "by_branch": dict(branches),
        "extensible": True,
        "notes": "源自 RulesLoader MAIN_STAR_BRIGHTNESS（与排盘亮度一致）",
    }
    for name, branches in MAIN_STAR_BRIGHTNESS.items()
}

# 辅星/煞星：骨架预留（未录入完整表前不返回虚假亮度）
STAR_STRENGTH_DATABASE.update({
    "左辅": {"extensible": True, "notes": "辅星亮度待扩展", "by_branch": {}},
    "右弼": {"extensible": True, "notes": "辅星亮度待扩展", "by_branch": {}},
    "文昌": {"extensible": True, "notes": "辅星亮度待扩展", "by_branch": {}},
    "文曲": {"extensible": True, "notes": "辅星亮度待扩展", "by_branch": {}},
    "擎羊": {"extensible": True, "notes": "煞星亮度待扩展", "by_branch": {}},
    "陀罗": {"extensible": True, "notes": "煞星亮度待扩展", "by_branch": {}},
    "火星": {"extensible": True, "notes": "煞星亮度待扩展", "by_branch": {}},
    "铃星": {"extensible": True, "notes": "煞星亮度待扩展", "by_branch": {}},
})


def get_star_strength(name: str) -> dict[str, Any] | None:
    entry = STAR_STRENGTH_DATABASE.get((name or "").strip())
    return dict(entry) if entry else None


def get_brightness(name: str, branch: str) -> str:
    entry = STAR_STRENGTH_DATABASE.get(name)
    if not entry:
        return ""
    by_branch = entry.get("by_branch") or {}
    return by_branch.get(branch, "")
