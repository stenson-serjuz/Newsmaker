from __future__ import annotations

from parsers.base.parser import BaseParser
from parsers.smart_city.strategies import StrategyResolver


class SmartCityParser(BaseParser):
    def __init__(self, normalizer, client, config, resolver: StrategyResolver) -> None:
        super().__init__(normalizer, client, config)
        self._resolver = resolver

    async def _fetch(self, ctx):
        response = await self._get(ctx)

        strategy = await self._resolver.resolve(response.text)

        return await strategy.extract(response.text)
