from __future__ import annotations

from typing import Sequence

from infrastructure.db.pool import (
    PostgresPool,
)

from infrastructure.db.transaction import (
    transaction,
)


class UserPreferenceRepository:
    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def match_users(
        self,
        *,
        city: str | None,
        category: str | None,
        language: str | None,
        urgency: str | None,
    ) -> Sequence[dict]:
        async with transaction(self._pool) as conn:
            rows = await conn.fetch(
                """
                SELECT
                    u.telegram_user_id,
                    u.tariff,
                    p.city,
                    p.category,
                    p.language,
                    p.urgency
                FROM users u
                JOIN user_preferences p
                    ON p.user_id = u.id
                WHERE
                    u.is_active = TRUE
                    AND (
                        p.city = $1
                        OR p.city IS NULL
                    )
                    AND (
                        p.category = $2
                        OR p.category IS NULL
                    )
                    AND (
                        p.language = $3
                        OR p.language IS NULL
                    )
                    AND (
                        p.urgency = $4
                        OR p.urgency IS NULL
                    )
                """,
                city,
                category,
                language,
                urgency,
            )

            return [
                dict(r)
                for r in rows
            ]
