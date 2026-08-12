from app.core.config import settings


def test_settings_load_test_database_url():
    expected_url = 'postgresql+asyncpg://postgres:1234@localhost:5432/mydb'
    assert settings.DATABASE_URL == expected_url
