from __future__ import annotations

import asyncio
from enum import Enum, auto
from typing import Optional, Set

from core.types.protocols import LoggerProtocol


class WorkerState(Enum):
    INITIAL = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


class BaseWorker:
    """
    Base worker:

    - lifecycle-safe
    - cancellation-safe
    - bounded concurrency
    - structured logging
    """

    def __init__(
        self,
        name: str,
        logger: LoggerProtocol,
        *,
        concurrency: int = 10,
    ) -> None:
        self._name = name
        self._logger = logger.bind(worker=name)

        self._concurrency = concurrency
        self._state = WorkerState.INITIAL

        self._tasks: Set[asyncio.Task] = set()
        self._semaphore = asyncio.Semaphore(concurrency)

        self._stop_event = asyncio.Event()

    @property
    def state(self) -> WorkerState:
        return self._state

    async def start(self) -> None:
        if self._state is not WorkerState.INITIAL:
            raise RuntimeError("Invalid start state")

        self._state = WorkerState.STARTING
        self._stop_event.clear()

        self._logger.info("worker_starting", concurrency=self._concurrency)

        try:
            await self._run()
            self._state = WorkerState.RUNNING
        except Exception as e:
            self._state = WorkerState.FAILED
            self._logger.error("worker_failed", error=str(e))
            raise

    async def stop(self) -> None:
        if self._state not in (WorkerState.RUNNING, WorkerState.FAILED):
            return

        self._state = WorkerState.STOPPING
        self._logger.info("worker_stopping")

        self._stop_event.set()

        await asyncio.gather(*self._tasks, return_exceptions=True)

        self._state = WorkerState.STOPPED
        self._logger.info("worker_stopped")

    async def _run(self) -> None:
        raise NotImplementedError

    async def _spawn(self, coro) -> None:
        async with self._semaphore:
            task = asyncio.create_task(coro)
            self._tasks.add(task)

            def _done(t: asyncio.Task) -> None:
                self._tasks.discard(t)

            task.add_done_callback(_done)
