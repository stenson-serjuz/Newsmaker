import asyncio
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core.types.protocols import LoggerProtocol


class RedisHealthCheck:
    def __init__(self, client: Redis, logger: LoggerProtocol) -> None:
        self._client = client
        self._logger = logger.bind(component="redis_health")

    async def check(self) -> bool:
        try:
            async with asyncio.timeout(2.0):
                await self._client.ping()
            return True
        except (asyncio.TimeoutError, RedisError) as e:
            self._logger.error("redis_health_failed", error=str(e))
            return False
