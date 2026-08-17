"""Environment-driven application settings."""

import json
from functools import lru_cache
from typing import Any, Literal, Self

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings loaded from environment variables or an optional .env file."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=False,
        populate_by_name=True,
    )

    app_name: str = Field(default="Backend API", description="Application name displayed in OpenAPI.")
    app_env: Literal["development", "test", "staging", "production"] = Field(
        default="development",
        validation_alias=AliasChoices("app_env", "APP_ENV", "ENVIRONMENT"),
    )
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/backend"
    test_database_url: str | None = None
    jwt_secret: str = Field(
        default="change-this-development-secret-before-deploying",
        repr=False,
    )
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = Field(default=3600, ge=30, le=86_400)
    jwt_refresh_expiry: int = Field(default=86_400, ge=300, le=2_592_000)
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit_requests: int = Field(default=100, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_env(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get("jwt_expiry") is None and data.get("JWT_EXPIRY") is None:
            minutes = data.get("access_token_expire_minutes") or data.get(
                "ACCESS_TOKEN_EXPIRE_MINUTES"
            )
            if minutes is not None:
                data["jwt_expiry"] = int(minutes) * 60
        return data

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value

        stripped = value.strip()
        if stripped in {"*", "[*]"}:
            return ["*"]
        if stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                inner = stripped.strip("[]")
                parsed = [part.strip().strip('"').strip("'") for part in inner.split(",") if part.strip()]
            if isinstance(parsed, list):
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_secrets_for_environment(self) -> Self:
        if self.app_env != "test" and len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters outside test environments.")
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance for dependency-free application configuration."""
    return Settings()
