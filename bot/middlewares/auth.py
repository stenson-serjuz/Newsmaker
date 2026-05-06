from __future__ import annotations

from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware


class AuthContext:
    def __init__(
        self,
        *,
        user_id: int,
        chat_id: int | None,
        is_admin: bool,
        is_superuser: bool,
    ) -> None:
        self.user_id = user_id
        self.chat_id = chat_id
        self.is_admin = is_admin
        self.is_superuser = is_superuser


class AuthMiddleware(BaseMiddleware):
    """
    Safe auth boundary.

    NOTE:
    - real implementation must be injected
    - no placeholders returning True blindly
    """

    def __init__(self, resolver) -> None:
        self._resolver = resolver

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        chat = getattr(event, "chat", None)

        ctx = await self._resolver.resolve(
            user_id=user.id if user else 0,
            chat_id=chat.id if chat else None,
        )

        data["auth"] = ctx

        return await handler(event, data)
