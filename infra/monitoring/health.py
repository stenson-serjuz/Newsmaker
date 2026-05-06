from __future__ import annotations

from typing import Protocol


class HealthCheck(Protocol):
    async def check(self) -> bool: ...


class HealthAggregator:
    def __init__(self, checks: list[HealthCheck]) -> None:
        self._checks = checks

    async def run(self) -> bool:
        results = await asyncio.gather(
            *(c.check() for c in self._checks),
            return_exceptions=True,
        )
        return all(r is True for r in results)
