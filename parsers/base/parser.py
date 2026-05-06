from __future__ import annotations

import asyncio
from typing import Sequence, Protocol

from parsers.base.models import RawItem, NormalizedItem
from parsers.base.errors import ParserError


class NormalizerProtocol(Protocol):
    async def normalize(self, items: Sequence[RawItem], source_id: str) -> Sequence[NormalizedItem]: ...


class BaseParser:
    def __init__(
        self,
        normalizer: NormalizerProtocol,
        *,
        timeout: float = 10.0,
    ) -> None:
        self._normalizer = normalizer
        self._timeout = timeout

    async def parse(self, source_id: str) -> Sequence[NormalizedItem]:
        try:
            async with asyncio.timeout(self._timeout):
                raw = await self._fetch(source_id)
                return await self._normalizer.normalize(raw, source_id)

        except asyncio.TimeoutError:
            raise ParserError("timeout")

    async def _fetch(self, source_id: str) -> Sequence[RawItem]:
        raise NotImplementedError
