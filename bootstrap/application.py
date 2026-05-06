from __future__ import annotations

import asyncio

from bootstrap.container import Container
from bootstrap.startup import StartupOrchestrator
from bootstrap.shutdown import ShutdownOrchestrator
from bootstrap.orchestration import RuntimeOrchestrator


class Application:
    """
    Top-level application coordinator.

    Ownership:
    - owns container
    - owns orchestrators
    - no business logic
    """

    def __init__(self) -> None:
        self._container = Container()

        self._startup = StartupOrchestrator(self._container)
        self._shutdown = ShutdownOrchestrator(self._container)
        self._runtime = RuntimeOrchestrator(self._container)

        self._running = False

    async def start(self) -> None:
        await self._startup.run()

    async def run(self) -> None:
        self._running = True
        await self._runtime.run()

    async def stop(self) -> None:
        if not self._running:
            return

        await self._shutdown.run()
        self._running = False
