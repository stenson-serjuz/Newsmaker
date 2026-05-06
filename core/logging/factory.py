from core.logging.logger import get_logger
from core.types.protocols import LoggerProtocol


class LoggerFactory:
    def create(self) -> LoggerProtocol:
        return get_logger()
