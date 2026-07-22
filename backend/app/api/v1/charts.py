"""命盘 API 路由。"""

from fastapi import APIRouter, HTTPException

from app.models.birth import BirthInput, ChartGenerateRequest
from app.models.chart import ChartOutput
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.exceptions import UnsupportedCalendarError, ZiweiEngineError

router = APIRouter(prefix="/charts", tags=["charts"])


@router.post("/generate", response_model=ChartOutput)
async def generate_chart(request: ChartGenerateRequest) -> ChartOutput:
    """生成紫微斗数命盘（Chart JSON V1.0 Final）。"""
    try:
        return ChartGenerator.generate(request)
    except UnsupportedCalendarError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ZiweiEngineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/generate/birth-input", response_model=ChartOutput)
async def generate_chart_from_birth_input(birth: BirthInput) -> ChartOutput:
    """使用 BirthInput 标准格式排盘。"""
    request = ChartGenerateRequest.from_birth_input(birth)
    return await generate_chart(request)
