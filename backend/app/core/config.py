from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Budget Tracker API"
    api_prefix: str = "/api"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./budget.db"
    allowed_origins: str = "http://localhost:5173"
    rate_limit_default: str = "100/minute"
    gold_price_api_url: str | None = None
    gold_price_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
