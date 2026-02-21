"""Application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/webintel",
    )

    @property
    def database_url_sync(self) -> str:
        """Return a synchronous SQLAlchemy URL for Alembic migrations."""

        if "+asyncpg" in self.database_url:
            return self.database_url.replace("+asyncpg", "+psycopg")
        return self.database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings instance."""

    return Settings()
