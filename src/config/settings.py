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
    sendgrid_api_key: str | None = Field(default=None, alias="SENDGRID_API_KEY")
    sendgrid_from_email: str = Field(
        default="noreply@example.com",
        alias="SENDGRID_FROM_EMAIL",
    )
    sendgrid_confirmation_template_id: str | None = Field(
        default=None,
        alias="SENDGRID_CONFIRMATION_TEMPLATE_ID",
    )
    sendgrid_email_verification_template_id: str | None = Field(
        default=None,
        alias="SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID",
    )
    sendgrid_password_reset_template_id: str | None = Field(
        default=None,
        alias="SENDGRID_PASSWORD_RESET_TEMPLATE_ID",
    )
    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")
    email_verification_token_expire_hours: int = Field(
        default=24,
        alias="EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS",
    )
    password_reset_token_expire_minutes: int = Field(
        default=30,
        alias="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
    )
    remember_me_jwt_expiry_days: int = Field(
        default=30,
        alias="REMEMBER_ME_JWT_EXPIRY_DAYS",
    )
    jwt_remember_me_expiry: int | None = Field(
        default=None,
        alias="JWT_REMEMBER_ME_EXPIRY",
    )
    auth0_domain: str | None = Field(default=None, alias="AUTH0_DOMAIN")
    auth0_client_id: str | None = Field(default=None, alias="AUTH0_CLIENT_ID")
    auth0_client_secret: str | None = Field(default=None, alias="AUTH0_CLIENT_SECRET")
    auth0_audience: str | None = Field(default=None, alias="AUTH0_AUDIENCE")
    auth0_webhook_secret: str | None = Field(
        default=None,
        alias="AUTH0_WEBHOOK_SECRET",
    )

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

    @property
    def effective_remember_me_jwt_expiry(self) -> int:
        """Return extended JWT lifetime in seconds for remember-me sessions."""
        if self.jwt_remember_me_expiry is not None:
            return self.jwt_remember_me_expiry
        return self.remember_me_jwt_expiry_days * 24 * 60 * 60


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
