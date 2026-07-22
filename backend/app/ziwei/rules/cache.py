"""规则内存缓存 — 从 seed_generator 加载，与 DB seeds 一致。"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.ziwei.rules.seed_generator import build_all_rules


@lru_cache(maxsize=1)
def get_rules_cache() -> dict[str, Any]:
    """加载规则缓存（Sprint 1：内存；未来可改为 DB + 缓存）。"""
    return build_all_rules()


def clear_rules_cache() -> None:
    get_rules_cache.cache_clear()
