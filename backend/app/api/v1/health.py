from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """服务健康检查，用于部署监控与本地调试。"""
    return {"status": "ok", "service": "ziwei-ai-api"}
