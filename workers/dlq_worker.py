from __future__ import annotations

from infrastructure.queue.interfaces import ConsumerProtocol

from workers.base import BaseWorker


class DLQWorker(BaseWorker):
    """
    Explicit quarantine semantics:
    - no automatic replay
    - messages are acknowledged and preserved in DLQ
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

        async for msg_id, _event in self._consumer.consume():
            if self._stop_event.is_set():
                break

            await self._consumer.ack(msg_id)
