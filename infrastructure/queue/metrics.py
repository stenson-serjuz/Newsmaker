from __future__ import annotations

from redis.asyncio import Redis


class QueueMetrics:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def stream_length(self, stream: str) -> int:
        return await self._redis.xlen(stream)

    async def pending_count(self, stream: str, group: str) -> int:
        info = await self._redis.xpending(stream, group)
        return info["pending"]

    async def lag(self, stream: str) -> int:
        return await self._redis.xlen(stream)
