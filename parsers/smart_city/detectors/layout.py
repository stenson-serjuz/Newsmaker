from __future__ import annotations

from bs4 import BeautifulSoup


class LayoutType:
    LIST = "list"
    CARD = "card"
    UNKNOWN = "unknown"


class LayoutDetector:
    def detect(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")

        if soup.select(".board_list"):
            return LayoutType.LIST

        if soup.select(".card"):
            return LayoutType.CARD

        return LayoutType.UNKNOWN
