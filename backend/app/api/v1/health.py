from fastapi import APIRouter

from app.database.database import database_status

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """服务健康检查，用于部署监控与本地调试。"""
    db = database_status()
    ready = db["ready"]
    return {
        "status": "ok" if ready else "degraded",
        "service": "ziwei-ai-api",
        "database": db,
    }
