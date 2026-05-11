from __future__ import annotations

import json

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class DeadLetterRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def move_to_dead_letter(
        self,
        event_id: str,
        payload: dict,
        error: str,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO dead_letter_events (
                    event_id,
                    payload,
                    error
                )
                VALUES (
                    $1,
                    $2::jsonb,
                    $3
                )
                """,
                event_id,
                json.dumps(payload),
                error,
            )
