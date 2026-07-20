from enum import Enum
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "User Authentication System"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = ""

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/app_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    RATE_LIMIT: str = "100/minute"
    RATE_LIMIT_ENABLED: bool = True

    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@example.com"

    PUBLIC_PATHS: list[str] = [
        "/",
        "/health",
        "/login",
        "/auth/register",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        return str(value).lower()

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT.value

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == Environment.TESTING.value

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION.value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
