from __future__ import annotations

import asyncio
import time
from typing import Protocol, Sequence
from uuid import UUID


class SourceRecord(Protocol):
    id: UUID
    is_active: bool
    is_degraded: bool


class SourceProvider(Protocol):
    async def list_active(self) -> Sequence[SourceRecord]: ...


class Scheduler:
    """
    Bounded, drift-safe scheduler with backoff.
    """

    def __init__(
        self,
        provider: SourceProvider,
        runner,
        *,
        interval: float = 30.0,
        concurrency: int = 5,
    ) -> None:
        self._provider = provider
        self._runner = runner

        self._interval = interval
        self._sem = asyncio.Semaphore(concurrency)

        self._stop = asyncio.Event()
        self._backoff: dict[UUID, float] = {}

    async def start(self) -> None:
        while not self._stop.is_set():
            start = time.monotonic()

            sources = await self._provider.list_active()

            tasks = [
                self._schedule_source(src)
                for src in sources
                if not src.is_degraded
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.monotonic() - start
            sleep = max(0, self._interval - elapsed)
            await asyncio.sleep(sleep)

    async def stop(self) -> None:
        self._stop.set()

    async def _schedule_source(self, src: SourceRecord) -> None:
        now = time.monotonic()

        backoff_until = self._backoff.get(src.id, 0)
        if now < backoff_until:
            return

        async with self._sem:
            try:
                await self._runner.run(src.id)
                self._backoff.pop(src.id, None)
            except Exception:
                # exponential backoff
                delay = self._backoff.get(src.id, 1.0) * 2
                delay = min(delay, 300)
                self._backoff[src.id] = now + delay
