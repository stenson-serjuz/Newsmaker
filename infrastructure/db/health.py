import asyncio
import asyncpg
from asyncpg import PostgresError

from core.types.protocols import LoggerProtocol


class PostgresHealthCheck:
    def __init__(self, pool: asyncpg.Pool, logger: LoggerProtocol) -> None:
        self._pool = pool
        self._logger = logger.bind(component="postgres_health")

    async def check(self) -> bool:
        try:
            async with asyncio.timeout(2.0):
                async with self._pool.acquire() as conn:
                    await conn.execute("SELECT 1")
            return True
        except (asyncio.TimeoutError, PostgresError) as e:
            self._logger.error("postgres_health_failed", error=str(e))
            return False
