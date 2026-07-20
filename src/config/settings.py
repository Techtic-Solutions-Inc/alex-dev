"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central application settings."""

    def __init__(self) -> None:
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            "sqlite:///./app.db",
        )
        self.JWT_SECRET_KEY: str = os.getenv(
            "JWT_SECRET_KEY",
            "dev-secret-key-change-in-production",
        )
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
        self.SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
        self.SENDGRID_FROM_EMAIL: str = os.getenv(
            "SENDGRID_FROM_EMAIL",
            "noreply@example.com",
        )
        self.APP_NAME: str = os.getenv("APP_NAME", "AI Assistant")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
