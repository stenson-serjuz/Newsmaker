from __future__ import annotations

import asyncio
from typing import Optional

import asyncpg
from asyncpg import Pool, PoolAcquireTimeoutError, PostgresError

from core.types.protocols import LoggerProtocol


class PostgresPool:
    """
    Ownership:
    - Managed by DI container
    - Lifecycle controlled via bootstrap.lifecycle
    - No global access

    Guarantees:
    - Warmed pool
    - Safe acquisition with timeout
    - Stale connection mitigation
    """

    def __init__(
        self,
        dsn: str,
        logger: LoggerProtocol,
        *,
        min_size: int = 5,
        max_size: int = 20,
        connect_timeout: float = 5.0,
        acquire_timeout: float = 5.0,
        command_timeout: float = 10.0,
        max_inactive_connection_lifetime: float = 300.0,
    ) -> None:
        self._dsn = dsn
        self._logger = logger.bind(component="postgres_pool")

        self._min_size = min_size
        self._max_size = max_size
        self._connect_timeout = connect_timeout
        self._acquire_timeout = acquire_timeout
        self._command_timeout = command_timeout
        self._max_inactive_connection_lifetime = max_inactive_connection_lifetime

        self._pool: Optional[Pool] = None

    async def start(self) -> None:
        self._logger.info("postgres_pool_starting")

        try:
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                timeout=self._connect_timeout,
                command_timeout=self._command_timeout,
                max_inactive_connection_lifetime=self._max_inactive_connection_lifetime,
            )
        except (asyncio.TimeoutError, PostgresError) as e:
            self._logger.error("postgres_pool_init_failed", error=str(e))
            raise

        await self._warmup()

        self._logger.info(
            "postgres_pool_started",
            min_size=self._min_size,
            max_size=self._max_size,
        )

    async def _warmup(self) -> None:
        if self._pool is None:
            raise RuntimeError("Pool not initialized")

        try:
            async with asyncio.timeout(self._acquire_timeout):
                async with self._pool.acquire() as conn:
                    await conn.execute("SELECT 1")
        except (asyncio.TimeoutError, PoolAcquireTimeoutError, PostgresError) as e:
            self._logger.error("postgres_pool_warmup_failed", error=str(e))
            raise

    async def close(self) -> None:
        if self._pool is None:
            return

        self._logger.info("postgres_pool_closing")

        try:
            await self._pool.close()
        except PostgresError as e:
            self._logger.error("postgres_pool_close_failed", error=str(e))
            raise

        self._logger.info("postgres_pool_closed")

    def get(self) -> Pool:
        if self._pool is None:
            raise RuntimeError("Postgres pool not initialized")
        return self._pool

    async def acquire(self) -> asyncpg.Connection:
        """
        Safe acquire with timeout
        """
        pool = self.get()

        try:
            async with asyncio.timeout(self._acquire_timeout):
                return await pool.acquire()
        except (asyncio.TimeoutError, PoolAcquireTimeoutError) as e:
            self._logger.error("postgres_acquire_timeout", error=str(e))
            raise
