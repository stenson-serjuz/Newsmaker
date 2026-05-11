from __future__ import annotations

from workers.repositories.delivery_target_repository import (
    DeliveryTargetRepository,
)


class DeliveryRouter:
    def __init__(
        self,
        targets: DeliveryTargetRepository,
    ) -> None:
        self._targets = targets

    async def resolve(
        self,
        *,
        category: str | None,
        language: str | None,
        tariff: str | None,
    ) -> list[dict]:
        rows = await self._targets.find_targets(
            category=category,
            language=language,
            tariff=tariff,
        )

        return rows
