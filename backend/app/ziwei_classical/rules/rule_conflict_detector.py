"""规则冲突检测 — 禁止自动选择。"""

from __future__ import annotations

from typing import Any

from app.ziwei_classical.rules.loader import (
    get_ming_rule,
    get_tianfu_config,
    load_catalog,
)


def detect_rule_conflicts() -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []

    # 天府多规则
    tf = get_tianfu_config()
    if tf.get("conflict") or len(tf.get("options") or {}) > 1:
        conflicts.append(
            {
                "rule": "tianfu",
                "conflict": True,
                "options": list((tf.get("options") or {}).keys()),
                "option_ids": {
                    k: v.get("id") for k, v in (tf.get("options") or {}).items()
                },
                "auto_select": False,
                "resolution": "classical_config.json → tianfu_rule",
                "sources": tf.get("source"),
            }
        )

    # 命宫措辞冲突
    ming = get_ming_rule()
    disputed = ming.get("disputed_wording")
    if disputed:
        conflicts.append(
            {
                "rule": "ming_gong",
                "conflict": True,
                "options": ["A_standard_forward_month_back_hour", "B_disputed_wording"],
                "detail": disputed,
                "auto_select": False,
                "active": ming.get("formula"),
                "sources": ming.get("source"),
            }
        )

    # 流派配置冲突提示
    catalog = load_catalog()
    conflicts.append(
        {
            "rule": "school",
            "conflict": True,
            "options": ["三合派", "飞星派", "北派"],
            "auto_select": False,
            "resolution": "classical_config.json → school",
            "note": "16册含多派口诀，禁止自动合并",
            "catalog_policy": catalog.get("policy"),
        }
    )

    return conflicts


def require_manual_config(conflicts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    items = conflicts if conflicts is not None else detect_rule_conflicts()
    return {
        "has_conflicts": any(c.get("conflict") for c in items),
        "conflicts": items,
        "message": "存在流派/文献冲突，必须通过 classical_config 显式选择，禁止自动择优",
    }
