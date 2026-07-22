"""用户与会员模型（Sprint 8）。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

MembershipLevel = Literal["free", "basic", "premium"]


class ProfileOutput(BaseModel):
    id: UUID
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    membership: MembershipLevel = "free"
    ai_quota: int = 3
    created_at: datetime
    updated_at: datetime


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(default=None, max_length=64)
    avatar_url: Optional[str] = Field(default=None, max_length=512)


class AuthUser(BaseModel):
    id: UUID
    email: Optional[str] = None
