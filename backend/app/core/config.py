"""应用核心配置（Phase 2）。"""

from app.config import settings as app_settings


class Settings:
    """扩展配置 — 兼容 Phase 2 目录规范。"""

    app_name: str = app_settings.app_name
    debug: bool = app_settings.debug
    database_url: str = getattr(app_settings, "database_url", "sqlite:///./ziwei_dev.db")
    backend_cors_origins: str = app_settings.backend_cors_origins


settings = Settings()

# 若主配置已扩展 database_url，同步读取
if hasattr(app_settings, "database_url"):
    settings.database_url = app_settings.database_url  # type: ignore[attr-defined]
