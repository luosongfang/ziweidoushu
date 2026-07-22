"""用户 Profile API（Sprint 8）。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import AuthUser, ProfileOutput, ProfileUpdateRequest
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=ProfileOutput)
async def get_profile(user: AuthUser = Depends(get_current_user)) -> ProfileOutput:
    """获取当前用户 Profile（含会员等级与 AI 配额）。"""
    return ProfileService.get_me(user)


@router.patch("", response_model=ProfileOutput)
async def update_profile(
    body: ProfileUpdateRequest,
    user: AuthUser = Depends(get_current_user),
) -> ProfileOutput:
    """更新用户 Profile。"""
    return ProfileService.update_me(user, body)
