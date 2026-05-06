from __future__ import annotations

from parsers.base.parser import BaseParser
from parsers.smart_city.detectors.layout import LayoutDetector, LayoutType
from parsers.smart_city.generic_adapter.strategies import (
    ListStrategy,
    CardStrategy,
)


class GenericSmartCityParser(BaseParser):
    def __init__(self, normalizer, client, config) -> None:
        super().__init__(normalizer, client, config)
        self._detector = LayoutDetector()

    async def _fetch(self, ctx):
        response = await self._get(ctx)

        html = response.text

        layout = self._detector.detect(html)

        if layout == LayoutType.LIST:
            strategy = ListStrategy()
        elif layout == LayoutType.CARD:
            strategy = CardStrategy()
        else:
            return []

        return await strategy.extract(html)
