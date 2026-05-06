from __future__ import annotations

import asyncio
from typing import Sequence

from parsers.base.parser import BaseParser
from parsers.base.models import RawItem
from parsers.smart_city.detectors.layout import LayoutDetector, LayoutType
from parsers.smart_city.generic_adapter.strategies import (
    ListStrategy,
    CardStrategy,
    TableStrategy,
)


class GenericSmartCityParser(BaseParser):
    """
    Production municipal parser:
    - layout detection
    - hybrid support
    - bounded detail fetch
    """

    def __init__(self, normalizer, client, config) -> None:
        super().__init__(normalizer, client, config)
        self._detector = LayoutDetector()
        self._detail_sem = asyncio.Semaphore(5)

    async def _fetch(self, ctx) -> Sequence[RawItem]:
        response = await self._get(ctx)
        html = response.text

        layout = self._detector.detect(html)

        if layout == LayoutType.LIST:
            strategy = ListStrategy()
        elif layout == LayoutType.CARD:
            strategy = CardStrategy()
        elif layout == LayoutType.TABLE:
            strategy = TableStrategy()
        else:
            return []

        items = await strategy.extract(html, ctx.url)

        # detail fetch pipeline (bounded)
        results: list[RawItem] = []
        for item in items:
            detailed = await self._enrich_detail(item)
            results.append(detailed)

        return results

    async def _enrich_detail(self, item: RawItem) -> RawItem:
        async with self._detail_sem:
            try:
                resp = await self._client.get(item.url)
                html = resp.text

                # naive extraction (safe fallback)
                content = html[:2000]

                return item.model_copy(update={"content": content})
            except Exception:
                return item
