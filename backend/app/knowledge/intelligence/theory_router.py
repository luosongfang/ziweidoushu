"""Theory router — map question_type to required palaces/stars/patterns/theories."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND = Path(__file__).resolve().parents[3]

# Fallback routes when DB empty
_FALLBACK_ROUTES: dict[str, dict[str, Any]] = {
    "career": {
        "required_palaces": ["命宫", "官禄宫", "财帛宫", "迁移宫"],
        "required_stars": [],
        "required_patterns": ["紫府同宫", "杀破狼", "机月同梁"],
        "required_theories": ["三合派", "四化", "大限"],
        "priority": 10,
        "description": "事业议题：命宫人格 + 官禄事业模式 + 财帛资源 + 迁移环境",
    },
    "entrepreneurship": {
        "required_palaces": ["命宫", "官禄宫", "财帛宫", "迁移宫", "福德宫"],
        "required_stars": [],
        "required_patterns": ["杀破狼", "紫府同宫"],
        "required_theories": ["三合派", "四化", "格局"],
        "priority": 10,
        "description": "创业评估：人格/资源/风险/执行/补给",
    },
    "career_switch": {
        "required_palaces": ["命宫", "官禄宫", "迁移宫"],
        "required_stars": ["破军"],
        "required_patterns": ["杀破狼"],
        "required_theories": ["三合派", "大限"],
        "priority": 20,
        "description": "职业转换：稳定需求与变革动力",
    },
    "wealth": {
        "required_palaces": ["财帛宫", "田宅宫", "官禄宫"],
        "required_stars": ["武曲", "天府", "禄存"],
        "required_patterns": [],
        "required_theories": ["三合派", "四化"],
        "priority": 10,
        "description": "财富规划：财帛态度 + 田宅根据地 + 事业变现",
    },
    "relationship": {
        "required_palaces": ["夫妻宫", "福德宫", "命宫"],
        "required_stars": [],
        "required_patterns": [],
        "required_theories": ["三合派", "四化"],
        "priority": 10,
        "description": "感情关系：互动模式 + 内在需求 + 自我边界",
    },
    "marriage": {
        "required_palaces": ["夫妻宫", "福德宫", "田宅宫"],
        "required_stars": [],
        "required_patterns": [],
        "required_theories": ["三合派"],
        "priority": 10,
        "description": "婚姻经营：相处模式 + 精神补给 + 生活场景",
    },
    "study": {
        "required_palaces": ["父母宫", "官禄宫", "命宫"],
        "required_stars": ["文昌", "文曲"],
        "required_patterns": [],
        "required_theories": ["三合派"],
        "priority": 20,
        "description": "学习考试：权威来源 + 能力映射 + 驱动力",
    },
    "family": {
        "required_palaces": ["父母宫", "子女宫", "福德宫"],
        "required_stars": [],
        "required_patterns": [],
        "required_theories": ["三合派"],
        "priority": 20,
        "description": "家庭关系：长辈/晚辈角色与边界",
    },
    "personality": {
        "required_palaces": ["命宫", "福德宫"],
        "required_stars": [],
        "required_patterns": [],
        "required_theories": ["三合派", "星曜"],
        "priority": 30,
        "description": "自我认知：命宫倾向 + 福德补给",
    },
    "life_stage": {
        "required_palaces": ["命宫", "迁移宫", "官禄宫"],
        "required_stars": [],
        "required_patterns": [],
        "required_theories": ["三合派", "大限", "流年"],
        "priority": 20,
        "description": "人生阶段：阶段主题与准备度",
    },
}


def _engine():
    load_dotenv(BACKEND / ".env", override=True)
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgresql") and "sslmode=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}sslmode=require"
    return create_engine(url, pool_pre_ping=True) if url else None


@lru_cache(maxsize=1)
def _cached_routes() -> dict[str, dict[str, Any]]:
    eng = _engine()
    if eng is None:
        return dict(_FALLBACK_ROUTES)
    try:
        with eng.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT question_type, required_palaces, required_stars,
                           required_patterns, required_theories, priority, description
                    FROM public.theory_routes
                    """
                )
            ).mappings().all()
        if not rows:
            return dict(_FALLBACK_ROUTES)
        out: dict[str, dict[str, Any]] = {}
        for r in rows:
            out[str(r["question_type"])] = {
                "required_palaces": list(r["required_palaces"] or []),
                "required_stars": list(r["required_stars"] or []),
                "required_patterns": list(r["required_patterns"] or []),
                "required_theories": list(r["required_theories"] or []),
                "priority": int(r["priority"] or 100),
                "description": r["description"] or "",
            }
        return out
    except Exception:
        return dict(_FALLBACK_ROUTES)


class TheoryRouter:
    @classmethod
    def refresh(cls) -> None:
        _cached_routes.cache_clear()

    @classmethod
    def route(cls, question_type: str) -> dict[str, Any]:
        routes = _cached_routes()
        base = routes.get(question_type) or routes.get("personality") or _FALLBACK_ROUTES["personality"]
        return {
            "question_type": question_type,
            "required_palaces": list(base.get("required_palaces") or []),
            "required_stars": list(base.get("required_stars") or []),
            "required_patterns": list(base.get("required_patterns") or []),
            "required_theories": list(base.get("required_theories") or []),
            "priority": base.get("priority", 100),
            "description": base.get("description") or "",
        }
