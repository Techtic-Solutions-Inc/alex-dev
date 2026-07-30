from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Agentwise API"
    database_url: str = "sqlite:///./app.db"

    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""
    auth0_connection: str = "Username-Password-Authentication"

    dashboard_url: str = "/dashboard"

    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    rate_limit_strategy: str = "ip_and_path"
    rate_limit_excluded_paths: list[str] = ["/health"]

    @field_validator("rate_limit_strategy")
    @classmethod
    def validate_rate_limit_strategy(cls, value: str) -> str:
        valid_strategies = {"ip", "user", "ip_and_path"}
        if value not in valid_strategies:
            raise ValueError(
                f"rate_limit_strategy must be one of: {', '.join(sorted(valid_strategies))}"
            )
        return value

    @field_validator("rate_limit_excluded_paths", mode="before")
    @classmethod
    def parse_excluded_paths(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [path.strip() for path in value.split(",") if path.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
