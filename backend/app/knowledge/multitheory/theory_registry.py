"""Theory system registry — load active multi-theory systems (no LLM)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal

# Canonical systems (fallback when DB empty)
FALLBACK_SYSTEMS: list[dict[str, Any]] = [
    {
        "name": "三合派",
        "type": "sanhe",
        "description": "三方四正宫位协同，侧重命/官/财/迁结构",
        "authority_level": 5,
        "active": True,
    },
    {
        "name": "飞星",
        "type": "feixing",
        "description": "星曜飞伏与组合关系视角",
        "authority_level": 4,
        "active": True,
    },
    {
        "name": "四化",
        "type": "sihua",
        "description": "禄权科忌动态变化与资源节奏",
        "authority_level": 5,
        "active": True,
    },
    {
        "name": "古诀格局",
        "type": "classic_formula",
        "description": "经典格局与古诀条件对照",
        "authority_level": 4,
        "active": True,
    },
]

# API / synthesis key aliases
TYPE_ALIASES: dict[str, str] = {
    "sanhe": "sanhe",
    "三合": "sanhe",
    "三合派": "sanhe",
    "feixing": "feixing",
    "飞星": "feixing",
    "sihua": "sihua",
    "四化": "sihua",
    "four_transform": "sihua",
    "classic_formula": "classic_formula",
    "古诀": "classic_formula",
    "格局": "classic_formula",
    "古诀格局": "classic_formula",
}

DISPLAY_NAME: dict[str, str] = {
    "sanhe": "三合派",
    "feixing": "飞星",
    "sihua": "四化",
    "classic_formula": "古诀格局",
}

API_KEY: dict[str, str] = {
    "sanhe": "sanhe",
    "feixing": "feixing",
    "sihua": "four_transform",
    "classic_formula": "classic_formula",
}


class TheoryRegistry:
    """Register and resolve theory systems."""

    @classmethod
    def normalize_type(cls, name_or_type: str) -> str:
        key = (name_or_type or "").strip()
        return TYPE_ALIASES.get(key, TYPE_ALIASES.get(key.lower(), key.lower() or "sanhe"))

    @classmethod
    def display(cls, theory_type: str) -> str:
        t = cls.normalize_type(theory_type)
        return DISPLAY_NAME.get(t, theory_type)

    @classmethod
    def api_key(cls, theory_type: str) -> str:
        t = cls.normalize_type(theory_type)
        return API_KEY.get(t, t)

    @classmethod
    @lru_cache(maxsize=1)
    def list_systems(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT id::text AS id, name, type, description,
                           authority_level, active
                    FROM public.theory_systems
                    WHERE active IS TRUE
                    ORDER BY authority_level DESC, name
                    """
                )
            ).mappings().all()
            if rows:
                return tuple(dict(r) for r in rows)
        except Exception:
            pass
        finally:
            db.close()
        return tuple(FALLBACK_SYSTEMS)

    @classmethod
    def refresh(cls) -> None:
        cls.list_systems.cache_clear()

    @classmethod
    def get_by_type(cls, theory_type: str) -> dict[str, Any] | None:
        t = cls.normalize_type(theory_type)
        for s in cls.list_systems():
            if cls.normalize_type(str(s.get("type") or s.get("name") or "")) == t:
                return dict(s)
        return None

    @classmethod
    def active_types(cls) -> list[str]:
        return [
            cls.normalize_type(str(s.get("type") or ""))
            for s in cls.list_systems()
            if s.get("active", True)
        ]
