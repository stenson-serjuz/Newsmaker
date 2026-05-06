from __future__ import annotations

import asyncio
from typing import Optional

import asyncpg

from core.logging.factory import LoggerFactory
from core.types.protocols import LoggerProtocol


class PostgresPool:
    def __init__(
        self,
        dsn: str,
        logger: LoggerProtocol,
        min_size: int = 5,
        max_size: int = 20,
        connect_timeout: float = 5.0,
    ) -> None:
        self._dsn = dsn
        self._logger = logger.bind(component="postgres_pool")

        self._min_size = min_size
        self._max_size = max_size
        self._connect_timeout = connect_timeout

        self._pool: Optional[asyncpg.Pool] = None

    async def start(self) -> None:
        self._logger.info("postgres_pool_starting")

        self._pool = await asyncpg.create_pool(
            dsn=self._dsn,
            min_size=self._min_size,
            max_size=self._max_size,
            timeout=self._connect_timeout,
            command_timeout=10,
        )

        await self._warmup()

        self._logger.info("postgres_pool_started")

    async def _warmup(self) -> None:
        assert self._pool is not None

        async with self._pool.acquire() as conn:
            await conn.execute("SELECT 1")

    async def close(self) -> None:
        if self._pool is None:
            return

        self._logger.info("postgres_pool_closing")
        await self._pool.close()
        self._logger.info("postgres_pool_closed")

    def get(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Postgres pool not initialized")
        return self._pool
