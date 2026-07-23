"""AI 测试入口 — SiliconFlow 紫微分析（增量模块，不影响排盘）。"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field, model_validator

from app.ai.prompt import ZIWEI_SYSTEM_PROMPT, build_user_message
from app.ai.siliconflow_client import (
    SiliconFlowClient,
    SiliconFlowEmptyResponseError,
    SiliconFlowNotConfiguredError,
    SiliconFlowRequestError,
)

router = APIRouter(tags=["ai"])


class AiTestRequest(BaseModel):
    """请求体：支持 chartData（前端测试页）与 chart（兼容字段）。"""

    chartData: str = Field(default="", description="紫微命盘文本")
    chart: str = Field(default="", description="兼容字段，等同 chartData")
    prompt: str = Field(default="", description="可选附加说明")

    @model_validator(mode="after")
    def merge_chart_fields(self) -> "AiTestRequest":
        if not self.chartData.strip() and self.chart.strip():
            self.chartData = self.chart
        return self


class AiTestResponse(BaseModel):
    success: bool
    result: str | None = None
    model: str | None = None
    error: str | None = None


class AiStatusResponse(BaseModel):
    service: str = "SiliconFlow"
    model: str
    status: str


@router.get("/api/ai-status", response_model=AiStatusResponse)
async def ai_status() -> AiStatusResponse:
    """SiliconFlow 配置健康检查。"""
    model = SiliconFlowClient.get_model()
    if not SiliconFlowClient.is_configured():
        return AiStatusResponse(service="SiliconFlow", model=model, status="missing_key")
    return AiStatusResponse(service="SiliconFlow", model=model, status="ready")


@router.post("/api/ai-test", response_model=AiTestResponse)
async def ai_test(body: AiTestRequest) -> AiTestResponse:
    """调用 SiliconFlow，对命盘文本做人生规划参考分析。"""
    chart_data = body.chartData.strip()
    extra = body.prompt.strip()

    if not chart_data and not extra:
        return AiTestResponse(success=False, error="请提供命盘文本")

    if not SiliconFlowClient.is_configured():
        return AiTestResponse(success=False, error="AI服务未配置")

    messages = [
        {"role": "system", "content": ZIWEI_SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(chart_data or extra, extra if chart_data else "")},
    ]

    try:
        content = await SiliconFlowClient.chat(messages)
    except SiliconFlowNotConfiguredError:
        return AiTestResponse(success=False, error="AI服务未配置")
    except SiliconFlowEmptyResponseError:
        return AiTestResponse(success=False, error="AI返回为空")
    except SiliconFlowRequestError:
        return AiTestResponse(success=False, error="AI服务调用失败")

    return AiTestResponse(
        success=True,
        result=content,
        model=SiliconFlowClient.get_model(),
    )
