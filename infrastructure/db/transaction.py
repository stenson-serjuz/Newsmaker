from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

import asyncpg

from infrastructure.db.pool import PostgresPool


@asynccontextmanager
async def transaction(
    pool: PostgresPool,
    *,
    isolation: Optional[str] = None,
    readonly: bool = False,
    timeout: Optional[float] = None,
) -> AsyncIterator[asyncpg.Connection]:
    """
    Transaction rules:
    - always uses pool abstraction
    - no direct pool bypass
    - single-use per scope
    """

    async with pool.connection() as conn:
        tx = conn.transaction(
            isolation=isolation,
            readonly=readonly,
        )

        if timeout:
            async with asyncio.timeout(timeout):
                async with tx:
                    yield conn
        else:
            async with tx:
                yield conn
