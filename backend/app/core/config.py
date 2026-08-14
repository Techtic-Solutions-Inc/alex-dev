from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_files() -> tuple[str, ...]:
    """Load workspace and backend env files (later entries override earlier)."""
    backend_dir = Path(__file__).resolve().parent.parent.parent
    root_dir = backend_dir.parent
    candidates = (
        root_dir / ".env.test",
        root_dir / ".env",
        backend_dir / ".env.test",
        backend_dir / ".env",
    )
    return tuple(str(path) for path in candidates if path.is_file())


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_resolve_env_files() or ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Backend API"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "mydatabase"
    TEST_MONGODB_URL: str = "mongodb://localhost:27017"
    TEST_DB_NAME: str = "mydatabase_test"
    AERICH_DATABASE_URL: str = "sqlite://app/db/migrations/aerich.db"

    JWT_SECRET: str = "your_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY: int = 30
    JWT_REFRESH_EXPIRY: int = 10080

    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT: str = "100/minute"


settings = Settings()
