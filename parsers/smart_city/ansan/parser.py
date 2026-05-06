from __future__ import annotations

from urllib.parse import urljoin
from bs4 import BeautifulSoup

from parsers.base.parser import BaseParser
from parsers.base.models import RawItem
from parsers.smart_city.selectors.fallback import FallbackSelector
from parsers.smart_city.ansan.selectors import SELECTORS


class AnsanParser(BaseParser):
    """
    Hardened Ansan parser:
    - URL normalization
    - selector fallback scoring
    - metadata extraction
    """

    async def _fetch(self, ctx):
        response = await self._get(ctx)

        soup = BeautifulSoup(response.text, "lxml")

        sel = FallbackSelector(SELECTORS["items"])
        result = sel.select(soup)

        items: list[RawItem] = []

        for node in result.nodes:
            link = node.select_one("a")
            if not link:
                continue

            href = link.get("href")
            url = urljoin(ctx.url, href)

            title = link.get_text(strip=True)

            # metadata extraction hooks
            category = node.get("data-category")

            items.append(
                RawItem(
                    external_id=url,
                    title=title,
                    content=category or "",
                    url=url,
                )
            )

        return items
