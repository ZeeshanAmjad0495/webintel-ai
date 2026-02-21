"""Application configuration settings powered by pydantic-settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and `.env` files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "WebIntel AI"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    debug: bool = False
    log_level: str = Field(default="INFO", description="Application log verbosity level.")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./webintel.db",
        description="Async SQLAlchemy connection URL.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings object for import-safe configuration access."""
    return Settings()
