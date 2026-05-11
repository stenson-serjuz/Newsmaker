from __future__ import annotations

from typing import Sequence

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class SubscriptionRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def get_active_chat_ids(
        self,
    ) -> Sequence[int]:
        async with transaction(self._pool) as conn:
            rows = await conn.fetch(
                """
                SELECT chat_id
                FROM telegram_subscriptions
                WHERE is_active = TRUE
                """
            )

            return [
                row["chat_id"]
                for row in rows
            ]
