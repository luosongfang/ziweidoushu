"""正式紫微AI分析接口 — POST /api/ziwei/analyze。"""

from __future__ import annotations

from fastapi import APIRouter

from app.ziwei_ai.report_generator import ZiweiAiReportGenerator
from app.ziwei_ai.schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter(prefix="/api/ziwei", tags=["ziwei-ai"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_ziwei(body: AnalyzeRequest) -> AnalyzeResponse:
    """
    紫微AI分析引擎 V1：
    问题分类 → 知识库 → 规则分析 → 安全过滤 → DeepSeek 报告。
    """
    return await ZiweiAiReportGenerator.generate(
        chart_data=body.chartData,
        question=body.question,
    )
