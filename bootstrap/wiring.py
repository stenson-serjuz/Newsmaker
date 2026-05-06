from bootstrap.container import Container
from core.types.protocols import LoggerProtocol


class Wiring:
    """
    Wiring layer responsibility:

    - assemble dependency graph
    - provide ready-to-use application services
    - isolate container from business logic
    - enable future module-based wiring (per bounded context)
    """

    def __init__(self, container: Container) -> None:
        self._container = container

    def get_logger(self) -> LoggerProtocol:
        return self._container.logger_factory.create()
