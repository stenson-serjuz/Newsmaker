from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime settings (typed).

    - Preserves existing config model
    - Provides driver-specific DSN normalization
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")

    # ------------------------------------------------------------------
    # 🔥 SQLAlchemy DSN (async dialect)
    # ------------------------------------------------------------------
    def sqlalchemy_database_dsn(self) -> str:
        """
        Normalize DSN for SQLAlchemy async engine.

        Required format:
            postgresql+asyncpg://
        """
        dsn = self.postgres_dsn.strip()

        if dsn.startswith("postgresql+asyncpg://"):
            return dsn

        if dsn.startswith("postgresql://"):
            return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)

        if dsn.startswith("postgresql+psycopg2://"):
            return dsn.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

        raise ValueError(f"Invalid POSTGRES_DSN for SQLAlchemy: {dsn}")

    # ------------------------------------------------------------------
    # 🔥 asyncpg DSN (raw driver)
    # ------------------------------------------------------------------
    def asyncpg_database_dsn(self) -> str:
        """
        Normalize DSN for asyncpg.create_pool()

        Required format:
            postgresql://  OR postgres://
        """
        dsn = self.postgres_dsn.strip()

        if dsn.startswith("postgresql://") or dsn.startswith("postgres://"):
            return dsn

        if dsn.startswith("postgresql+asyncpg://"):
            return dsn.replace("postgresql+asyncpg://", "postgresql://", 1)

        if dsn.startswith("postgresql+psycopg2://"):
            return dsn.replace("postgresql+psycopg2://", "postgresql://", 1)

        raise ValueError(f"Invalid POSTGRES_DSN for asyncpg: {dsn}")


# ----------------------------------------------------------------------
# 🔥 BACKWARD-COMPAT LOADER
# ----------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_settings() -> Settings:
    return Settings()
