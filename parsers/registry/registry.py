from __future__ import annotations

from typing import Callable, Dict

from parsers.base.parser import BaseParser
from parsers.base.context import ParserContext


ParserFactory = Callable[[], BaseParser]


class ParserRegistry:
    def __init__(self) -> None:
        self._factories: Dict[str, ParserFactory] = {}

    def register(self, source_type: str, factory: ParserFactory) -> None:
        self._factories[source_type] = factory

    def get(self, source_type: str) -> BaseParser:
        if source_type not in self._factories:
            raise KeyError(f"Parser not found: {source_type}")

        return self._factories[source_type]()
