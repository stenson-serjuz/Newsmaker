# infrastructure/redis/client.py

from __future__ import annotations

import asyncio
from typing import Optional, Any

from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from redis.exceptions import RedisError


class RedisClient:
    """
    Retry strategy:
    - Redis driver handles low-level retries
    - application layer handles retry logic
    """

    def __init__(
        self,
        url: str,
        logger: Any,
    ) -> None:
        self._url = url
        self._logger = logger.bind(component="redis_client")

        self._client: Optional[Redis] = None

        self._pubsub: Optional[PubSub] = None
        self._listener_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._logger.info("redis_connecting")

        try:
            self._client = Redis.from_url(
                self._url,
                encoding="utf-8",
                decode_responses=True,
                health_check_interval=30,
            )

            await self._client.ping()

            self._logger.info("redis_ping_success")

            # IMPORTANT:
            # PubSub listener is long-running runtime behavior.
            # It must NOT block application startup.
            #
            # Previous implementation awaited the listener directly,
            # causing startup hang before:
            #   redis_started
            #   startup_completed
            #   polling startup
            #
            # Correct behavior:
            # detach listener into background task.
            self._pubsub = self._client.pubsub()

            self._listener_task = asyncio.create_task(
                self._run_listener(),
                name="redis_pubsub_listener",
            )

        except RedisError as e:
            self._logger.error(
                "redis_connection_failed",
                error=str(e),
            )
            raise

        self._logger.info("redis_connected")

    async def _run_listener(self) -> None:
        """
        Long-running Redis PubSub listener.

        Must run in background task and never block startup().
        """

        if self._pubsub is None:
            return

        self._logger.info("redis_listener_started")

        try:
            async for message in self._pubsub.listen():
                self._logger.debug(
                    "redis_pubsub_message",
                    message=str(message),
                )

        except asyncio.CancelledError:
            self._logger.info("redis_listener_cancelled")
            raise

        except Exception as e:
            self._logger.error(
                "redis_listener_failed",
                error=str(e),
            )

    async def close(self) -> None:
        self._logger.info("redis_closing")

        if self._listener_task is not None:
            self._listener_task.cancel()

            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self._pubsub is not None:
            await self._pubsub.close()

        if self._client is not None:
            try:
                await self._client.aclose()
            except RedisError as e:
                self._logger.error(
                    "redis_close_failed",
                    error=str(e),
                )
                raise

        self._logger.info("redis_closed")

    async def stop(self) -> None:
        await self.close()

    def get(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis client not initialized")

        return self._client
