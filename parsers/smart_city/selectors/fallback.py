from __future__ import annotations

from typing import Sequence
from bs4 import BeautifulSoup

from parsers.smart_city.selectors.base import SelectorResult


class FallbackSelector:
    """
    Fallback chain with confidence scoring.
    """

    def __init__(self, selectors: Sequence[str]) -> None:
        self._selectors = selectors

    def select(self, soup: BeautifulSoup) -> SelectorResult:
        best_nodes = []
        best_score = 0.0

        for idx, sel in enumerate(self._selectors):
            nodes = soup.select(sel)
            if nodes:
                score = 1.0 - (idx * 0.2)
                if score > best_score:
                    best_nodes = nodes
                    best_score = score

        return SelectorResult(best_nodes, best_score)
