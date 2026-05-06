from typing import Optional

from core.config.runtime import RuntimeConfig, build_runtime_config
from core.logging.logger import configure_logging
from core.logging.factory import LoggerFactory


class Container:
    def __init__(self) -> None:
        self._config: Optional[RuntimeConfig] = None
        self._logger_factory: Optional[LoggerFactory] = None

    def init_config(self) -> None:
        self._config = build_runtime_config()

    def init_logging(self) -> None:
        assert self._config is not None
        configure_logging(self._config.get().log_level)

    def init_logger_factory(self) -> None:
        self._logger_factory = LoggerFactory()

    @property
    def config(self) -> RuntimeConfig:
        assert self._config is not None
        return self._config

    @property
    def logger_factory(self) -> LoggerFactory:
        assert self._logger_factory is not None
        return self._logger_factory
