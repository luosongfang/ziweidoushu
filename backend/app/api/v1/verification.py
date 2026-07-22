"""验证 API。"""

from fastapi import APIRouter

from app.ziwei.verification.manager import VerificationManager

router = APIRouter(prefix="/verification", tags=["verification"])


@router.get("/reference")
async def run_reference_verification():
    """运行全部标准命盘验证（Sprint 6）。"""
    report = VerificationManager.run_reference_suite()
    return {
        "passed": report.passed,
        "rulesVersion": report.rules_version,
        "totalCharts": report.total_charts,
        "failedCharts": report.failed_charts,
        "message": report.message,
    }
