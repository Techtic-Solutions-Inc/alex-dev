from pydantic_settings import BaseSettings, SettingsConfigDict


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
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    JWT_SECRET: str = "your_secret_key"
    JWT_EXPIRY: int = 30
    JWT_REMEMBER_ME_EXPIRY: int = 43200
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT: str = "100/minute"


settings = Settings()
