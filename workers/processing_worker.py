from __future__ import annotations

import asyncio

from contracts.events.envelope import EventEnvelope
from infrastructure.queue.interfaces import ConsumerProtocol, ProducerProtocol
from infrastructure.queue.retry import RetryPolicy
from infrastructure.queue.dlq import DeadLetterQueue

from workers.base import BaseWorker


class ProcessingWorker(BaseWorker):
    """
    Handles:
    - event consumption
    - handler invocation (external)
    - retry / DLQ routing
    """

    def __init__(
        self,
        consumer: ConsumerProtocol,
        retry_producer: ProducerProtocol,
        dlq: DeadLetterQueue,
        retry_policy: RetryPolicy,
        logger,
    ) -> None:
        super().__init__("processing_worker", logger)

        self._consumer = consumer
        self._retry_producer = retry_producer
        self._dlq = dlq
        self._retry_policy = retry_policy

    async def _run(self) -> None:
        await self._consumer.start()

        async for msg_id, event in self._consumer.consume():
            if self._stop_event.is_set():
                break

            await self._spawn(self._handle(msg_id, event))

    async def _handle(self, msg_id: str, event: EventEnvelope) -> None:
        try:
            # handler abstraction (external)
            await asyncio.sleep(0)

            await self._consumer.ack(msg_id)

        except asyncio.CancelledError:
            raise

        except Exception as e:
            meta = event.retry

            if self._retry_policy.is_poison(meta):
                await self._dlq.push(
                    event,
                    reason=str(e),
                    consumer="processing",
                    shard_id=event.delivery.shard_id,
                )
                await self._consumer.ack(msg_id)
                return

            next_meta = self._retry_policy.next(meta)

            await self._retry_producer.publish(
                f"stream:retry:{event.delivery.shard_id}",
                event.copy(update={"retry": next_meta}),
            )

            await self._consumer.ack(msg_id)
