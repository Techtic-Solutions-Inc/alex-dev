from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Agentwise API"
    debug: bool = False

    database_url: str = "sqlite:///./app.db"

    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""
    auth0_connection: str = "Username-Password-Authentication"

    dashboard_redirect_url: str = "/dashboard"


@lru_cache
def get_settings() -> Settings:
    return Settings()
