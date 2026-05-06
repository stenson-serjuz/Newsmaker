from __future__ import annotations

import httpx

from parsers.base.parser import BaseParser
from parsers.smart_city.strategies import Strategy, DefaultStrategy


class SmartCityParser(BaseParser):
    def __init__(self, normalizer, client: httpx.AsyncClient, strategy: Strategy | None = None) -> None:
        super().__init__(normalizer)
        self._client = client
        self._strategy = strategy or DefaultStrategy()

    async def _fetch(self, url: str):
        response = await self._client.get(url)
        return await self._strategy.extract(response.text)
