"""星曜知识查询 API — GET /api/star/{name}（增量，不影响排盘）。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from app.ziwei_data import (
    FOUR_TRANSFORMATIONS,
    get_star_public,
    get_star_strength,
    knowledge_coverage,
)

router = APIRouter(prefix="/api/star", tags=["star-knowledge"])


class StarInfoResponse(BaseModel):
    name: str
    type: str = ""
    traditional: str = ""
    modern: str = ""
    keywords: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    category: str = ""


class StarCoverageResponse(BaseModel):
    coverage: dict


@router.get("/_coverage", response_model=StarCoverageResponse)
async def star_knowledge_coverage() -> StarCoverageResponse:
    """知识库完成度（运维/测试用）。"""
    return StarCoverageResponse(coverage=knowledge_coverage())


@router.get("/_transformations/{stem}")
async def star_transformations(stem: str = Path(..., min_length=1, max_length=2)):
    """按天干查询四化表。"""
    row = FOUR_TRANSFORMATIONS.get(stem.strip())
    if not row:
        raise HTTPException(status_code=404, detail=f"未找到天干四化：{stem}")
    return {"stem": stem.strip(), "transformations": row}


@router.get("/_strength/{name}")
async def star_strength(name: str = Path(..., min_length=1)):
    """查询庙旺平陷知识条目（若尚未录入则 404）。"""
    data = get_star_strength(name)
    if data is None:
        raise HTTPException(status_code=404, detail=f"庙旺数据尚未录入：{name}")
    return {"name": name, "strength": data}


@router.get("/{name}", response_model=StarInfoResponse)
async def get_star_info(name: str = Path(..., min_length=1, description="星曜名称")):
    """
    查询单颗星曜的知识解释。

    示例：`GET /api/star/紫微`
    """
    info = get_star_public(name)
    if info is None:
        raise HTTPException(status_code=404, detail=f"星曜知识未收录：{name}")
    return StarInfoResponse(**info)
