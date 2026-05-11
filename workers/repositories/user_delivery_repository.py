from __future__ import annotations

from infrastructure.db.pool import (
    PostgresPool,
)

from infrastructure.db.transaction import (
    transaction,
)


class UserDeliveryRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def was_delivered(
        self,
        *,
        user_id: str,
        event_id: str,
    ) -> bool:
        async with transaction(self._pool) as conn:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM user_event_delivery
                WHERE
                    user_id = $1
                    AND event_id = $2
                """,
                user_id,
                event_id,
            )

            return row is not None

    async def save_delivery(
        self,
        *,
        user_id: str,
        event_id: str,
        relevance_score: int,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO user_event_delivery (
                    id,
                    user_id,
                    event_id,
                    relevance_score
                )
                VALUES (
                    gen_random_uuid(),
                    $1,
                    $2,
                    $3
                )
                """,
                user_id,
                event_id,
                relevance_score,
            )
