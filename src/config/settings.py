from pydantic import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str
    sendgrid_api_key: str
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()