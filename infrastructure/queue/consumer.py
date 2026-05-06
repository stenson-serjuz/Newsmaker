from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

from redis.asyncio import Redis
from redis.exceptions import RedisError

from contracts.events.envelope import EventEnvelope


class StreamConsumer:
    def __init__(
        self,
        redis: Redis,
        stream: str,
        group: str,
        consumer_name: str,
    ) -> None:
        self._redis = redis
        self._stream = stream
        self._group = group
        self._consumer = consumer_name

    async def ensure_group(self) -> None:
        try:
            await self._redis.xgroup_create(
                self._stream,
                self._group,
                id="0",
                mkstream=True,
            )
        except RedisError:
            pass

    async def consume(
        self,
        count: int = 10,
        block_ms: int = 5000,
    ) -> AsyncIterator[tuple[str, EventEnvelope]]:
        while True:
            try:
                messages = await self._redis.xreadgroup(
                    groupname=self._group,
                    consumername=self._consumer,
                    streams={self._stream: ">"},
                    count=count,
                    block=block_ms,
                )

                if not messages:
                    continue

                for _, entries in messages:
                    for msg_id, data in entries:
                        event = EventEnvelope.model_validate_json(data["data"])
                        yield msg_id, event

            except asyncio.CancelledError:
                raise
            except RedisError:
                await asyncio.sleep(1)

    async def ack(self, message_id: str) -> None:
        await self._redis.xack(self._stream, self._group, message_id)
