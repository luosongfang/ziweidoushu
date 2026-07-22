"""内存存储 — 开发/测试用（Sprint 8）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class StoredProfile:
    id: UUID
    display_name: str | None = None
    avatar_url: str | None = None
    membership: str = "free"
    ai_quota: int = 3
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)


@dataclass
class StoredChart:
    id: UUID
    user_id: UUID
    name: str
    birth_datetime: datetime
    gender: str
    calendar_type: str
    timezone: str
    chart_data: dict[str, Any]
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)


@dataclass
class StoredAnalysis:
    id: UUID
    user_id: UUID
    chart_id: UUID
    analysis_type: str
    palace_name: str | None
    prompt_version: str
    input_context: dict[str, Any]
    result_text: str
    tokens_used: int
    created_at: datetime = field(default_factory=_utcnow)


@dataclass
class StoredOrder:
    id: UUID
    user_id: UUID
    plan_id: str
    amount_cents: int
    currency: str
    status: str
    payment_provider: str | None
    payment_ref: str | None
    created_at: datetime = field(default_factory=_utcnow)
    paid_at: datetime | None = None


class MemoryStore:
    """进程内存储，Supabase 未配置时使用。"""

    _instance: "MemoryStore | None" = None

    def __init__(self) -> None:
        self.profiles: dict[UUID, StoredProfile] = {}
        self.charts: dict[UUID, StoredChart] = {}
        self.analyses: dict[UUID, StoredAnalysis] = {}
        self.orders: dict[UUID, StoredOrder] = {}

    @classmethod
    def get(cls) -> "MemoryStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None


def get_memory_store() -> MemoryStore:
    return MemoryStore.get()
