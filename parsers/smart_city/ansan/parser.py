from __future__ import annotations

from bs4 import BeautifulSoup

from parsers.base.parser import BaseParser
from parsers.base.models import RawItem
from parsers.smart_city.selectors.fallback import FallbackSelector
from parsers.smart_city.ansan.selectors import SELECTORS


class AnsanParser(BaseParser):
    async def _fetch(self, ctx):
        response = await self._get(ctx)

        soup = BeautifulSoup(response.text, "lxml")

        items_selector = FallbackSelector(SELECTORS["items"])
        nodes = items_selector.select(soup)

        result: list[RawItem] = []

        for node in nodes:
            link = node.select_one("a")
            if not link:
                continue

            title = link.text.strip()

            result.append(
                RawItem(
                    external_id=link.get("href"),
                    title=title,
                    content="",
                    url=link.get("href"),
                )
            )

        return result
