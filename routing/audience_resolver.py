from __future__ import annotations

from typing import Sequence, Protocol

from subscriptions.models import Subscription
from subscriptions.service import SubscriptionService
from subscriptions.entitlements import EntitlementPolicy
from routing.targets import Target
from core.types.protocols import LoggerProtocol


class AudienceCache(Protocol):
    async def get(self, key: str) -> Sequence[Target] | None: ...
    async def set(self, key: str, value: Sequence[Target], ttl: int) -> None: ...


class AudienceResolver:
    """
    Resolves:
    - source → subscriptions → targets
    - applies entitlements
    - cache-ready
    """

    def __init__(
        self,
        subs: SubscriptionService,
        policy: EntitlementPolicy,
        logger: LoggerProtocol,
        cache: AudienceCache | None = None,
    ) -> None:
        self._subs = subs
        self._policy = policy
        self._cache = cache
        self._logger = logger.bind(component="audience_resolver")

    async def resolve(
        self,
        *,
        source_id: int,
        city: str | None,
        is_government: bool,
        category: str | None,
    ) -> Sequence[Target]:
        cache_key = f"audience:{source_id}:{city}:{category}"

        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                return cached

        result: list[Target] = []

        subs = await self._subs.by_source(source_id)

        if city:
            subs += await self._subs.by_city(city)

        for sub in subs:
            if sub.state != "active":
                continue

            if not self._policy.can_access_source(
                sub.tariff,
                is_government=is_government,
                has_city_scope=bool(sub.city),
            ):
                continue

            if category and sub.categories and category not in sub.categories:
                continue

            result.append(
                Target(
                    chat_id=sub.chat_id,
                    tenant_id=sub.tenant_id,
                )
            )

        if self._cache:
            await self._cache.set(cache_key, result, ttl=60)

        self._logger.info("audience_resolved", count=len(result))

        return result
