from __future__ import annotations

from uuid import UUID

from sources.models.health import SourceHealth

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class HealthRepositoryImpl:
    """
    Runtime source health persistence.

    Uses asyncpg directly because:
    - high-frequency scheduler writes
    - lightweight operational state
    - runtime-critical hot path
    """

    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def get(
        self,
        source_id: UUID,
    ) -> SourceHealth | None:
        async with transaction(self._pool) as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    last_success_at,
                    last_error_at,
                    failure_count,
                    is_degraded
                FROM source_health
                WHERE source_id = $1
                """,
                source_id,
            )

        if not row:
            return None

        return SourceHealth(
            last_success_at=row["last_success_at"],
            last_error_at=row["last_error_at"],
            failure_count=row["failure_count"],
            is_degraded=row["is_degraded"],
        )

    async def save(
        self,
        source_id: UUID,
        health: SourceHealth,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO source_health (
                    source_id,
                    last_success_at,
                    last_error_at,
                    failure_count,
                    is_degraded
                )
                VALUES ($1, $2, $3, $4, $5)

                ON CONFLICT (source_id)
                DO UPDATE SET
                    last_success_at = EXCLUDED.last_success_at,
                    last_error_at = EXCLUDED.last_error_at,
                    failure_count = EXCLUDED.failure_count,
                    is_degraded = EXCLUDED.is_degraded,
                    updated_at = NOW()
                """,
                source_id,
                health.last_success_at,
                health.last_error_at,
                health.failure_count,
                health.is_degraded,
            )
