"""AI 解读持久化 + 配额服务（Sprint 8）。"""

from __future__ import annotations

from uuid import UUID

from app.ai.analysis_service import AnalysisService
from app.ai.context_builder import ContextBuilder
from app.db.repository import Repository, get_repository
from app.models.analysis import AnalysisGenerateRequest, AnalysisOutput
from app.models.chart import ChartOutput
from app.models.chart_record import (
    AnalysisRecordOutput,
    AnalysisRecordSummary,
    PersistAnalysisRequest,
)
from app.models.user import AuthUser


class AnalysisPersistenceService:
    @classmethod
    async def generate_and_persist(
        cls,
        user: AuthUser,
        body: PersistAnalysisRequest,
        repo: Repository | None = None,
    ) -> tuple[AnalysisOutput, AnalysisRecordOutput]:
        repository = repo or get_repository()
        stored_chart = repository.get_chart(body.chart_id, user.id)
        if not stored_chart:
            raise ValueError("命盘不存在或无权访问")

        repository.deduct_ai_quota(user.id)

        chart = ChartOutput.model_validate(stored_chart.chart_data)
        request = AnalysisGenerateRequest(
            chart=chart,
            analysis_type=body.analysis_type,  # type: ignore[arg-type]
            palace_name=body.palace_name,
            reference_date=body.reference_date,
            mode=body.mode,  # type: ignore[arg-type]
        )
        result = await AnalysisService.generate(request)

        record = repository.save_analysis(
            user_id=user.id,
            chart_id=body.chart_id,
            analysis_type=body.analysis_type,
            palace_name=body.palace_name,
            prompt_version=ContextBuilder.PROMPT_VERSION,
            input_context=result.input_context,
            result_text=result.result_text,
            tokens_used=result.tokens_used,
        )
        return result, cls._to_output(record)

    @classmethod
    def list_analyses(cls, user: AuthUser, repo: Repository | None = None) -> list[AnalysisRecordSummary]:
        repository = repo or get_repository()
        return [cls._to_summary(a) for a in repository.list_analyses(user.id)]

    @classmethod
    def get_analysis(
        cls,
        user: AuthUser,
        analysis_id: UUID,
        repo: Repository | None = None,
    ) -> AnalysisRecordOutput:
        repository = repo or get_repository()
        record = repository.get_analysis(analysis_id, user.id)
        if not record:
            raise ValueError("解读记录不存在或无权访问")
        return cls._to_output(record)

    @staticmethod
    def _to_summary(record) -> AnalysisRecordSummary:
        preview = record.result_text[:120].replace("\n", " ")
        return AnalysisRecordSummary(
            id=record.id,
            chart_id=record.chart_id,
            analysis_type=record.analysis_type,
            palace_name=record.palace_name,
            preview=preview,
            created_at=record.created_at,
        )

    @staticmethod
    def _to_output(record) -> AnalysisRecordOutput:
        return AnalysisRecordOutput(
            id=record.id,
            user_id=record.user_id,
            chart_id=record.chart_id,
            analysis_type=record.analysis_type,
            palace_name=record.palace_name,
            prompt_version=record.prompt_version,
            result_text=record.result_text,
            tokens_used=record.tokens_used,
            created_at=record.created_at,
        )
