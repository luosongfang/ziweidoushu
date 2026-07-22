from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.charts import router as charts_router
from app.api.v1.verification import router as verification_router
from app.api.v1.analyses import router as analyses_router
from app.api.v1.me import router as me_router
from app.api.v1.saved_charts import router as saved_charts_router
from app.api.v1.membership import router as membership_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
