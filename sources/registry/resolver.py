from __future__ import annotations

from typing import Protocol

from parsers.registry.registry import ParserRegistry
from parsers.base.parser import BaseParser


class ParserResolver:
    """
    No global registry.
    Injected via DI.
    """

    def __init__(self, registry: ParserRegistry) -> None:
        self._registry = registry

    def resolve(self, parser_key: str) -> BaseParser:
        return self._registry.get(parser_key)
