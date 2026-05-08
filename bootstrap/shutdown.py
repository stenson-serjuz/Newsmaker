from __future__ import annotations

from bootstrap.container import Container


class ShutdownOrchestrator:
    def __init__(self, container: Container) -> None:
        self._c = container

    async def run(self) -> None:
        await self._c.redis.close()

        await self._c.postgres.stop()

        await self._c.bot.session.close()
