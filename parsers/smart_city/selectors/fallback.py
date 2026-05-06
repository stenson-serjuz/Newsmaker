from __future__ import annotations

from typing import Sequence
from bs4 import BeautifulSoup


class FallbackSelector:
    def __init__(self, selectors: Sequence[str]) -> None:
        self._selectors = selectors

    def select(self, soup: BeautifulSoup):
        for sel in self._selectors:
            nodes = soup.select(sel)
            if nodes:
                return nodes
        return []
