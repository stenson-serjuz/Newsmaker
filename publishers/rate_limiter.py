from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from typing import Callable, Awaitable


class RateLimiter:
    """
    Concurrency-safe rate limiter.

    - lock-protected
    - ready for Redis-backed replacement
    - provides pressure hooks
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

        self._lock = asyncio.Lock()

    async def acquire(self, chat_id: int) -> float:
        async with self._lock:
            now = time.time()

            chat_delay = max(0.0, (1 / self._per_chat_rate) - (now - self._chat_last[chat_id]))
            global_delay = max(0.0, (1 / self._global_rate) - (now - self._global_last))

            delay = max(chat_delay, global_delay)

            if delay > 0:
                await asyncio.sleep(delay)

            now = time.time()

            self._chat_last[chat_id] = now
            self._global_last = now

            return delay

    def pressure(self) -> float:
        """
        Backpressure signal:
        - simple heuristic based on global timestamp skew
        """
        return time.time() - self._global_last
