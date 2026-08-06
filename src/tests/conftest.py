import pytest
from src.config.settings import settings

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    assert settings.database_url_test != settings.database_url, "DATABASE_URL_TEST must differ from DATABASE_URL"
    create_test_tables()
    yield
    # Do not drop tables on shared databases; use transactions or truncate instead
