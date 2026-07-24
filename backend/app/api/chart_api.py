"""Phase 2 命盘 API — 统一走 ChartPipeline → StandardChartSchema V2.5。"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import ensure_schema, get_db, is_database_ready
from app.database.models import persist_chart
from app.schemas.chart_schema import ChartCreateRequest
from app.ziwei.chart_pipeline import ChartPipeline
from app.ziwei.core.chart_schema_v2 import ChartCreateApiResponse
from app.ziwei_engine.calendar.lunar_converter import LunarConverter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chart", tags=["chart-engine-v1"])


def _database_error_detail() -> str:
    if settings.is_postgres and not settings.database_is_configured:
        return (
            "DATABASE_URL 未配置：请在 backend/.env 填入 Supabase 连接串"
            "（替换 [YOUR-PASSWORD]），然后重启后端并执行 alembic upgrade head"
        )
    return "数据库保存失败：请检查 Supabase 连接、密码与迁移状态（alembic upgrade head）"


@router.post("/create")
def create_chart(
    body: ChartCreateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    生成紫微斗数命盘（统一入口 ChartPipeline → V2.5）。

    校准阶段默认返回 StandardChartSchema V2.5；附带 accuracy 元数据。
    schema_version=3.0 时仍可通过 ProfessionalNormalizer（可选，不影响校准验收）。
    """
    solar_date = body.solar_date
    if body.calendar_type == "lunar":
        try:
            solar_date = LunarConverter.lunar_to_solar(
                body.solar_date,
                is_leap=body.is_leap_month,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        # 排盘本身不因准确率阻断；准确率写入响应供 AI 层门槛使用
        chart, meta = ChartPipeline.generate(
            name=body.name,
            gender=body.gender,
            solar_date=solar_date,
            time=body.time,
            location=body.location,
            reference_year=body.reference_year,
            require_accuracy=False,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"排盘失败：{exc}") from exc

    # V1.2.6 校准：生产验收以 V2.5 为准
    if getattr(body, "schema_version", "2.5") == "3.0":
        from app.ziwei.core.professional_normalizer import ProfessionalNormalizer

        raw = ChartPipeline.generate_raw(
            name=body.name,
            gender=body.gender,
            solar_date=solar_date,
            time=body.time,
            location=body.location,
            reference_year=body.reference_year,
        )
        v3 = ProfessionalNormalizer.normalize(raw, include_legacy_v2=True)
        payload = v3.model_dump(mode="json")
        payload["accuracy"] = meta["accuracy"]
        payload["classical_audit_summary"] = meta["classical_audit_summary"]
    else:
        payload = ChartCreateApiResponse(
            **chart.model_dump(),
            chart_id=None,
            birth_profile_id=None,
            persisted=False,
        ).model_dump(mode="json")
        payload["accuracy"] = meta["accuracy"]
        payload["classical_audit_summary"] = meta["classical_audit_summary"]

    chart_id = None
    birth_profile_id = None
    persisted = False
    persist_warning: str | None = None

    if body.persist:
        if not is_database_ready():
            persist_warning = _database_error_detail()
        else:
            try:
                ensure_schema()
                record = persist_chart(
                    db,
                    chart.model_dump(mode="json"),
                    solar_date=solar_date,
                    birth_time=body.time,
                    location=body.location,
                    user_id=body.user_id,
                )
                db.commit()
                chart_id = record.id
                birth_profile_id = record.birth_profile_id
                persisted = True
            except SQLAlchemyError as exc:
                db.rollback()
                logger.exception("命盘持久化失败：%s", exc)
                persist_warning = _database_error_detail()

    if persist_warning:
        warnings = list(payload.get("warnings") or [])
        warnings.append(persist_warning)
        payload["warnings"] = warnings

    payload["chart_id"] = chart_id
    payload["birth_profile_id"] = birth_profile_id
    payload["persisted"] = persisted
    return payload
