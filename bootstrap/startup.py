from __future__ import annotations

import asyncio

from bootstrap.container import Container


class StartupOrchestrator:
    """
    Startup phases:
    1. Config + logging
    2. Connections
    3. Readiness check
    4. Worker startup
    """

    def __init__(self, container: Container) -> None:
        self._c = container

    async def run(self) -> None:
        self._c.init_config()
        self._c.init_logging()
        self._c.init_logger_factory()

        self._c.init_connections()

        await self._c.postgres.start()
        await self._c.redis.start()

        await self._readiness()

        await self._start_workers()

    async def _readiness(self) -> None:
        await asyncio.gather(
            self._c.postgres_health.check(),
            self._c.redis_health.check(),
        )

    async def _start_workers(self) -> None:
        for worker in self._c.workers:
            await worker.start()
