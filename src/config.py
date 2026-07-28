from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./app.db"
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""
    auth0_connection: str = "Username-Password-Authentication"
    dashboard_url: str = "/dashboard"
    auth0_token_url: str | None = None

    @property
    def resolved_auth0_token_url(self) -> str:
        if self.auth0_token_url:
            return self.auth0_token_url
        if not self.auth0_domain:
            return ""
        return f"https://{self.auth0_domain}/oauth/token"


@lru_cache
def get_settings() -> Settings:
    return Settings()
