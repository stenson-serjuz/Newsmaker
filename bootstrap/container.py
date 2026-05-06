from typing import Optional

from core.config.runtime import RuntimeConfig
from core.logging.factory import LoggerFactory

from infrastructure.db.pool import PostgresPool
from infrastructure.redis.client import RedisClient


class Container:
    """
    DI container.

    RULES:
    - no business logic
    - no dynamic creation in runtime
    - explicit lifecycle

    Future:
    - will be split per bounded context
    - avoid god-object growth by modular containers
    """

    def __init__(self) -> None:
        self._config: Optional[RuntimeConfig] = None
        self._logger_factory: Optional[LoggerFactory] = None

        self._pg: Optional[PostgresPool] = None
        self._redis: Optional[RedisClient] = None

    def init_connections(self) -> None:
        if self._config is None or self._logger_factory is None:
            raise RuntimeError("Dependencies not initialized")

        logger = self._logger_factory.create()

        self._pg = PostgresPool(
            dsn=self._config.db_dsn,
            logger=logger,
        )

        self._redis = RedisClient(
            url=self._config.redis_url,
            logger=logger,
        )

    @property
    def postgres(self) -> PostgresPool:
        if self._pg is None:
            raise RuntimeError("Postgres not initialized")
        return self._pg

    @property
    def redis(self) -> RedisClient:
        if self._redis is None:
            raise RuntimeError("Redis not initialized")
        return self._redis
