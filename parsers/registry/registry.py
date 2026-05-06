from __future__ import annotations

from typing import Dict

from parsers.base.parser import BaseParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: Dict[str, BaseParser] = {}

    def register(self, source_type: str, parser: BaseParser) -> None:
        self._parsers[source_type] = parser

    def get(self, source_type: str) -> BaseParser:
        if source_type not in self._parsers:
            raise KeyError(f"Parser not found for type {source_type}")
        return self._parsers[source_type]
