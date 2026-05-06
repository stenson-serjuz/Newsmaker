from __future__ import annotations

from redis.asyncio import Redis

from contracts.events.envelope import EventEnvelope


class DeadLetterQueue:
    def __init__(self, redis: Redis, stream: str) -> None:
        self._redis = redis
        self._stream = stream

    async def push(self, event: EventEnvelope, reason: str) -> None:
        await self._redis.xadd(
            self._stream,
            {
                "data": event.model_dump_json(),
                "error": reason,
            },
            maxlen=50_000,
            approximate=True,
        )
