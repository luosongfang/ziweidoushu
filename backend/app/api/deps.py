"""FastAPI 依赖注入。"""

from app.core.auth import get_current_user, get_optional_user
from app.db.repository import Repository, get_repository

__all__ = ["get_current_user", "get_optional_user", "get_repository", "Repository"]
