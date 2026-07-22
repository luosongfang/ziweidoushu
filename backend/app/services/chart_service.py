"""命盘持久化服务（Sprint 8）。"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.db.repository import Repository, get_repository
from app.models.birth import BirthInput, ChartGenerateRequest
from app.models.chart import ChartOutput
from app.models.chart_record import ChartRecordOutput, ChartRecordSummary, ChartSaveRequest
from app.models.user import AuthUser
from app.ziwei.chart_generator import ChartGenerator


class ChartPersistenceService:
    @classmethod
    def save(
        cls,
        user: AuthUser,
        body: ChartSaveRequest,
        repo: Repository | None = None,
    ) -> ChartRecordOutput:
        repository = repo or get_repository()
        chart = cls._resolve_chart(body)
        record = repository.save_chart(
            user_id=user.id,
            chart=chart,
            birth_datetime=body.birth.to_datetime(),
            calendar_type=body.birth.calendar_type,
            timezone=body.birth.timezone,
        )
        return cls._to_output(record)

    @classmethod
    def list_charts(cls, user: AuthUser, repo: Repository | None = None) -> list[ChartRecordSummary]:
        repository = repo or get_repository()
        return [cls._to_summary(c) for c in repository.list_charts(user.id)]

    @classmethod
    def get_chart(
        cls,
        user: AuthUser,
        chart_id: UUID,
        repo: Repository | None = None,
    ) -> ChartRecordOutput:
        repository = repo or get_repository()
        record = repository.get_chart(chart_id, user.id)
        if not record:
            raise ValueError("命盘不存在或无权访问")
        return cls._to_output(record)

    @classmethod
    def delete_chart(
        cls,
        user: AuthUser,
        chart_id: UUID,
        repo: Repository | None = None,
    ) -> None:
        repository = repo or get_repository()
        if not repository.delete_chart(chart_id, user.id):
            raise ValueError("命盘不存在或无权访问")

    @staticmethod
    def _resolve_chart(body: ChartSaveRequest) -> ChartOutput:
        if body.chart is not None:
            return body.chart
        ref = None
        if body.reference_date:
            ref = datetime.strptime(body.reference_date, "%Y-%m-%d")
        request = ChartGenerateRequest.from_birth_input(body.birth)
        return ChartGenerator.generate(request, reference_date=ref)

    @staticmethod
    def _to_summary(record) -> ChartRecordSummary:
        chart_data = record.chart_data
        meta = chart_data.get("meta", {})
        return ChartRecordSummary(
            id=record.id,
            name=record.name,
            birth_datetime=record.birth_datetime,
            gender=record.gender,
            ming_gong=meta.get("mingGong", ""),
            wuxing_ju=meta.get("wuxingJu", ""),
            created_at=record.created_at,
        )

    @staticmethod
    def _to_output(record) -> ChartRecordOutput:
        return ChartRecordOutput(
            id=record.id,
            user_id=record.user_id,
            name=record.name,
            birth_datetime=record.birth_datetime,
            gender=record.gender,
            calendar_type=record.calendar_type,
            timezone=record.timezone,
            chart_data=ChartOutput.model_validate(record.chart_data),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
