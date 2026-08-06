from src.config.settings import get_settings


def test_example() -> None:
    settings = get_settings()
    assert settings.effective_jwt_secret is not None
