"""Annual (流年) influence interface — traditional rules, no absolute prediction."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

_FALLBACK_ANNUAL: list[dict[str, Any]] = [
    {
        "year_type": "stem",
        "trigger_rule": {"stems": STEMS, "note": "年干对应四化节奏观察"},
        "influence_dimension": "four_transform",
        "description": "流年天干提示四化主题变化，用于一年注意力分配，不作年度判决。",
    },
    {
        "year_type": "branch",
        "trigger_rule": {"branches": BRANCHES, "note": "年支与宫位地支对照"},
        "influence_dimension": "palace_activation",
        "description": "流年地支可对照相关宫位主题被激活的可能，强调准备与复盘。",
    },
    {
        "year_type": "palace",
        "trigger_rule": {"focus_palaces": ["命宫", "官禄宫", "财帛宫", "迁移宫"]},
        "influence_dimension": "career_wealth",
        "description": "流年落入事业财帛相关宫位时，适合做目标拆解与资源盘点。",
    },
    {
        "year_type": "palace",
        "trigger_rule": {"focus_palaces": ["夫妻宫", "福德宫"]},
        "influence_dimension": "relationship",
        "description": "流年落到情感福德相关宫位时，适合加强沟通与边界管理。",
    },
]


class AnnualEngine:
    """流年影响接口：返回维度与建议表达，禁止绝对事件预测。"""

    @classmethod
    @lru_cache(maxsize=1)
    def list_rules(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT year_type, trigger_rule, influence_dimension, description
                    FROM public.annual_influence_rules
                    """
                )
            ).mappings().all()
            if rows:
                import json

                out = []
                for r in rows:
                    item = dict(r)
                    tr = item.get("trigger_rule") or {}
                    if isinstance(tr, str):
                        tr = json.loads(tr)
                    item["trigger_rule"] = tr
                    out.append(item)
                return tuple(out)
        except Exception:
            pass
        finally:
            db.close()
        return tuple(_FALLBACK_ANNUAL)

    @classmethod
    def refresh(cls) -> None:
        cls.list_rules.cache_clear()

    @classmethod
    def year_stem_branch(cls, year: int) -> dict[str, str]:
        # 1984 甲子年为参照
        base = 1984
        idx = (int(year) - base) % 60
        return {"stem": STEMS[idx % 10], "branch": BRANCHES[idx % 12], "year": str(year)}

    @classmethod
    def analyze(
        cls,
        *,
        year: int | None = None,
        question_type: str | None = None,
        major_palace: str | None = None,
    ) -> dict[str, Any]:
        from datetime import datetime

        y = int(year or datetime.now().year)
        sb = cls.year_stem_branch(y)
        matched: list[dict[str, Any]] = []
        for rule in cls.list_rules():
            yt = rule.get("year_type")
            tr = rule.get("trigger_rule") or {}
            hit = False
            if yt == "stem" and sb["stem"] in (tr.get("stems") or STEMS):
                hit = True
            elif yt == "branch" and sb["branch"] in (tr.get("branches") or BRANCHES):
                hit = True
            elif yt == "palace":
                focuses = tr.get("focus_palaces") or []
                if not focuses:
                    hit = True
                elif major_palace and major_palace in focuses:
                    hit = True
                elif question_type in {"career", "entrepreneurship", "wealth"} and any(
                    p in focuses for p in ("官禄宫", "财帛宫", "迁移宫")
                ):
                    hit = True
                elif question_type in {"relationship", "marriage"} and any(
                    p in focuses for p in ("夫妻宫", "福德宫")
                ):
                    hit = True
            if hit:
                matched.append(
                    {
                        "year_type": yt,
                        "influence_dimension": rule.get("influence_dimension"),
                        "description": rule.get("description"),
                        "source": {
                            "type": "annual_influence_rule",
                            "year_type": yt,
                            "book": "流年规则",
                        },
                    }
                )

        summary = (
            f"流年{y}（{sb['stem']}{sb['branch']}）可用于观察一年节奏与注意力分配；"
            "传统流年规则强调准备与复盘，不作绝对事件预测。"
        )
        if matched:
            summary += " " + (matched[0].get("description") or "")

        return {
            "year": y,
            "stem": sb["stem"],
            "branch": sb["branch"],
            "ganzhi": f"{sb['stem']}{sb['branch']}",
            "influences": matched[:6],
            "summary": summary,
            "growth_advice": "把流年主题拆成季度目标与复盘节点，用可验证行动代替吉凶判断。",
            "sources": [m["source"] for m in matched[:4]]
            or [{"type": "annual_influence_rule", "book": "流年规则"}],
        }
