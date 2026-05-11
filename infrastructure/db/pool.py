from __future__ import annotations

import asyncio
from typing import Any, Optional, AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Pool, PostgresError

from core.types.protocols import LoggerProtocol


class PostgresPool:
    """
    Asyncpg connection pool wrapper.

    - lifecycle-safe
    - timeout-safe
    - no connection leaks (context-managed acquire)
    """

    def __init__(
        self,
        dsn: str,
        logger: LoggerProtocol,
        *,
        min_size: int = 1,
        max_size: int = 10,
        command_timeout: float = 30.0,
        acquire_timeout: float = 5.0,
        max_inactive_connection_lifetime: float = 300.0,
    ) -> None:
        self._dsn = dsn
        self._logger = logger.bind(component="postgres_pool")

        self._min_size = min_size
        self._max_size = max_size
        self._command_timeout = command_timeout
        self._acquire_timeout = acquire_timeout
        self._max_inactive_connection_lifetime = max_inactive_connection_lifetime

        self._pool: Optional[Pool] = None

    async def start(self) -> None:
        try:
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                command_timeout=self._command_timeout,
                max_inactive_connection_lifetime=self._max_inactive_connection_lifetime,
            )

            # warmup: acquire + release
            async with self.acquire() as conn:
                await conn.execute("SELECT 1")

            self._logger.info("postgres_pool_started")

        except (PostgresError, asyncio.TimeoutError) as e:
            self._logger.error(
                "postgres_pool_start_failed",
                error=str(e),
            )
            raise RuntimeError("Postgres pool initialization failed") from e

    async def stop(self) -> None:
        if self._pool:
            try:
                await self._pool.close()
                self._logger.info("postgres_pool_stopped")
            except asyncio.CancelledError:
                raise
            except PostgresError as e:
                self._logger.warning(
                    "postgres_pool_stop_failed",
                    error=str(e),
                )

    async def health(self) -> bool:
        if not self._pool:
            return False

        try:
            async with self.acquire() as conn:
                await conn.execute("SELECT 1")
            return True
        except (PostgresError, asyncio.TimeoutError):
            return False

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        """
        Proper async context-managed connection acquisition.
        Prevents leaks and enforces timeout.
        """
        if not self._pool:
            raise RuntimeError("Pool not initialized")

        try:
            conn = await asyncio.wait_for(
                self._pool.acquire(),
                timeout=self._acquire_timeout,
            )

            try:
                yield conn
            finally:
                await self._pool.release(conn)

        except asyncio.TimeoutError:
            self._logger.warning("postgres_pool_acquire_timeout")
            raise
        except PostgresError as e:
            self._logger.error(
                "postgres_pool_acquire_failed",
                error=str(e),
            )
            raise

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[asyncpg.Connection]:
        """
        Compatibility layer for repositories expecting
        pool.connection() interface.
        """

        async with self.acquire() as conn:
            yield conn
    
    def metrics(self) -> dict[str, Any]:
        """
        Pool observability metrics.
        """
        if not self._pool:
            return {"status": "not_initialized"}

        return {
            "size": self._pool.get_size(),
            "free": self._pool.get_idle_size(),
            "max_size": self._max_size,
        }
