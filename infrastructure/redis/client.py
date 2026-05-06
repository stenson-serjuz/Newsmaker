from __future__ import annotations

from typing import Optional

from redis.asyncio import Redis

from core.types.protocols import LoggerProtocol


class RedisClient:
    def __init__(self, url: str, logger: LoggerProtocol) -> None:
        self._url = url
        self._logger = logger.bind(component="redis_client")
        self._client: Optional[Redis] = None

    async def start(self) -> None:
        self._logger.info("redis_connecting")

        self._client = Redis.from_url(
            self._url,
            encoding="utf-8",
            decode_responses=True,
        )

        await self._client.ping()

        self._logger.info("redis_connected")

    async def close(self) -> None:
        if self._client is None:
            return

        self._logger.info("redis_closing")
        await self._client.close()
        self._logger.info("redis_closed")

    def get(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis client not initialized")
        return self._client
