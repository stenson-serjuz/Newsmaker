from __future__ import annotations

import asyncio

from infrastructure.queue.streams import StreamTopology
from infrastructure.queue.consumer import StreamConsumer

from workers.base import BaseWorker


class MaintenanceWorker(BaseWorker):
    """
    Handles:
    - stream trimming
    - pending reclaim
    - cleanup
    """

    def __init__(
        self,
        topology: StreamTopology,
        consumer: StreamConsumer,
        logger,
    ) -> None:
        super().__init__("maintenance_worker", logger)

        self._topology = topology
        self._consumer = consumer

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            await self._consumer.reclaim_pending()

            await self._topology.trim(self._consumer._stream, 100_000)

            await asyncio.sleep(10)
