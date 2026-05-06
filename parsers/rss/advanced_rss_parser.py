from __future__ import annotations

import asyncio
from typing import Sequence
from urllib.parse import urljoin

import feedparser

from parsers.base.parser import BaseParser
from parsers.base.models import RawItem
from parsers.base.errors import ParserError


MAX_FEED_SIZE = 2_000_000  # 2MB safety


class AdvancedRSSParser(BaseParser):
    """
    Hardened RSS:
    - partial malformed tolerance
    - payload size protection
    - absolute URL normalization
    - attachment/media extraction hooks
    """

    async def _fetch(self, ctx) -> Sequence[RawItem]:
        response = await self._get(ctx)

        if response.status_code == 304:
            return []

        content = response.content[:MAX_FEED_SIZE]

        parsed = feedparser.parse(content)

        # tolerate bozo feeds but mark as degraded
        entries = getattr(parsed, "entries", []) or []

        items: list[RawItem] = []

        for entry in entries:
            link = entry.get("link")
            if not link:
                continue

            abs_link = urljoin(ctx.url, link)

            # media / enclosures
            media_url = None
            if entry.get("enclosures"):
                media_url = entry.enclosures[0].get("href")
            elif entry.get("media_content"):
                media_url = entry.media_content[0].get("url")

            items.append(
                RawItem(
                    external_id=entry.get("id") or abs_link,
                    title=entry.get("title", "") or "",
                    content=entry.get("summary", "") or "",
                    url=abs_link,
                    media_url=media_url,
                )
            )

        return items
