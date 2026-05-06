from __future__ import annotations

import asyncio
import time
from enum import Enum, auto
from typing import Optional, Set, Awaitable, Callable

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
    Runtime-safe worker base:

    - correct lifecycle transitions
    - bounded concurrency (semaphore enforced)
    - task safety (no leaks, logged exceptions)
    - graceful shutdown
    - heartbeat + basic metrics
    """

    def __init__(
        self,
        name: str,
        logger: LoggerProtocol,
        *,
        concurrency: int = 10,
        heartbeat_interval: float = 5.0,
    ) -> None:
        self._name = name
        self._logger = logger.bind(worker=name)

        self._concurrency = concurrency
        self._semaphore = asyncio.Semaphore(concurrency)

        self._state = WorkerState.INITIAL
        self._stop_event = asyncio.Event()

        self._tasks: Set[asyncio.Task] = set()
        self._runner_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        self._started_at: float = 0.0
        self._heartbeat_interval = heartbeat_interval
        self._last_heartbeat: float = 0.0

    # -------------------- public API --------------------

    @property
    def state(self) -> WorkerState:
        return self._state

    def metrics(self) -> dict[str, int | float]:
        return {
            "state": self._state.name,
            "active_tasks": len(self._tasks),
            "concurrency": self._concurrency,
            "uptime_sec": int(time.time() - self._started_at) if self._started_at else 0,
            "last_heartbeat": int(self._last_heartbeat),
        }

    async def start(self) -> None:
        if self._state is not WorkerState.INITIAL:
            raise RuntimeError("Invalid start state")

        self._state = WorkerState.STARTING
        self._stop_event.clear()

        self._logger.info("worker_starting", concurrency=self._concurrency)

        self._started_at = time.time()

        # RUNNING state set BEFORE runtime loop
        self._state = WorkerState.RUNNING

        # spawn runner
        self._runner_task = asyncio.create_task(self._run_guarded())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        if self._state not in (WorkerState.RUNNING, WorkerState.FAILED):
            return

        self._state = WorkerState.STOPPING
        self._logger.info("worker_stopping")

        self._stop_event.set()

        if self._runner_task:
            self._runner_task.cancel()

        # wait for in-flight tasks
        await asyncio.gather(*self._tasks, return_exceptions=True)

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        self._state = WorkerState.STOPPED
        self._logger.info("worker_stopped")

    # -------------------- internal --------------------

    async def _run_guarded(self) -> None:
        try:
            await self._run()
        except asyncio.CancelledError:
            self._logger.info("worker_runner_cancelled")
        except Exception as e:
            self._state = WorkerState.FAILED
            self._logger.error("worker_runtime_failed", error=str(e))
            raise

    async def _run(self) -> None:
        raise NotImplementedError

    async def _spawn(self, fn: Callable[[], Awaitable[None]]) -> None:
        """
        Safe task wrapper with:
        - semaphore enforcement
        - exception logging
        - cancellation propagation
        """

        await self._semaphore.acquire()

        async def runner() -> None:
            try:
                await fn()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self._logger.error("task_failed", error=str(e))
            finally:
                self._semaphore.release()

        task = asyncio.create_task(runner())
        self._tasks.add(task)

        def _done(t: asyncio.Task) -> None:
            self._tasks.discard(t)

        task.add_done_callback(_done)

    async def _heartbeat_loop(self) -> None:
        while not self._stop_event.is_set():
            self._last_heartbeat = time.time()
            self._logger.debug("worker_heartbeat", active_tasks=len(self._tasks))
            await asyncio.sleep(self._heartbeat_interval)
