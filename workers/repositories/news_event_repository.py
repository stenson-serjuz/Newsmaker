from __future__ import annotations

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction

from contracts.events.envelope import EventEnvelope


class NewsEventRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def save(
        self,
        event: EventEnvelope,
    ) -> None:
        payload = dict(event.payload)

        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO news_events (
                    id,
                    event_id,
                    source_id,
                    external_id,
                    title,
                    content,
                    url,
                    content_hash,
                    payload,
                    metadata,
                    status,
                    retry_count
                )
                VALUES (
                    gen_random_uuid(),
                    $1,
                    $2,
                    $3,
                    $4,
                    $5,
                    $6,
                    $7,
                    $8::jsonb,
                    $9::jsonb,
                    $10,
                    $11
                )
                ON CONFLICT (event_id)
                DO NOTHING
                """,
                event.event_id,
                payload["source_id"],
                payload["external_id"],
                payload["title"],
                payload["content"],
                payload["url"],
                payload["content_hash"],
                event.model_dump_json(),
                event.metadata,
                "received",
                event.retry.retry_count,
            )
