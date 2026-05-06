from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models.subscriptions import Subscription


class SubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def by_source(self, source_id: int) -> list[Subscription]:
        result = await self._session.execute(
            select(Subscription).where(
                Subscription.source_id == source_id,
                Subscription.is_active == True,
            )
        )
        return list(result.scalars().all())
