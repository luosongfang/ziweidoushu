"""Life stage models — match age to advisor stage (no LLM)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal

_FALLBACK_STAGES: list[dict[str, Any]] = [
    {
        "stage_name": "childhood",
        "age_range": {"min": 0, "max": 12},
        "focus_dimensions": ["learning", "family", "growth"],
        "advisor_template": "童年阶段宜夯实学习习惯与安全感，把好奇转化为可持续兴趣。",
    },
    {
        "stage_name": "education",
        "age_range": {"min": 13, "max": 22},
        "focus_dimensions": ["learning", "growth", "career"],
        "advisor_template": "求学阶段宜积累可迁移能力与价值判断，为后续事业路径做准备。",
    },
    {
        "stage_name": "career_build",
        "age_range": {"min": 23, "max": 34},
        "focus_dimensions": ["career", "wealth", "growth"],
        "advisor_template": "事业奠基阶段宜用小步验证建立专业信用与资源网络。",
    },
    {
        "stage_name": "career_expand",
        "age_range": {"min": 35, "max": 44},
        "focus_dimensions": ["career", "wealth", "growth"],
        "advisor_template": "事业拓展阶段宜把既有优势结构化，并同步关注风险管理。",
    },
    {
        "stage_name": "relationship",
        "age_range": {"min": 45, "max": 59},
        "focus_dimensions": ["relationship", "family", "growth"],
        "advisor_template": "关系与家庭经营阶段宜强化沟通边界与相互支持系统。",
    },
    {
        "stage_name": "retirement",
        "age_range": {"min": 60, "max": 120},
        "focus_dimensions": ["growth", "family", "learning"],
        "advisor_template": "成熟收成阶段宜整理经验资产，转向传承、健康节奏与意义感。",
    },
]


class StageAnalyzer:
    """Match chronological age to life_stage_models."""

    @classmethod
    @lru_cache(maxsize=1)
    def list_stages(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT stage_name, age_range, focus_dimensions, advisor_template
                    FROM public.life_stage_models
                    ORDER BY (age_range->>'min')::int ASC NULLS LAST
                    """
                )
            ).mappings().all()
            if rows:
                out = []
                for r in rows:
                    item = dict(r)
                    ar = item.get("age_range") or {}
                    if isinstance(ar, str):
                        import json

                        ar = json.loads(ar)
                    fd = item.get("focus_dimensions") or []
                    if isinstance(fd, str):
                        import json

                        fd = json.loads(fd)
                    item["age_range"] = ar
                    item["focus_dimensions"] = fd
                    out.append(item)
                return tuple(out)
        except Exception:
            pass
        finally:
            db.close()
        return tuple(_FALLBACK_STAGES)

    @classmethod
    def refresh(cls) -> None:
        cls.list_stages.cache_clear()

    @classmethod
    def match(cls, age: int | None) -> dict[str, Any]:
        if age is None:
            # default working-adult stage for unknown age
            age = 35
        for stage in cls.list_stages():
            ar = stage.get("age_range") or {}
            lo = int(ar.get("min", 0))
            hi = int(ar.get("max", 200))
            if lo <= age <= hi:
                return {
                    "stage_name": stage["stage_name"],
                    "age_range": f"{lo}-{hi}",
                    "age_range_raw": {"min": lo, "max": hi},
                    "focus": list(stage.get("focus_dimensions") or []),
                    "advisor_template": stage.get("advisor_template") or "",
                    "source": {
                        "type": "life_stage_model",
                        "stage": stage["stage_name"],
                    },
                }
        last = cls.list_stages()[-1]
        ar = last.get("age_range") or {}
        return {
            "stage_name": last["stage_name"],
            "age_range": f"{ar.get('min', 60)}-{ar.get('max', 120)}",
            "age_range_raw": ar,
            "focus": list(last.get("focus_dimensions") or []),
            "advisor_template": last.get("advisor_template") or "",
            "source": {"type": "life_stage_model", "stage": last["stage_name"]},
        }

    @classmethod
    def analyze(
        cls,
        age: int | None,
        *,
        major_limit: dict[str, Any] | None = None,
        question_type: str | None = None,
    ) -> dict[str, Any]:
        stage = cls.match(age)
        traditional_bits = [
            f"人生阶段模型对应：{stage['stage_name']}（{stage['age_range']}岁）。",
        ]
        if major_limit:
            traditional_bits.append(
                f"当前大限宫位参考：{major_limit.get('palace')}（{major_limit.get('age_range')}）。"
            )
        if question_type:
            traditional_bits.append(f"结合议题类型「{question_type}」做阶段重点对齐。")
        return {
            **stage,
            "traditional_view": " ".join(traditional_bits)
            + " 大限与阶段仅描述主题重心，不作绝对事件预测。",
            "age": age,
        }
