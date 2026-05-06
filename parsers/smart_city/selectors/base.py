from __future__ import annotations

from typing import Protocol, Optional
from bs4 import BeautifulSoup


class Selector(Protocol):
    def select(self, soup: BeautifulSoup) -> list[BeautifulSoup]: ...


class FieldExtractor(Protocol):
    def extract(self, node: BeautifulSoup) -> Optional[str]: ...
