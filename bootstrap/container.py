from __future__ import annotations

from typing import Optional

from core.config.settings import load_settings, Settings
from core.logging.logger import get_logger, Logger
from core.lifecycle import Lifecycle

# NOTE:
# All existing imports for services/pools/etc. are preserved
# (omitted here for brevity but MUST remain in your real file)


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
        self._logger: Optional[Logger] = None
        self._lifecycle: Optional[Lifecycle] = None

        # other dependencies (pools, services, etc.)
        # remain unchanged

    # ------------------------------------------------------------------
    # 🔥 BACKWARD-COMPAT API (FIX)
    # ------------------------------------------------------------------
    def init_config(self) -> None:
        """
        Backward-compatible initialization method.

        Previously used by startup lifecycle:
            self._c.init_config()

        Now acts as a shim over new lazy-loading config.
        """
        if self._settings is None:
            self._settings = load_settings()

    # ------------------------------------------------------------------
    # EXISTING INITIALIZATION FLOW (unchanged)
    # ------------------------------------------------------------------
    def init_all(self) -> None:
        """
        Full container initialization.

        Keeps existing architecture intact.
        """
        self.init_config()

        if self._logger is None:
            self._logger = get_logger()

        if self._lifecycle is None:
            self._lifecycle = Lifecycle()

        # other init_* calls remain unchanged
        # e.g. init_db(), init_redis(), init_services()

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------
    @property
    def settings(self) -> Settings:
        if self._settings is None:
            self._settings = load_settings()
        return self._settings

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = get_logger()
        return self._logger

    @property
    def lifecycle(self) -> Lifecycle:
        if self._lifecycle is None:
            self._lifecycle = Lifecycle()
        return self._lifecycle

    # ------------------------------------------------------------------
    # (other properties unchanged)
    # ------------------------------------------------------------------
