from __future__ import annotations

from typing import Sequence
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from parsers.base.models import RawItem


def _abs(base: str, href: str | None) -> str:
    return urljoin(base, href or "")


class ListStrategy:
    async def extract(self, html: str, base_url: str) -> Sequence[RawItem]:
        soup = BeautifulSoup(html, "lxml")
        items: list[RawItem] = []

        for li in soup.select(".board_list li"):
            a = li.select_one("a")
            if not a:
                continue

            href = a.get("href")
            url = _abs(base_url, href)
            title = a.get_text(strip=True)

            items.append(
                RawItem(
                    external_id=url,
                    title=title,
                    content="",
                    url=url,
                )
            )

        return items


class CardStrategy:
    async def extract(self, html: str, base_url: str) -> Sequence[RawItem]:
        soup = BeautifulSoup(html, "lxml")
        items: list[RawItem] = []

        for card in soup.select(".card"):
            title_el = card.select_one(".title")
            link = card.select_one("a")

            if not title_el or not link:
                continue

            href = link.get("href")
            url = _abs(base_url, href)

            items.append(
                RawItem(
                    external_id=url,
                    title=title_el.get_text(strip=True),
                    content="",
                    url=url,
                )
            )

        return items


class TableStrategy:
    async def extract(self, html: str, base_url: str) -> Sequence[RawItem]:
        soup = BeautifulSoup(html, "lxml")
        items: list[RawItem] = []

        for row in soup.select("table tr"):
            link = row.select_one("a")
            if not link:
                continue

            href = link.get("href")
            url = _abs(base_url, href)

            items.append(
                RawItem(
                    external_id=url,
                    title=link.get_text(strip=True),
                    content="",
                    url=url,
                )
            )

        return items
