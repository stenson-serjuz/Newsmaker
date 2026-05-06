from __future__ import annotations

import uuid
from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware

from core.logging.context import bind_trace_id, clear_trace_id


class TraceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        trace_id = str(uuid.uuid4())
        bind_trace_id(trace_id)
        data["trace_id"] = trace_id

        try:
            return await handler(event, data)
        finally:
            clear_trace_id()
