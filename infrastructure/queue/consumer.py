from __future__ import annotations

import asyncio
from typing import AsyncIterator

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from contracts.events.envelope import EventEnvelope

from infrastructure.queue.interfaces import (
    ConsumerProtocol,
)


class StreamConsumer(ConsumerProtocol):
    """
    Redis Streams consumer group wrapper.

    Guarantees:
    - at-least-once delivery
    - explicit ACK
    - consumer group recovery
    """

    def __init__(
        self,
        redis: Redis,
        *,
        stream: str,
        group: str,
        consumer_name: str,
        block_ms: int = 5000,
        batch_size: int = 10,
    ) -> None:
        self._redis = redis

        self._stream = stream
        self._group = group
        self._consumer = consumer_name

        self._block_ms = block_ms
        self._batch_size = batch_size

        self._running = False

    async def start(self) -> None:
        try:
            await self._redis.xgroup_create(
                name=self._stream,
                groupname=self._group,
                id="0",
                mkstream=True,
            )
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def consume(
        self,
    ) -> AsyncIterator[
        tuple[str, EventEnvelope]
    ]:
        while self._running:
            response = await self._redis.xreadgroup(
                groupname=self._group,
                consumername=self._consumer,
                streams={
                    self._stream: ">"
                },
                count=self._batch_size,
                block=self._block_ms,
            )

            if not response:
                await asyncio.sleep(0.1)
                continue

            for _, messages in response:
                for message_id, payload in messages:
                    raw = payload["data"]

                    event = (
                        EventEnvelope
                        .model_validate_json(raw)
                    )

                    yield (
                        message_id,
                        event,
                    )

    async def ack(
        self,
        message_id: str,
    ) -> None:
        await self._redis.xack(
            self._stream,
            self._group,
            message_id,
        )
