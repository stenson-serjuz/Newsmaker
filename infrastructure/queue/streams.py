from __future__ import annotations

from redis.asyncio import Redis


class StreamNames:
    @staticmethod
    def events(shard: int) -> str:
        return f"stream:events:{shard}"

    @staticmethod
    def retry(shard: int) -> str:
        return f"stream:retry:{shard}"

    @staticmethod
    def dlq(shard: int) -> str:
        return f"stream:dlq:{shard}"


class ConsumerGroups:
    @staticmethod
    def workers(shard: int) -> str:
        return f"cg:events:{shard}:workers"

    @staticmethod
    def retry(shard: int) -> str:
        return f"cg:retry:{shard}"
