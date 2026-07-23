from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.chart_api import router as chart_engine_router
from app.api.ai_test import router as ai_test_router
from app.api.ziwei_analyze import router as ziwei_analyze_router
from app.api.v1.health import router as health_router
from app.api.v1.charts import router as charts_router
from app.api.v1.verification import router as verification_router
from app.api.v1.analyses import router as analyses_router
from app.api.v1.me import router as me_router
from app.api.v1.saved_charts import router as saved_charts_router
from app.api.v1.membership import router as membership_router
from app.api.v1.knowledge_analyze import router as knowledge_analyze_router
from app.api.v1.decision_feedback import router as decision_feedback_router
from app.api.v1.evaluation import router as evaluation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 — 初始化数据库表结构与种子数据。"""
    import logging

    from app.database.database import database_status, init_db

    logger = logging.getLogger("uvicorn.error")
    init_db()
    status = database_status()
    if status["ready"]:
        logger.info("Supabase/PostgreSQL 已连接，数据库就绪")
    elif settings.is_postgres and not status["configured"]:
        logger.error(
            "DATABASE_URL 未配置：请编辑 backend/.env 替换 [YOUR-PASSWORD] 后重启"
        )
    elif settings.is_postgres:
        logger.error("Supabase 连接失败：请检查 DATABASE_URL 密码与网络")
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chart_engine_router)
app.include_router(ai_test_router)
app.include_router(ziwei_analyze_router)
app.include_router(health_router, prefix="/api/v1")
app.include_router(charts_router, prefix="/api/v1")
app.include_router(verification_router, prefix="/api/v1")
app.include_router(analyses_router, prefix="/api/v1")
app.include_router(me_router, prefix="/api/v1")
app.include_router(saved_charts_router, prefix="/api/v1")
app.include_router(membership_router, prefix="/api/v1")
app.include_router(knowledge_analyze_router, prefix="/api/v1")
app.include_router(decision_feedback_router, prefix="/api/v1")
app.include_router(evaluation_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "紫微AI API", "version": "0.1.0"}
