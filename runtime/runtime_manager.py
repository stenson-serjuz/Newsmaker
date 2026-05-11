from __future__ import annotations

import asyncio

from runtime.scheduler import Scheduler


class RuntimeManager:
    """
    Orchestrates runtime:
    - scheduler lifecycle
    - graceful shutdown
    """

    def __init__(
        self,
        scheduler: Scheduler,
        logger,
    ) -> None:
        self._scheduler = scheduler
        self._logger = logger.bind(component="runtime_manager")

        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._logger.info("runtime_start")
    
        self._task = asyncio.create_task(
            self._run_scheduler()
        )

    async def _run_scheduler(self) -> None:
        try:
            await self._scheduler.start()
    
        except Exception as e:
            self._logger.exception(
                "scheduler_crashed",
                error=str(e),
            )
            raise
    
    async def stop(self) -> None:
        self._logger.info("runtime_stop")

        await self._scheduler.stop()

        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
