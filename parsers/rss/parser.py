from __future__ import annotations

import httpx
import feedparser

from parsers.base.parser import BaseParser
from parsers.base.models import RawItem


class RSSParser(BaseParser):
    def __init__(self, normalizer, client: httpx.AsyncClient) -> None:
        super().__init__(normalizer)
        self._client = client

    async def _fetch(self, source_url: str):
        response = await self._client.get(source_url)

        parsed = feedparser.parse(response.text)

        items: list[RawItem] = []

        for entry in parsed.entries:
            items.append(
                RawItem(
                    external_id=entry.get("id", entry.get("link")),
                    title=entry.get("title", ""),
                    content=entry.get("summary", ""),
                    url=entry.get("link", ""),
                )
            )

        return items
