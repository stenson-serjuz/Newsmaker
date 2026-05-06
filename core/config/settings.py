from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime settings (typed).
    Ensures DSN always uses asyncpg driver.
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

        # replace incorrect sync driver
        if dsn.startswith("postgresql://"):
            return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)

        # fallback safety
        if "postgresql+psycopg2://" in dsn:
            return dsn.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

        raise ValueError(f"Invalid POSTGRES_DSN: {dsn}")
