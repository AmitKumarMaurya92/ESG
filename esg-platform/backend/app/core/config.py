
"""
ESG Intelligence & Carbon Accounting Platform
Core configuration module using Pydantic BaseSettings.
All configuration is sourced from environment variables.
"""

from functools import lru_cache
from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All secrets must be supplied via .env or environment — never hardcoded.
    """

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "ESG Intelligence Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── API ──────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ── Supabase ─────────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    # WARNING: Service role key must NEVER be sent to the frontend.
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = ""  # postgresql+asyncpg://...

    # ── JWT ──────────────────────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── AI / LLM ─────────────────────────────────────────────────────────────
    LLM_PROVIDER: str = "openai"  # openai | gemini | anthropic
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── Redis / Celery ───────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Storage ──────────────────────────────────────────────────────────────
    STORAGE_BUCKET: str = "esg-documents"

    # ── Frontend ─────────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"

    # ── Security ─────────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50  # Maximum file upload size in megabytes
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [
        "pdf", "png", "jpg", "jpeg", "csv", "xlsx", "docx"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    Uses lru_cache so .env is only parsed once per process lifetime.
    """
    return Settings()


# Convenience alias used throughout the application
settings = get_settings()
