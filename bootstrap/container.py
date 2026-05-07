from __future__ import annotations

from typing import Optional, Any

from core.config.settings import load_settings, Settings
from core.logging.logger import get_logger

# 🔥 REAL EXISTING INFRASTRUCTURE (reuse, do NOT invent)
from infrastructure.db.pool import PostgresPool


class Container:
    """
    DI Container.

    - Holds application dependencies
    - Owns lifecycle-bound resources
    - Provides backward-compatible init methods
    """

    def __init__(self) -> None:
        # core
        self._settings: Optional[Settings] = None
        self._logger: Optional[Any] = None

        # 🔥 REAL postgres dependency (lazy)
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
        Initialize real infrastructure connections.

        Previously removed → now restored properly.
        """
        if self._postgres is None:
            # ensure dependencies exist
            settings = self.settings
            logger = self.logger

            # 🔥 REAL wiring (no fake objects)
            self._postgres = PostgresPool(
                dsn=settings.database_dsn(),
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

    # 🔥 REQUIRED BY STARTUP (CRITICAL FIX)
    @property
    def postgres(self) -> PostgresPool:
        """
        Real postgres dependency expected by startup:

        startup.py →
            await self._c.postgres.start()
        """
        if self._postgres is None:
            self.init_connections()

        # safety guard
        if self._postgres is None:
            raise RuntimeError("PostgresPool not initialized")

        return self._postgres
