import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    PASSWORD_RESET_FRONTEND_URL: str = os.getenv(
        "PASSWORD_RESET_FRONTEND_URL",
        "http://localhost:5173/reset-password",
    )


settings = Settings()
