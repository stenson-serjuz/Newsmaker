from bootstrap.container import Container
from core.types.protocols import LoggerProtocol


class Wiring:
    def __init__(self, container: Container) -> None:
        self._container = container

    def get_logger(self) -> LoggerProtocol:
        return self._container.logger_factory.create()
