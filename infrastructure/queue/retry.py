from __future__ import annotations

import time
import random

from contracts.events.retry import RetryMetadata


class RetryPolicy:
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ) -> None:
        self._base = base_delay
        self._max = max_delay

    def next(self, meta: RetryMetadata) -> RetryMetadata:
        attempt = meta.attempt + 1

        exp = min(self._base * (2 ** attempt), self._max)
        jitter = random.uniform(0, exp * 0.1)

        delay = exp + jitter

        return RetryMetadata(
            attempt=attempt,
            max_attempts=meta.max_attempts,
            next_attempt_at=int(time.time() + delay),
            last_error=meta.last_error,
        )

    def is_exhausted(self, meta: RetryMetadata) -> bool:
        return meta.attempt >= meta.max_attempts
