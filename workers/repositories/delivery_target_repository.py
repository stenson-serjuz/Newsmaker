from __future__ import annotations

from typing import Sequence

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class DeliveryTargetRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def find_targets(
        self,
        *,
        category: str | None,
        language: str | None,
        tariff: str | None,
    ) -> Sequence[dict]:
        async with transaction(self._pool) as conn:
            rows = await conn.fetch(
                """
                SELECT *
                FROM delivery_targets
                WHERE
                    is_active = TRUE
                    AND (
                        category = $1
                        OR category IS NULL
                    )
                    AND (
                        language = $2
                        OR language IS NULL
                    )
                    AND (
                        tariff = $3
                        OR tariff IS NULL
                    )
                """,
                category,
                language,
                tariff,
            )

            return [
                dict(r)
                for r in rows
            ]
