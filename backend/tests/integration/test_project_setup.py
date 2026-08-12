from app.core.config import settings


def test_settings_load_test_database_url() -> None:
    expected_url = "postgresql+psycopg2://postgres:1234@localhost:5432/mydb"
    assert settings.DATABASE_URL == expected_url
