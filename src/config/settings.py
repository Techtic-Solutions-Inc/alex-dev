"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://user:password@localhost/dbname"
    database_url_test: str | None = None

    jwt_secret: str = "mysecretkey"
    jwt_secret_key: str | None = None
    jwt_expiry: int = 3600
    access_token_expire_minutes: int | None = None
    jwt_algorithm: str = "HS256"

    log_level: str = "INFO"
    environment: str = "development"
    cors_origins: str = "*"

    @property
    def effective_jwt_secret(self) -> str:
        """Return the configured JWT secret, supporting legacy env names."""
        return self.jwt_secret_key or self.jwt_secret

    @property
    def effective_jwt_expiry(self) -> int:
        """Return token expiry in seconds."""
        if self.access_token_expire_minutes is not None:
            return self.access_token_expire_minutes * 60
        return self.jwt_expiry

    @model_validator(mode="after")
    def default_test_database_url(self) -> "Settings":
        """Use the primary database URL when a dedicated test URL is not provided."""
        if self.database_url_test is None:
            self.database_url_test = self.database_url
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
