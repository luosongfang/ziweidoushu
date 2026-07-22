from fastapi import APIRouter

from app.config import settings
from app.database.database import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """服务健康检查，用于部署监控与本地调试。"""
    db_ok = check_database_connection() if settings.is_postgres else True
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "ziwei-ai-api",
        "database": "connected" if db_ok else "unavailable",
    }
