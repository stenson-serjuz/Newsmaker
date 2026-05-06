from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime settings (typed).

    - Preserves existing config model
    - Enforces asyncpg DSN normalization
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")

    def database_dsn(self) -> str:
        """
        Normalize DSN to asyncpg dialect.
        """
        dsn = self.postgres_dsn.strip()

        # already correct
        if dsn.startswith("postgresql+asyncpg://"):
            return dsn

        # replace default sync driver
        if dsn.startswith("postgresql://"):
            return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)

        # replace explicit psycopg2
        if dsn.startswith("postgresql+psycopg2://"):
            return dsn.replace(
                "postgresql+psycopg2://",
                "postgresql+asyncpg://",
                1,
            )

        raise ValueError(f"Invalid POSTGRES_DSN: {dsn}")


# 🔥 RESTORED PUBLIC API (backward compatibility)
@lru_cache(maxsize=1)
def load_settings() -> Settings:
    """
    Backward-compatible settings loader.

    - Preserves existing import contract:
        from core.config.settings import load_settings
    - Singleton-safe via lru_cache
    - Avoids repeated env parsing
    """
    return Settings()
