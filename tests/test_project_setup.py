"""Verify the FastAPI backend project scaffolding exists."""

from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = WORKSPACE_ROOT / "backend"


def test_backend_package_structure() -> None:
    expected_paths = [
        BACKEND_ROOT / "pyproject.toml",
        BACKEND_ROOT / "app" / "main.py",
        BACKEND_ROOT / "app" / "core" / "config.py",
        BACKEND_ROOT / "app" / "api" / "v1" / "router.py",
        BACKEND_ROOT / "app" / "common" / "guards" / "jwt.py",
        BACKEND_ROOT / "app" / "common" / "utils" / "token.py",
        BACKEND_ROOT / "app" / "middleware" / "logging.py",
        BACKEND_ROOT / "app" / "middleware" / "rate_limiter.py",
        BACKEND_ROOT / "app" / "exceptions" / "handlers.py",
        BACKEND_ROOT / "app" / "db" / "session.py",
    ]
    for path in expected_paths:
        assert path.is_file(), f"Expected file missing: {path}"
