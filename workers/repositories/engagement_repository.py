from __future__ import annotations

from infrastructure.db.pool import (
    PostgresPool,
)

from infrastructure.db.transaction import (
    transaction,
)


class EngagementRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def track(
        self,
        *,
        user_id: str,
        event_id: str,
        event_type: str,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO user_engagement (
                    id,
                    user_id,
                    event_id,
                    event_type
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
                event_type,
            )
