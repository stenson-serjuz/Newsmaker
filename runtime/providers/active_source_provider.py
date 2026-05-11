from __future__ import annotations

from typing import Sequence

from sources.repositories.source_repository import (
    SourceRepositoryImpl,
)

from sources.repositories.health_repository import (
    HealthRepositoryImpl,
)


class ActiveSourceProvider:
    """
    Scheduler source provider.

    Combines:
    - source configuration
    - runtime health state
    """

    def __init__(
        self,
        source_repo: SourceRepositoryImpl,
        health_repo: HealthRepositoryImpl,
    ) -> None:
        self._sources = source_repo
        self._health = health_repo

    async def list_active(self) -> Sequence:
        sources = await self._sources.list_active()

        result = []

        for source in sources:
            health = await self._health.get(source.id)

            degraded = (
                health.is_degraded
                if health
                else False
            )

            result.append(
                source.model_copy(
                    update={
                        "is_degraded": degraded,
                    }
                )
            )

        return result
