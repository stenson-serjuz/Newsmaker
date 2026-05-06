from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

import asyncpg


@asynccontextmanager
async def transaction(
    pool: asyncpg.Pool,
    *,
    isolation: Optional[str] = None,
    readonly: bool = False,
    timeout: Optional[float] = None,
) -> AsyncIterator[asyncpg.Connection]:
    """
    Transaction scope rules:

    - one transaction per use-case
    - never shared across async tasks
    - must be short-lived

    Supports:
    - isolation level
    - readonly transactions
    - timeout
    """

    async with pool.acquire() as conn:
        tx = conn.transaction(
            isolation=isolation,
            readonly=readonly,
        )

        try:
            if timeout:
                async with asyncio.timeout(timeout):
                    async with tx:
                        yield conn
            else:
                async with tx:
                    yield conn
        except asyncio.CancelledError:
            raise
        except Exception:
            raise
