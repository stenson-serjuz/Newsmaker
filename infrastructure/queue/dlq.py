from __future__ import annotations

import time
from redis.asyncio import Redis

from contracts.events.envelope import EventEnvelope


class DeadLetterQueue:
    def __init__(self, redis: Redis, stream: str) -> None:
        self._redis = redis
        self._stream = stream

    async def push(
        self,
        event: EventEnvelope,
        *,
        reason: str,
        consumer: str,
        shard_id: int,
    ) -> None:
        await self._redis.xadd(
            self._stream,
            {
                "data": event.model_dump_json(),
                "error": reason,
                "failed_at": str(int(time.time())),
                "consumer": consumer,
                "retry_attempts": str(event.retry.attempt),
                "trace_id": event.trace_id or "",
                "shard": str(shard_id),
            },
            maxlen=50_000,
            approximate=True,
        )
