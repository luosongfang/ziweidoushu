"""Phase 2 命盘 API — POST /api/chart/create。"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chart", tags=["chart-engine-v1"])


@router.post("/create", response_model=ChartCreateResponse)
def create_chart(
    body: ChartCreateRequest,
    db: Session = Depends(get_db),
) -> ChartCreateResponse:
    """
    生成紫微斗数命盘（Engine V1.0）并写入 Supabase PostgreSQL。

    流程：出生资料 → 排盘引擎 → 持久化 birth_profiles / ziwei_charts / chart_palaces → 返回结果
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
    birth_profile_id = None

    if body.persist:
        try:
            record = persist_chart(
                db,
                raw,
                solar_date=body.solar_date,
                birth_time=body.time,
                location=body.location,
                user_id=body.user_id,
            )
            db.commit()
            chart_id = record.id
            birth_profile_id = record.birth_profile_id
        except SQLAlchemyError as exc:
            db.rollback()
            logger.exception("命盘持久化失败：%s", exc)
            raise HTTPException(
                status_code=503,
                detail="数据库保存失败，请检查 Supabase 连接与迁移状态",
            ) from exc

    return ChartCreateResponse(
        name=raw["name"],
        gender=raw["gender"],
        birth=BirthInfo(**raw["birth"]),
        chart=ChartInfo(**raw["chart"]),
        engine_version=raw["engine_version"],
        rules_version=raw["rules_version"],
        chart_id=chart_id,
        birth_profile_id=birth_profile_id,
    )
