from enum import Enum, auto
import asyncio

from bootstrap.container import Container
from infrastructure.db.health import PostgresHealthCheck
from infrastructure.redis.health import RedisHealthCheck


class LifecycleState(Enum):
    INITIAL = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


class LifecycleManager:
    def __init__(self, container: Container) -> None:
        self._container = container
        self._state = LifecycleState.INITIAL

    @property
    def state(self) -> LifecycleState:
        return self._state

    async def startup(self) -> None:
        if self._state is not LifecycleState.INITIAL:
            raise RuntimeError("Invalid lifecycle transition")

        self._state = LifecycleState.STARTING

        try:
            self._container.init_config()
            self._container.init_logging()
            self._container.init_logger_factory()
            self._container.init_connections()

            await self._container.postgres.start()
            await self._container.redis.start()

            await self._readiness_check()

            self._state = LifecycleState.RUNNING

        except Exception:
            self._state = LifecycleState.FAILED
            raise

    async def _readiness_check(self) -> None:
        logger = self._container.logger_factory.create().bind(component="readiness")

        pg = PostgresHealthCheck(self._container.postgres.get(), logger)
        redis = RedisHealthCheck(self._container.redis.get(), logger)

        results = await asyncio.gather(
            pg.check(),
            redis.check(),
            return_exceptions=False,
        )

        if not all(results):
            logger.error("readiness_failed", results=results)
            raise RuntimeError("Readiness check failed")

        logger.info("readiness_ok")

    async def shutdown(self) -> None:
        if self._state not in (LifecycleState.RUNNING, LifecycleState.FAILED):
            raise RuntimeError("Invalid shutdown transition")

        self._state = LifecycleState.STOPPING

        try:
            await asyncio.shield(self._container.redis.close())
            await asyncio.shield(self._container.postgres.close())
        finally:
            self._state = LifecycleState.STOPPED
