from __future__ import annotations

from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from core.types.protocols import LoggerProtocol


class RedisClient:
    """
    Ownership:
    - managed by container
    - single instance per process

    Guarantees:
    - safe startup
    - reconnect handled by driver
    """

    def __init__(
        self,
        url: str,
        logger: LoggerProtocol,
    ) -> None:
        self._url = url
        self._logger = logger.bind(component="redis_client")
        self._client: Optional[Redis] = None

    async def start(self) -> None:
        self._logger.info("redis_connecting")

        try:
            self._client = Redis.from_url(
                self._url,
                encoding="utf-8",
                decode_responses=True,
                health_check_interval=30,
                retry_on_timeout=True,
            )

            await self._client.ping()

        except RedisError as e:
            self._logger.error("redis_connection_failed", error=str(e))
            raise

        self._logger.info("redis_connected")

    async def close(self) -> None:
        if self._client is None:
            return

        self._logger.info("redis_closing")

        try:
            await self._client.aclose()
        except RedisError as e:
            self._logger.error("redis_close_failed", error=str(e))
            raise

        self._logger.info("redis_closed")

    def get(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis client not initialized")
        return self._client
