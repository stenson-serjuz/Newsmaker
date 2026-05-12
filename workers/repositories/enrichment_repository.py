from __future__ import annotations

import json

from infrastructure.db.pool import (
    PostgresPool,
)

from infrastructure.db.transaction import (
    transaction,
)


class EnrichmentRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def reserve_events(
        self,
        limit: int = 10,
    ) -> list[dict]:
        async with transaction(
            self._pool,
        ) as conn:
            rows = await conn.fetch(
                """
                UPDATE news_events
                SET enrichment_status = 'processing'
                WHERE id IN (
                    SELECT id
                    FROM news_events
                    WHERE enrichment_status = 'pending'
                    ORDER BY created_at
                    LIMIT $1
                    FOR UPDATE SKIP LOCKED
                )
                RETURNING *
                """,
                limit,
            )

            return [
                dict(r)
                for r in rows
            ]

    async def complete(
        self,
        event_id: str,
        *,
        enriched_title: str,
        enriched_content: str,
        summary: str,
        language: str,
        category: str,
        urgency: str,
        city: str | None,
        priority_score: int,
        tags: list[str],
    ) -> None:
        async with transaction(
            self._pool,
        ) as conn:
            await conn.execute(
                """
                UPDATE news_events
                SET
                    enrichment_status = 'completed',
                    enriched_title = $2,
                    enriched_content = $3,
                    summary = $4,
                    language = $5,
                    category = $6,
                    urgency = $7,
                    city = $8,
                    priority_score = $9,
                    tags = $10::jsonb
                WHERE event_id = $1
                """,
                event_id,
                enriched_title,
                enriched_content,
                summary,
                language,
                category,
                urgency,
                city,
                priority_score,
                json.dumps(tags),
            )

    async def fail(
        self,
        event_id: str,
    ) -> None:
        async with transaction(
            self._pool,
        ) as conn:
            await conn.execute(
                """
                UPDATE news_events
                SET enrichment_status = 'failed'
                WHERE event_id = $1
                """,
                event_id,
            )
