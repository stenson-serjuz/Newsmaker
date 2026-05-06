from __future__ import annotations

import uuid
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any

from core.logging.context import bind_trace_id


class TraceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        trace_id = str(uuid.uuid4())
        bind_trace_id(trace_id)
        data["trace_id"] = trace_id
        return await handler(event, data)
