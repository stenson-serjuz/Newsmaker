from __future__ import annotations

from typing import Sequence

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class EventProcessingRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def reserve_events(
        self,
        worker_id: str,
        limit: int = 10,
    ) -> Sequence[dict]:
        async with transaction(self._pool) as conn:
            rows = await conn.fetch(
                """
                UPDATE news_events
                SET
                    delivery_status = 'reserved',
                    reserved_by = $1,
                    reserved_at = NOW()
                WHERE id IN (
                    SELECT id
                    FROM news_events
                    WHERE delivery_status = 'pending'
                    ORDER BY created_at
                    LIMIT $2
                    FOR UPDATE SKIP LOCKED
                )
                RETURNING *
                """,
                worker_id,
                limit,
            )

            return [dict(r) for r in rows]

    async def mark_sent(
        self,
        event_id: str,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                UPDATE news_events
                SET
                    delivery_status = 'sent',
                    sent_at = NOW()
                WHERE event_id = $1
                """,
                event_id,
            )

    async def mark_failed(
        self,
        event_id: str,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                UPDATE news_events
                SET
                    delivery_status = 'failed'
                WHERE event_id = $1
                """,
                event_id,
            )

    async def mark_retry(
        self,
        event_id: str,
        retry_count: int,
        next_retry_at,
        error: str,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                UPDATE news_events
                SET
                    delivery_status = 'retry',
                    retry_count = $2,
                    next_retry_at = $3,
                    last_error = $4
                WHERE event_id = $1
                """,
                event_id,
                retry_count,
                next_retry_at,
                error,
            )
