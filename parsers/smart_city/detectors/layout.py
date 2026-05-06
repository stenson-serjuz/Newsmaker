from __future__ import annotations

from bs4 import BeautifulSoup


class LayoutType:
    LIST = "list"
    CARD = "card"
    TABLE = "table"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class LayoutDetector:
    def detect(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")

        has_list = bool(soup.select(".board_list"))
        has_card = bool(soup.select(".card"))
        has_table = bool(soup.select("table"))

        if has_list and has_table:
            return LayoutType.HYBRID
        if has_table:
            return LayoutType.TABLE
        if has_list:
            return LayoutType.LIST
        if has_card:
            return LayoutType.CARD

        return LayoutType.UNKNOWN
