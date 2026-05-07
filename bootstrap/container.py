from __future__ import annotations

import os

from core.config.settings import load_settings
from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool
from infrastructure.redis.client import RedisClient


class Container:
    def __init__(self) -> None:
        self.settings = load_settings()

        self.logger = get_logger()

        self._postgres = PostgresPool(
            dsn=self.settings.asyncpg_database_dsn(),
            logger=self.logger,
        )

        self._redis = RedisClient(
            dsn=os.environ["REDIS_URL"],
            logger=self.logger,
        )

    @property
    def postgres(self) -> PostgresPool:
        return self._postgres

    @property
    def redis(self) -> RedisClient:
        return self._redis
