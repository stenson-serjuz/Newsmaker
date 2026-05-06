from __future__ import annotations

from typing import Sequence
from bs4 import BeautifulSoup

from parsers.base.models import RawItem


class ListStrategy:
    async def extract(self, html: str) -> Sequence[RawItem]:
        soup = BeautifulSoup(html, "lxml")

        items: list[RawItem] = []

        for li in soup.select(".board_list li"):
            link = li.select_one("a")
            if not link:
                continue

            items.append(
                RawItem(
                    external_id=link.get("href"),
                    title=link.text.strip(),
                    content="",
                    url=link.get("href"),
                )
            )

        return items


class CardStrategy:
    async def extract(self, html: str) -> Sequence[RawItem]:
        soup = BeautifulSoup(html, "lxml")

        items: list[RawItem] = []

        for card in soup.select(".card"):
            title = card.select_one(".title")
            if not title:
                continue

            items.append(
                RawItem(
                    external_id=title.text,
                    title=title.text,
                    content="",
                    url="",
                )
            )

        return items
