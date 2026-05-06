from __future__ import annotations

import asyncio
import time
from collections import defaultdict


class RateLimiter:
    """
    Token bucket style limiter (in-memory)

    NOTE:
    - Redis-based limiter can replace this later
    """

    def __init__(
        self,
        per_chat_rate: float = 1.0,
        global_rate: float = 30.0,
    ) -> None:
        self._per_chat_rate = per_chat_rate
        self._global_rate = global_rate

        self._chat_last: dict[int, float] = defaultdict(float)
        self._global_last: float = 0.0

    async def acquire(self, chat_id: int) -> None:
        now = time.time()

        chat_delay = max(0.0, (1 / self._per_chat_rate) - (now - self._chat_last[chat_id]))
        global_delay = max(0.0, (1 / self._global_rate) - (now - self._global_last))

        delay = max(chat_delay, global_delay)

        if delay > 0:
            await asyncio.sleep(delay)

        self._chat_last[chat_id] = time.time()
        self._global_last = time.time()
