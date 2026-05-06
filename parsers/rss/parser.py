from __future__ import annotations

import feedparser

from parsers.base.parser import BaseParser
from parsers.base.models import RawItem
from parsers.base.errors import ParserError


class RSSParser(BaseParser):
    async def _fetch(self, ctx):
        response = await self._get(ctx)

        if response.status_code == 304:
            return []

        parsed = feedparser.parse(response.text)

        if parsed.bozo:
            raise ParserError("malformed_feed")

        items: list[RawItem] = []

        for entry in parsed.entries:
            if "title" not in entry or "link" not in entry:
                continue

            items.append(
                RawItem(
                    external_id=entry.get("id") or entry.get("link"),
                    title=entry.get("title", ""),
                    content=entry.get("summary", ""),
                    url=entry.get("link"),
                )
            )

        return items
