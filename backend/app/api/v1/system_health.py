"""System health API — V1.3。"""

from __future__ import annotations

from fastapi import APIRouter

from app.knowledge.health.knowledge_health import KnowledgeHealthChecker

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/knowledge-health")
def knowledge_health() -> dict:
    return KnowledgeHealthChecker.check()
