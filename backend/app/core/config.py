"""Environment-driven application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings loaded from environment variables or an optional .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        enable_decoding=False,
    )

    app_name: str = Field(default="Backend API", description="Application name displayed in OpenAPI.")
    app_env: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/backend"
    test_database_url: str | None = None
    jwt_secret: str = Field(
        default="change-this-development-secret-before-deploying",
        min_length=32,
        repr=False,
    )
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = Field(default=3600, ge=60, le=86_400)
    jwt_refresh_expiry: int = Field(default=86_400, ge=300, le=2_592_000)
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit_requests: int = Field(default=100, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance for dependency-free application configuration."""
    return Settings()
