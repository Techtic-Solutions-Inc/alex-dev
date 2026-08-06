"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the FastAPI application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    database_url_test: str | None = Field(default=None, alias="DATABASE_URL_TEST")
    jwt_secret: str | None = Field(default=None, alias="JWT_SECRET")
    jwt_secret_key: str | None = Field(default=None, alias="JWT_SECRET_KEY")
    jwt_expiry: int | None = Field(default=None, alias="JWT_EXPIRY")
    access_token_expire_minutes: int | None = Field(
        default=None,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    secret_key: str | None = Field(default=None, alias="SECRET_KEY")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    @property
    def effective_jwt_secret(self) -> str:
        """Return the configured JWT signing secret."""
        return (
            self.jwt_secret_key
            or self.jwt_secret
            or self.secret_key
            or "changeme"
        )

    @property
    def effective_jwt_expiry(self) -> int:
        """Return JWT lifetime in seconds."""
        if self.jwt_expiry is not None:
            return self.jwt_expiry
        if self.access_token_expire_minutes is not None:
            return self.access_token_expire_minutes * 60
        return 3600


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
