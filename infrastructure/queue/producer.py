from __future__ import annotations

import json
from redis.asyncio import Redis

from contracts.events.envelope import EventEnvelope


class StreamProducer:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def publish(self, stream: str, event: EventEnvelope) -> str:
        return await self._redis.xadd(
            stream,
            {"data": event.model_dump_json()},
            maxlen=100_000,
            approximate=True,
        )
