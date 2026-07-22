"""Phase 2 命盘 API — POST /api/chart/create。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import persist_chart
from app.schemas.chart_schema import (
    BirthInfo,
    ChartCreateRequest,
    ChartCreateResponse,
    ChartInfo,
)
from app.ziwei_engine.chart_builder import ChartBuilder

router = APIRouter(prefix="/api/chart", tags=["chart-engine-v1"])


@router.post("/create", response_model=ChartCreateResponse)
def create_chart(
    body: ChartCreateRequest,
    db: Session = Depends(get_db),
) -> ChartCreateResponse:
    """
    生成紫微斗数命盘（Engine V1.0）。

    基于真实历法与规则表计算，非 mock 数据。
    """
    try:
        raw = ChartBuilder.build(
            name=body.name,
            gender=body.gender,
            solar_date=body.solar_date,
            time=body.time,
            location=body.location,
            reference_year=body.reference_year,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"排盘失败：{exc}") from exc

    chart_id = None
    if body.persist:
        record = persist_chart(db, raw)
        db.commit()
        chart_id = record.id

    return ChartCreateResponse(
        name=raw["name"],
        gender=raw["gender"],
        birth=BirthInfo(**raw["birth"]),
        chart=ChartInfo(**raw["chart"]),
        engine_version=raw["engine_version"],
        rules_version=raw["rules_version"],
        chart_id=chart_id,
    )
