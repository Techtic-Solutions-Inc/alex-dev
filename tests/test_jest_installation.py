"""Tests ensuring the Python test runner dependencies are available."""

import importlib.util
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent / "backend"


def test_pytest_is_installed_in_backend_venv() -> None:
    result = subprocess.run(
        [str(BACKEND_ROOT / ".venv" / "bin" / "python"), "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "pytest" in result.stdout


def test_required_test_dependencies_are_importable() -> None:
    for module_name in ("pytest", "httpx", "fastapi", "pymongo"):
        assert importlib.util.find_spec(module_name) is not None, f"{module_name} is not installed"

    assert sys.version_info >= (3, 11)
