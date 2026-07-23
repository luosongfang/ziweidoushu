"""Interpretation layer — traditional high-risk phrasing → safe guidance (no LLM)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from app.ai.safety_filter import SafetyFilter
from app.knowledge.advisor.advisor_safety import AdvisorSafety

BACKEND = Path(__file__).resolve().parents[3]

_FALLBACK_RULES: list[tuple[str, str, str]] = [
    ("必有灾难", "high", "传统理论认为此阶段需要更加关注风险管理。"),
    ("会发生灾难", "high", "不作为确定事件预测，仅作为传统文化角度的反思参考。"),
    ("你一定会失败", "high", "这个方向可能存在压力与不确定性，建议分阶段验证并准备备选方案。"),
    ("你一定会发财", "high", "可能具备财富管理优势，需要结合现实行动与风险控制。"),
    ("必然离婚", "high", "关系模式可能存在需要沟通调整的地方。"),
    ("婚姻必失败", "high", "关系模式中可能存在需要沟通改善的地方。"),
    ("今年必有灾", "high", "这个阶段建议提高风险意识，提前做好心理准备与规划。"),
    ("破财", "medium", "提示关注资源管理、风险控制和财务规划。"),
    ("有劫难", "high", "传统理论认为某阶段可能存在压力或挑战，可以提前做好心理准备。"),
    ("必然成功", "medium", "结果取决于准备度、执行与环境反馈，建议分阶段验证。"),
]


@lru_cache(maxsize=1)
def _db_rules() -> tuple[tuple[str, str, str], ...]:
    load_dotenv(BACKEND / ".env", override=True)
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        return tuple(_FALLBACK_RULES)
    if url.startswith("postgresql") and "sslmode=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}sslmode=require"
    try:
        eng = create_engine(url, pool_pre_ping=True)
        with eng.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT traditional_expression, risk_level, safe_expression
                    FROM public.interpretation_rules
                    """
                )
            ).mappings().all()
        if not rows:
            return tuple(_FALLBACK_RULES)
        return tuple(
            (
                str(r["traditional_expression"]),
                str(r["risk_level"] or "medium"),
                str(r["safe_expression"]),
            )
            for r in rows
        )
    except Exception:
        return tuple(_FALLBACK_RULES)


class InterpretationLayer:
    @classmethod
    def refresh(cls) -> None:
        _db_rules.cache_clear()

    @classmethod
    def apply(cls, text: str) -> str:
        if not text:
            return text
        out = text
        rules = sorted(_db_rules(), key=lambda x: len(x[0]), reverse=True)
        for trad, _risk, safe in rules:
            if trad and trad in out:
                out = out.replace(trad, safe)
        # compose with existing safety layers
        out = AdvisorSafety.apply(out)
        out = SafetyFilter.apply(out)
        return out

    @classmethod
    def apply_list(cls, items: list[str]) -> list[str]:
        return [cls.apply(x) for x in items if x]
