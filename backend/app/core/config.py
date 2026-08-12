from pydantic_settings import BaseSettings, SettingsConfigDict


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
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT: str = "100/minute"


settings = Settings()
