from __future__ import annotations

from parsers.base.models import NormalizedItem

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class PublicationDedupService:
    """
    Runtime deduplication service.

    Guarantees:
    - no duplicate external_id per source
    - no duplicate content_hash spam
    """

    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def is_duplicate(
        self,
        item: NormalizedItem,
    ) -> bool:
        async with transaction(self._pool) as conn:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM publications
                WHERE
                    source_id = $1
                    AND (
                        external_id = $2
                        OR content_hash = $3
                    )
                LIMIT 1
                """,
                str(item.source_id),
                item.external_id,
                item.content_hash,
            )

            if row:
                return True

            await conn.execute(
                """
                INSERT INTO publications (
                    source_id,
                    external_id,
                    content_hash,
                    delivery_state,
                    retry_count
                )
                VALUES ($1, $2, $3, $4, $5)
                """,
                str(item.source_id),
                item.external_id,
                item.content_hash,
                "pending",
                0,
            )

        return False
