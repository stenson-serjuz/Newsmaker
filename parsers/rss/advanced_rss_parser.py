from __future__ import annotations

import feedparser
from typing import Sequence

from parsers.base.parser import BaseParser
from parsers.base.models import RawItem
from parsers.base.errors import ParserError


class AdvancedRSSParser(BaseParser):
    async def _fetch(self, ctx) -> Sequence[RawItem]:
        response = await self._get(ctx)

        if response.status_code == 304:
            return []

        parsed = feedparser.parse(response.content)

        if parsed.bozo:
            raise ParserError("rss_malformed")

        items: list[RawItem] = []

        for entry in parsed.entries:
            link = entry.get("link")
            if not link:
                continue

            media = None
            if "media_content" in entry:
                media = entry.media_content[0].get("url")

            items.append(
                RawItem(
                    external_id=entry.get("id") or link,
                    title=entry.get("title", ""),
                    content=entry.get("summary", ""),
                    url=link,
                    media_url=media,
                )
            )

        return items
