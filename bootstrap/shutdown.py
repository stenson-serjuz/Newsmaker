from __future__ import annotations

import asyncio

from bootstrap.container import Container


class ShutdownOrchestrator:
    """
    Shutdown phases:
    1. stop intake (bot/workers)
    2. drain workers
    3. close bot
    4. close Redis
    5. close Postgres
    """

    def __init__(self, container: Container) -> None:
        self._c = container

    async def run(self) -> None:
        # stop workers first
        await asyncio.gather(*(w.stop() for w in self._c.workers))

        # close bot
        if self._c.bot:
            await self._c.bot.session.close()

        # infra
        await self._c.redis.close()
        await self._c.postgres.close()
