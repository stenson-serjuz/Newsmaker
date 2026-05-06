from __future__ import annotations

from typing import Protocol, Sequence
from parsers.base.models import RawItem


class Strategy(Protocol):
    async def extract(self, html: str) -> Sequence[RawItem]: ...


class DefaultStrategy:
    async def extract(self, html: str) -> Sequence[RawItem]:
        return []  # placeholder
