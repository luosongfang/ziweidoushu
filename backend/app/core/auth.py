"""认证与用户上下文（Sprint 8）。"""

from __future__ import annotations

from uuid import UUID

import httpx
from fastapi import Depends, Header, HTTPException

from app.config import settings
from app.models.user import AuthUser


async def _verify_supabase_token(token: str) -> AuthUser:
    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="Supabase 未配置，无法验证登录")

    url = f"{settings.supabase_url.rstrip('/')}/auth/v1/user"
    api_key = (
        settings.supabase_service_role_key
        or settings.effective_supabase_anon_key
    )
    if not api_key:
        raise HTTPException(status_code=503, detail="Supabase API Key 未配置")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}", "apikey": api_key},
        )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="无效或已过期的登录凭证")

    data = response.json()
    return AuthUser(id=UUID(data["id"]), email=data.get("email"))


def _parse_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


async def get_optional_user(
    authorization: str | None = Header(default=None),
    x_dev_user_id: str | None = Header(default=None, alias="X-Dev-User-Id"),
) -> AuthUser | None:
    """可选认证 — 未登录返回 None。"""
    if settings.auth_dev_mode and x_dev_user_id:
        try:
            return AuthUser(id=UUID(x_dev_user_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="X-Dev-User-Id 格式无效") from exc

    token = _parse_bearer(authorization)
    if not token:
        return None

    if settings.supabase_url:
        return await _verify_supabase_token(token)

    if settings.auth_dev_mode:
        try:
            return AuthUser(id=UUID(token))
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="开发模式下 token 需为 UUID") from exc

    raise HTTPException(status_code=503, detail="认证服务未配置")


async def get_current_user(user: AuthUser | None = Depends(get_optional_user)) -> AuthUser:
    """必须登录。"""
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user
