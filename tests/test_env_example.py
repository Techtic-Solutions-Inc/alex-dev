"""Tests for the committed environment template."""

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def test_env_example_file_contains_required_keys() -> None:
    required_keys = [
        "DATABASE_URL",
        "JWT_SECRET",
        "JWT_EXPIRY",
        "JWT_REFRESH_EXPIRY",
        "APP_NAME",
        "APP_ENV",
        "DEBUG",
        "API_V1_PREFIX",
        "CORS_ORIGINS",
        "RATE_LIMIT_REQUESTS",
        "RATE_LIMIT_WINDOW_SECONDS",
    ]
    content = (WORKSPACE_ROOT / ".env.example").read_text(encoding="utf-8")
    for key in required_keys:
        assert key in content, f"{key} not found in .env.example"
