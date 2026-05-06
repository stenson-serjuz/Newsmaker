from __future__ import annotations

from infrastructure.queue.interfaces import ConsumerProtocol

from workers.base import BaseWorker


class DLQWorker(BaseWorker):
    """
    DLQ processor (manual replay boundary)
    """

    def __init__(
        self,
        consumer: ConsumerProtocol,
        logger,
    ) -> None:
        super().__init__("dlq_worker", logger)

        self._consumer = consumer

    async def _run(self) -> None:
        await self._consumer.start()

        async for msg_id, event in self._consumer.consume():
            if self._stop_event.is_set():
                break

            # no auto-replay
            await self._consumer.ack(msg_id)
