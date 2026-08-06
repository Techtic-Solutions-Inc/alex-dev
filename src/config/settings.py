import os
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    database_url: str
    database_url_test: str

    @validator('database_url_test', pre=True, always=True)
    def validate_test_database_url(cls, v, values):
        if os.getenv("PYTEST_CURRENT_TEST") and v == values.get('database_url'):
            raise ValueError("DATABASE_URL_TEST must differ from DATABASE_URL when running tests")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()