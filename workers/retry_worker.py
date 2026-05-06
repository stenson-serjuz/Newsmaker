from __future__ import annotations

import time
import asyncio

from infrastructure.queue.interfaces import ConsumerProtocol, ProducerProtocol
from contracts.events.envelope import EventEnvelope

from workers.base import BaseWorker


class RetryWorker(BaseWorker):
    """
    Handles delayed retry execution
    """

    def __init__(
        self,
        consumer: ConsumerProtocol,
        producer: ProducerProtocol,
        logger,
    ) -> None:
        super().__init__("retry_worker", logger)

        self._consumer = consumer
        self._producer = producer

    async def _run(self) -> None:
        await self._consumer.start()

        async for msg_id, event in self._consumer.consume():
            if self._stop_event.is_set():
                break

            await self._spawn(self._process(msg_id, event))

    async def _process(self, msg_id: str, event: EventEnvelope) -> None:
        try:
            if event.retry.next_attempt_at and event.retry.next_attempt_at > int(time.time()):
                return

            await self._producer.publish(
                f"stream:events:{event.delivery.shard_id}",
                event,
            )

            await self._consumer.ack(msg_id)

        except asyncio.CancelledError:
            raise
