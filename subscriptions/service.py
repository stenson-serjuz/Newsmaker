from __future__ import annotations

from typing import Protocol, Sequence

from subscriptions.models import Subscription
from core.types.protocols import LoggerProtocol


class SubscriptionRepository(Protocol):
    async def get_active_by_source(self, source_id: int) -> Sequence[Subscription]: ...
    async def get_active_by_city(self, city: str) -> Sequence[Subscription]: ...


class SubscriptionService:
    """
    Orchestrates subscription access.

    - no DB implementation
    - repository injected
    """

    def __init__(
        self,
        repo: SubscriptionRepository,
        logger: LoggerProtocol,
    ) -> None:
        self._repo = repo
        self._logger = logger.bind(component="subscription_service")

    async def by_source(self, source_id: int) -> Sequence[Subscription]:
        subs = await self._repo.get_active_by_source(source_id)
        return subs

    async def by_city(self, city: str) -> Sequence[Subscription]:
        subs = await self._repo.get_active_by_city(city)
        return subs
