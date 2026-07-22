from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_PLACEHOLDER_MARKERS = (
    "[YOUR-PASSWORD]",
    "[your-password]",
    "xxxxxxxxx",
    "your_password",
    "changeme",
)


class Settings(BaseSettings):
    """应用配置，从环境变量或 backend/.env 读取。"""

    app_name: str = "紫微AI API"
    debug: bool = True
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: str = "http://localhost:3000"

    database_url: str = Field(
        default="sqlite:///./ziwei_dev.db",
        validation_alias="DATABASE_URL",
    )
    supabase_url: str = Field(default="", validation_alias="SUPABASE_URL")
    supabase_key: str = Field(default="", validation_alias="SUPABASE_KEY")
    supabase_anon_key: str = Field(default="", validation_alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(
        default="",
        validation_alias="SUPABASE_SERVICE_ROLE_KEY",
    )
    auth_dev_mode: bool = True
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def effective_supabase_anon_key(self) -> str:
        return self.supabase_key or self.supabase_anon_key

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")

    @property
    def database_is_configured(self) -> bool:
        """DATABASE_URL 是否已填写真实连接信息。"""
        if not self.is_postgres:
            return True
        lowered = self.database_url.lower()
        return not any(marker.lower() in lowered for marker in _PLACEHOLDER_MARKERS)


settings = Settings()
