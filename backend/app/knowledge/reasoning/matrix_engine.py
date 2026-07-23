"""Matrix Engine V2 — star / palace / four-transform matrices."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.knowledge.knowledge_models import (
    FourTransformMatrix,
    PalaceDimensionMatrix,
    StarCombinationMatrix,
)
from app.knowledge.knowledge_service import KnowledgeService
from app.knowledge.reasoning.schemas import ReasoningResult


def _row_to_dict(obj: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if hasattr(val, "hex"):
            val = str(val)
        data[col.name] = val
    return data


_DIM_BY_QTYPE: dict[str, str] = {
    "career": "事业",
    "entrepreneurship": "事业",
    "career_switch": "事业",
    "wealth": "财富",
    "relationship": "关系",
    "marriage": "关系",
    "study": "成长",
    "family": "家庭",
    "personality": "成长",
    "life_stage": "成长",
}


@lru_cache(maxsize=1)
def _cached_star_combos() -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        return tuple(_row_to_dict(r) for r in db.scalars(select(StarCombinationMatrix)).all())
    finally:
        db.close()


@lru_cache(maxsize=8)
def _cached_palace_rows(dimension: str) -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        rows = db.scalars(
            select(PalaceDimensionMatrix).where(PalaceDimensionMatrix.dimension == dimension)
        ).all()
        return tuple(_row_to_dict(r) for r in rows)
    finally:
        db.close()


@lru_cache(maxsize=1)
def _cached_four_transform_rows() -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        return tuple(_row_to_dict(r) for r in db.scalars(select(FourTransformMatrix)).all())
    finally:
        db.close()


class MatrixEngine:
    """综合判断矩阵：星曜组合 + 宫位维度 + 四化。"""

    @classmethod
    def _session(cls) -> Session:
        return SessionLocal()

    @classmethod
    def list_star_combos(cls, db: Session | None = None) -> list[dict[str, Any]]:
        if db is not None:
            return [_row_to_dict(r) for r in db.scalars(select(StarCombinationMatrix)).all()]
        return list(_cached_star_combos())

    @classmethod
    def match_star_combinations(cls, stars: list[str]) -> list[dict[str, Any]]:
        star_set = set(stars)
        matched = []
        for row in cls.list_star_combos():
            needed = {row["star_a"], row.get("star_b"), row.get("star_c")} - {None, ""}
            if needed and needed.issubset(star_set):
                matched.append(row)
        return matched

    @classmethod
    def palace_dimensions(
        cls,
        palaces: list[str],
        dimension: str,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        if db is not None:
            rows = db.scalars(
                select(PalaceDimensionMatrix).where(
                    PalaceDimensionMatrix.dimension == dimension
                )
            ).all()
            wanted = set(palaces)
            return [_row_to_dict(r) for r in rows if r.palace_name in wanted]
        wanted = set(palaces)
        return [r for r in _cached_palace_rows(dimension) if r.get("palace_name") in wanted]

    @classmethod
    def four_transforms(
        cls,
        year_stem: str | None = None,
        transform_types: list[str] | None = None,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        if db is not None:
            rows = [_row_to_dict(r) for r in db.scalars(select(FourTransformMatrix)).all()]
        else:
            rows = list(_cached_four_transform_rows())
        if year_stem:
            stemmed = [r for r in rows if r.get("year_stem") == year_stem]
            if stemmed:
                rows = stemmed
            else:
                rows = [r for r in rows if r.get("year_stem") is None]
        else:
            rows = [r for r in rows if r.get("year_stem") is None]
        if transform_types:
            rows = [r for r in rows if r.get("transform_type") in transform_types]
        return rows

    @classmethod
    def analyze(
        cls,
        chart: dict[str, Any],
        question_type: str,
        required_palaces: list[str] | None = None,
    ) -> tuple[ReasoningResult, dict[str, Any]]:
        stars = KnowledgeService.extract_stars_from_chart(chart)
        combos = cls.match_star_combinations(stars)
        dim = _DIM_BY_QTYPE.get(question_type, "成长")
        palaces = required_palaces or ["命宫", "官禄宫"]
        palace_rows = cls.palace_dimensions(palaces, dim)

        year_stem = None
        if isinstance(chart.get("year_stem"), str):
            year_stem = chart["year_stem"]
        elif isinstance(chart.get("meta"), dict):
            year_stem = chart["meta"].get("year_stem") or chart["meta"].get("stem")
        transforms = cls.four_transforms(year_stem=year_stem)

        obs: list[str] = []
        trad: list[str] = []
        strengths: list[str] = []
        challenges: list[str] = []
        suggestions: list[str] = []
        sources: list[dict[str, Any]] = []
        trace = [
            f"matrix:stars={','.join(stars)}",
            f"matrix:combos={len(combos)}",
            f"matrix:palace_dim={dim}:{len(palace_rows)}",
            f"matrix:four_tf={len(transforms)}",
        ]

        for c in combos:
            sources.append(
                {
                    "type": "star_combination",
                    "name": c.get("combination_name"),
                    "pattern": c.get("traditional_pattern"),
                }
            )
            obs.append(f"命中组合矩阵：{c.get('combination_name')}（{c.get('traditional_pattern')}）")
            if c.get("traditional_pattern"):
                trad.append(str(c["traditional_pattern"]))
            if question_type in {"career", "entrepreneurship", "career_switch"} and c.get(
                "career_dimension"
            ):
                strengths.append(str(c["career_dimension"]))
            elif question_type == "wealth" and c.get("wealth_dimension"):
                strengths.append(str(c["wealth_dimension"]))
            elif question_type in {"relationship", "marriage"} and c.get(
                "relationship_dimension"
            ):
                strengths.append(str(c["relationship_dimension"]))
            elif c.get("personality_dimension"):
                strengths.append(str(c["personality_dimension"]))
            if c.get("challenge_dimension"):
                challenges.append(str(c["challenge_dimension"]))
            if c.get("growth_direction"):
                suggestions.append(str(c["growth_direction"]))

        for p in palace_rows:
            sources.append(
                {
                    "type": "palace_dimension",
                    "name": p.get("palace_name"),
                    "dimension": p.get("dimension"),
                }
            )
            if p.get("traditional_meaning"):
                trad.append(f"{p['palace_name']}/{dim}：{p['traditional_meaning']}")
            if p.get("modern_meaning"):
                obs.append(str(p["modern_meaning"]))
            if p.get("advice_template"):
                suggestions.append(str(p["advice_template"]))

        for t in transforms[:6]:
            sources.append(
                {
                    "type": "four_transform",
                    "name": t.get("transform_type"),
                    "star": t.get("star_name"),
                    "stem": t.get("year_stem"),
                }
            )
            if t.get("traditional_effect"):
                trad.append(str(t["traditional_effect"]))
            if t.get("positive_expression"):
                strengths.append(str(t["positive_expression"]))
            if t.get("challenge_expression"):
                challenges.append(str(t["challenge_expression"]))
            if t.get("growth_advice"):
                suggestions.append(str(t["growth_advice"]))
            if t.get("modern_effect"):
                obs.append(str(t["modern_effect"]))

        result = ReasoningResult(
            dimension=f"matrix:{dim}",
            observations=list(dict.fromkeys(obs))[:10],
            traditional_basis=list(dict.fromkeys(trad))[:12],
            strengths=list(dict.fromkeys(strengths))[:8],
            challenges=list(dict.fromkeys(challenges))[:8],
            suggestions=list(dict.fromkeys(suggestions))[:8],
            sources=sources,
            call_trace=trace,
        )
        summary = {
            "dimension": dim,
            "matched_combinations": [c.get("combination_name") for c in combos],
            "palace_count": len(palace_rows),
            "four_transform_count": len(transforms),
            "chart_stars": stars,
        }
        return result, summary
