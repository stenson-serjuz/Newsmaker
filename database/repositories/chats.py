from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models.chats import Chat


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(
        self,
        telegram_id: int,
    ) -> Chat | None:
        result = await self._session.execute(
            select(Chat).where(Chat.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        tenant_id,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Chat]:
        result = await self._session.execute(
            select(Chat)
            .where(Chat.tenant_id == tenant_id, Chat.is_active == True)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def add(self, chat: Chat) -> None:
        self._session.add(chat)
