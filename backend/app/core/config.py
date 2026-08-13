from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_files() -> tuple[str, ...]:
    """Load workspace and backend env files (later entries override earlier)."""
    backend_dir = Path(__file__).resolve().parent.parent
    root_dir = backend_dir.parent
    candidates = (
        root_dir / ".env.test",
        root_dir / ".env",
        backend_dir / ".env.test",
        backend_dir / ".env",
    )
    return tuple(str(path) for path in candidates if path.is_file())


def sync_database_url(url: str) -> str:
    """Return a synchronous driver URL for Alembic and sync SQLAlchemy engines."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_resolve_env_files() or ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    JWT_SECRET: str = "your_secret_key"
    JWT_EXPIRY: int = 30
    JWT_REMEMBER_ME_EXPIRY: int = 43200
    PASSWORD_RESET_TOKEN_EXPIRY: int = 30
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT: str = "100/minute"
    FRONTEND_URL: str = "http://localhost:3000"
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@example.com"
    SENDGRID_FROM_NAME: str = "Support"
    GOOGLE_ANALYTICS_MEASUREMENT_ID: str = ""
    GOOGLE_ANALYTICS_API_SECRET: str = ""
    GOOGLE_ANALYTICS_ENABLED: bool = False
    STRIPE_SECRET_KEY: str = ""
    STRIPE_ENABLED: bool = False


settings = Settings()
