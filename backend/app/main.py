from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.chart_api import router as chart_engine_router
from app.api.v1.health import router as health_router
from app.api.v1.charts import router as charts_router
from app.api.v1.verification import router as verification_router
from app.api.v1.analyses import router as analyses_router
from app.api.v1.me import router as me_router
from app.api.v1.saved_charts import router as saved_charts_router
from app.api.v1.membership import router as membership_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 — 初始化种子数据（表结构由 Alembic 管理）。"""
    try:
        from app.database.database import check_database_connection, init_db

        if check_database_connection():
            init_db()
    except Exception:
        pass
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
app.include_router(health_router, prefix="/api/v1")
app.include_router(charts_router, prefix="/api/v1")
app.include_router(verification_router, prefix="/api/v1")
app.include_router(analyses_router, prefix="/api/v1")
app.include_router(me_router, prefix="/api/v1")
app.include_router(saved_charts_router, prefix="/api/v1")
app.include_router(membership_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "紫微AI API", "version": "0.1.0"}
