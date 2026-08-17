"""Tests for lint/format tooling configuration."""

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent / "backend"


def test_ruff_configuration_exists() -> None:
    pyproject = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.ruff" in pyproject
    assert "select" in pyproject
