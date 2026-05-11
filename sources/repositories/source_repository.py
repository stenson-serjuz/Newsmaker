from __future__ import annotations

from uuid import UUID

from sources.models.source import SourceModel

from database.models.enums import SourceTypeEnum

from infrastructure.db.pool import PostgresPool
from infrastructure.db.transaction import transaction


class SourceRepositoryImpl:
    """
    Source configuration repository.

    Uses asyncpg because:
    - scheduler/runtime hot-path
    - lightweight reads
    - predictable performance
    """

    def __init__(
        self,
        pool: PostgresPool,
    ) -> None:
        self._pool = pool

    async def add(
        self,
        source: SourceModel,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                INSERT INTO sources (
                    id,
                    name,
                    type,
                    url,
                    parser,
                    is_active
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                source.id,
                source.name,
                source.type.value,
                str(source.url),
                source.parser_key,
                source.is_active,
            )

    async def update(
        self,
        source: SourceModel,
    ) -> None:
        async with transaction(self._pool) as conn:
            await conn.execute(
                """
                UPDATE sources
                SET
                    name = $2,
                    type = $3,
                    url = $4,
                    parser = $5,
                    is_active = $6
                WHERE id = $1
                """,
                source.id,
                source.name,
                source.type.value,
                str(source.url),
                source.parser_key,
                source.is_active,
            )

    async def get(
        self,
        source_id: UUID,
    ) -> SourceModel | None:
        async with transaction(self._pool) as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    id,
                    name,
                    type,
                    url,
                    parser,
                    is_active
                FROM sources
                WHERE id = $1
                """,
                source_id,
            )

        if not row:
            return None

        return SourceModel(
            id=row["id"],
            name=row["name"],
            type=SourceTypeEnum(row["type"]),
            url=row["url"],
            parser_key=row["parser"],
            is_active=row["is_active"],
        )

    async def exists_by_url(
        self,
        url: str,
    ) -> bool:
        async with transaction(self._pool) as conn:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM sources
                WHERE url = $1
                LIMIT 1
                """,
                url,
            )

        return row is not None

    async def list_active(self) -> list[SourceModel]:
        async with transaction(self._pool) as conn:
            rows = await conn.fetch(
                """
                SELECT
                    id,
                    name,
                    type,
                    url,
                    parser,
                    is_active
                FROM sources
                WHERE is_active = TRUE
                """
            )

        return [
            SourceModel(
                id=row["id"],
                name=row["name"],
                type=SourceTypeEnum(row["type"]),
                url=row["url"],
                parser_key=row["parser"],
                is_active=row["is_active"],
            )
            for row in rows
        ]
