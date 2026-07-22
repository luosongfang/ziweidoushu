"""用户 Profile 服务（Sprint 8）。"""

from __future__ import annotations

from uuid import UUID

from app.db.repository import Repository, get_repository
from app.models.user import AuthUser, ProfileOutput, ProfileUpdateRequest


class ProfileService:
    @classmethod
    def get_me(cls, user: AuthUser, repo: Repository | None = None) -> ProfileOutput:
        repository = repo or get_repository()
        profile = repository.ensure_profile(user.id, user.email)
        return cls._to_output(profile)

    @classmethod
    def update_me(
        cls,
        user: AuthUser,
        body: ProfileUpdateRequest,
        repo: Repository | None = None,
    ) -> ProfileOutput:
        repository = repo or get_repository()
        profile = repository.update_profile(
            user.id,
            display_name=body.display_name,
            avatar_url=body.avatar_url,
        )
        return cls._to_output(profile)

    @staticmethod
    def _to_output(profile) -> ProfileOutput:
        return ProfileOutput(
            id=profile.id,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
            membership=profile.membership,
            ai_quota=profile.ai_quota,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
