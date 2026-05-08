from __future__ import annotations

import os
from typing import Optional, Any

from aiogram import Bot, Dispatcher

from core.config.settings import load_settings, Settings
from core.logging.logger import get_logger

from infrastructure.db.pool import PostgresPool
from infrastructure.db.health import PostgresHealthCheck

from infrastructure.redis.client import RedisClient
from infrastructure.redis.health import RedisHealthCheck

from scheduler.scheduler import Scheduler


class Container:
    def __init__(self) -> None:
        self._settings: Optional[Settings] = None
        self._logger: Optional[Any] = None

        self._postgres: Optional[PostgresPool] = None
        self._redis: Optional[RedisClient] = None

        self._postgres_health: Optional[PostgresHealthCheck] = None
        self._redis_health: Optional[RedisHealthCheck] = None

        self._bot: Optional[Bot] = None
        self._dispatcher: Optional[Dispatcher] = None

        self._scheduler: Optional[Scheduler] = None

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
        self.init_logging()

    def init_connections(self) -> None:
        settings = self.settings
        logger = self.logger

        if self._postgres is None:
            self._postgres = PostgresPool(
                dsn=settings.asyncpg_database_dsn(),
                logger=logger,
            )

        if self._redis is None:
            self._redis = RedisClient(
                url=os.environ["REDIS_URL"],
                logger=logger,
            )

        if self._bot is None:
            self._bot = Bot(
                token=settings.bot_token,
            )

        if self._dispatcher is None:
            self._dispatcher = Dispatcher()

        if self._scheduler is None:
            self._scheduler = Scheduler(
                logger=logger,
            )

    # ------------------------------------------------------------------
    # INIT FLOW
    # ------------------------------------------------------------------
    def init_all(self) -> None:
        self.init_config()
        self.init_logging()
        self.init_connections()

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
    def postgres(self) -> PostgresPool:
        if self._postgres is None:
            self.init_connections()

        if self._postgres is None:
            raise RuntimeError("PostgresPool not initialized")

        return self._postgres

    @property
    def redis(self) -> RedisClient:
        if self._redis is None:
            self.init_connections()

        if self._redis is None:
            raise RuntimeError("RedisClient not initialized")

        return self._redis

    @property
    def postgres_health(self) -> PostgresHealthCheck:
        if self._postgres_health is None:
            pool = self.postgres._pool

            if pool is None:
                raise RuntimeError("Postgres pool is not started")

            self._postgres_health = PostgresHealthCheck(
                pool=pool,
                logger=self.logger,
            )

        return self._postgres_health

    @property
    def redis_health(self) -> RedisHealthCheck:
        if self._redis_health is None:
            self._redis_health = RedisHealthCheck(
                client=self.redis.get(),
                logger=self.logger,
            )

        return self._redis_health

    @property
    def workers(self) -> list[Any]:
        return []

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            self.init_connections()

        if self._bot is None:
            raise RuntimeError("Bot not initialized")

        return self._bot

    @property
    def dispatcher(self) -> Dispatcher:
        if self._dispatcher is None:
            self.init_connections()

        if self._dispatcher is None:
            raise RuntimeError("Dispatcher not initialized")

        return self._dispatcher

    @property
    def scheduler(self) -> Scheduler:
        if self._scheduler is None:
            self.init_connections()

        if self._scheduler is None:
            raise RuntimeError("Scheduler not initialized")

        return self._scheduler
