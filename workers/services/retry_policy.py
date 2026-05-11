from __future__ import annotations


class RetryPolicy:
    def next_delay(
        self,
        retry_count: int,
    ) -> int:
        delays = {
            1: 30,
            2: 120,
            3: 600,
            4: 1800,
        }

        return delays.get(retry_count, 3600)

    def should_dead_letter(
        self,
        retry_count: int,
    ) -> bool:
        return retry_count >= 5
