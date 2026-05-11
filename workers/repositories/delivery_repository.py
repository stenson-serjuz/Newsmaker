from __future__ import annotations

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class DeliveryRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def mark_sent(
        self,
        event_id: str,
        latency_ms: int,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO delivery_attempts (
                    event_id,
                    platform,
                    status,
                    latency_ms
                )
                VALUES (
                    $1,
                    'telegram',
                    'sent',
                    $2
                )
                """,
                event_id,
                latency_ms,
            )

    async def mark_failed(
        self,
        event_id: str,
        error: str,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO delivery_attempts (
                    event_id,
                    platform,
                    status,
                    error
                )
                VALUES (
                    $1,
                    'telegram',
                    'failed',
                    $2
                )
                """,
                event_id,
                error,
            )
