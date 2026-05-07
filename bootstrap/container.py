from __future__ import annotations

from typing import Optional, Any

from core.config.settings import load_settings, Settings
from core.logging.logger import get_logger


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

        # NOTE:
        # connection objects (db/redis) are initialized elsewhere in current architecture

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
        """
        Legacy alias → delegates to logging init
        """
        self.init_logging()

    def init_connections(self) -> None:
        """
        Backward-compatible shim for startup orchestration.

        In current architecture:
        - connection initialization is handled lazily or via other layers
        - no explicit container-level init method exists

        This method preserves startup contract without duplicating logic.
        """
        # no-op by design (connections are initialized in their respective layers)
        return None

    # ------------------------------------------------------------------
    # INIT FLOW
    # ------------------------------------------------------------------
    def init_all(self) -> None:
        self.init_config()
        self.init_logging()

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
