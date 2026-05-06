from __future__ import annotations

from typing import Protocol, Optional, Sequence
from bs4 import BeautifulSoup


class Selector(Protocol):
    def select(self, soup: BeautifulSoup) -> Sequence[BeautifulSoup]: ...


class FieldExtractor(Protocol):
    def extract(self, node: BeautifulSoup) -> Optional[str]: ...


class SelectorResult:
    def __init__(self, nodes: Sequence[BeautifulSoup], confidence: float) -> None:
        self.nodes = nodes
        self.confidence = confidence
