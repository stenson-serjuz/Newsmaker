from __future__ import annotations

from redis.asyncio import Redis
from redis.exceptions import ResponseError


class StreamTopology:
    """
    Ownership:
    - initialized externally (bootstrap or migration step)
    - NOT owned by consumer
    """

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @staticmethod
    def events(shard: int) -> str:
        return f"stream:events:{shard}"

    @staticmethod
    def retry(shard: int) -> str:
        return f"stream:retry:{shard}"

    @staticmethod
    def dlq(shard: int) -> str:
        return f"stream:dlq:{shard}"

    @staticmethod
    def group_events(shard: int) -> str:
        return f"cg:events:{shard}:workers"

    async def ensure_group(self, stream: str, group: str) -> None:
        try:
            await self._redis.xgroup_create(
                stream,
                group,
                id="0",
                mkstream=True,
            )
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

    async def trim(self, stream: str, maxlen: int) -> None:
        await self._redis.xtrim(stream, maxlen=maxlen, approximate=True)
