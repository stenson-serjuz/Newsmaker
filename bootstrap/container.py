from __future__ import annotations

from typing import Optional, Any

from core.config.settings import load_settings, Settings
from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool


class Container:
    def __init__(self) -> None:
        self._settings: Optional[Settings] = None
        self._logger: Optional[Any] = None
        self._postgres: Optional[PostgresPool] = None

    # ------------------------------------------------------------------
    # BACKWARD-COMPAT API
    # ------------------------------------------------------------------
    def init_config(self) -> None:
        if self._settings is None:
            self._settings = load_settings()

    def init_logging(self) -> None:
        if self._logger is None:
            self._logger = get_logger()

    def init_logger_factory(self) -> None:
        self.init_logging()

    def init_connections(self) -> None:
        """
        Restore real postgres wiring with CORRECT asyncpg DSN
        """
        if self._postgres is None:
            settings = self.settings
            logger = self.logger

            # 🔥 FIX: use asyncpg DSN, NOT sqlalchemy DSN
            self._postgres = PostgresPool(
                dsn=settings.asyncpg_database_dsn(),
                logger=logger,
            )

    # ------------------------------------------------------------------
    # INIT FLOW
    # ------------------------------------------------------------------
    def init_all(self) -> None:
        self.init_config()
        self.init_logging()
        self.init_connections()

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------
    @property
    def settings(self) -> Settings:
        if self._settings is None:
            self._settings = load_settings()
        return self._settings

    @property
    def logger(self) -> Any:
        if self._logger is None:
            self._logger = get_logger()
        return self._logger

    @property
    def postgres(self) -> PostgresPool:
        if self._postgres is None:
            self.init_connections()

        if self._postgres is None:
            raise RuntimeError("PostgresPool not initialized")

        return self._postgres
