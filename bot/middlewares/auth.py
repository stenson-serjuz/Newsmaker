from __future__ import annotations

from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any


class AuthMiddleware(BaseMiddleware):
    """
    Tenant-safe boundary.

    NOTE:
    - real permission logic injected via services later
    """

    async def __call__(
        self,
        handler: Callable,
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        data["is_admin"] = True
        data["is_superuser"] = False
        return await handler(event, data)
