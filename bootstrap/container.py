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

    # ------------------------------------------------------------------
    # BACKWARD-COMPAT API
    # ------------------------------------------------------------------
    def init_config(self) -> None:
        if self._settings is None:
            self._settings = load_settings()

    def init_logging(self) -> None:
        """
        Backward-compatible logging initializer.

        Previously used by startup lifecycle:
            self._c.init_logging()

        Now acts as a thin shim over get_logger().
        """
        if self._logger is None:
            self._logger = get_logger()

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
