from __future__ import annotations

import httpx

from parsers.base.parser import BaseParser


class GovernmentParser(BaseParser):
    def __init__(self, normalizer, client: httpx.AsyncClient) -> None:
        super().__init__(normalizer)
        self._client = client

    async def _fetch(self, url: str):
        response = await self._client.get(url)
        return []
