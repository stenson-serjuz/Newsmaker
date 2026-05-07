from __future__ import annotations

from typing import Optional, Any

from core.config.settings import load_settings, Settings
from core.logging.logger import get_logger
from core.lifecycle import Lifecycle


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
        self._lifecycle: Optional[Lifecycle] = None

        # other dependencies (unchanged)

    # ------------------------------------------------------------------
    # BACKWARD-COMPAT API
    # ------------------------------------------------------------------
    def init_config(self) -> None:
        if self._settings is None:
            self._settings = load_settings()

    # ------------------------------------------------------------------
    # INIT FLOW
    # ------------------------------------------------------------------
    def init_all(self) -> None:
        self.init_config()

        if self._logger is None:
            self._logger = get_logger()

        if self._lifecycle is None:
            self._lifecycle = Lifecycle()

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
    def lifecycle(self) -> Lifecycle:
        if self._lifecycle is None:
            self._lifecycle = Lifecycle()
        return self._lifecycle
