"""Typed, environment-driven application configuration."""

import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_files() -> tuple[str, ...]:
    """Return available environment files in increasing precedence order."""
    backend_dir = Path(__file__).resolve().parents[2]
    workspace_dir = backend_dir.parent
    candidates = [workspace_dir / ".env", backend_dir / ".env"]
    if os.getenv("APP_ENV", "development").lower() == "test":
        candidates.extend((workspace_dir / ".env.test", backend_dir / ".env.test"))
    return tuple(str(path) for path in candidates if path.is_file())


class Settings(BaseSettings):
    """Configuration shared by the API, authentication, and migrations."""

    model_config = SettingsConfigDict(
        env_file=_resolve_env_files() or ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Backend API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, ge=1)
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "app"
    MIGRATIONS_COLLECTION: str = "_migrations"
    MIGRATIONS_LOCK_COLLECTION: str = "_migration_locks"
    MIGRATION_LOCK_TIMEOUT_SECONDS: int = 60
    JWT_SECRET: str = "change-this-development-secret-before-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "backend-api"
    JWT_AUDIENCE: str = "backend-clients"
    JWT_EXPIRY_SECONDS: int = Field(default=3600, ge=60)
    JWT_REFRESH_EXPIRY_SECONDS: int = Field(default=86400, ge=300)
    EMAIL_VERIFICATION_EXPIRY_SECONDS: int = Field(default=86400, ge=300)
    SENDGRID_API_KEY: str | None = None
    SENDGRID_FROM_EMAIL: str | None = None
    EMAIL_VERIFICATION_URL: str = "http://localhost:3000/verify-email"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """Accept JSON arrays or comma-separated CORS origins."""
        if isinstance(value, str) and not value.lstrip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
