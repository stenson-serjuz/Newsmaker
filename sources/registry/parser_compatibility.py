from __future__ import annotations

from collections import defaultdict


class ParserCompatibilityRegistry:
    """
    Parser/source-type compatibility registry.
    """

    def __init__(self) -> None:
        self._mapping: dict[str, set[str]] = defaultdict(set)

    def register(
        self,
        parser_key: str,
        source_type: str,
    ) -> None:
        self._mapping[parser_key].add(source_type)

    async def supports(
        self,
        parser_key: str,
        source_type: str,
    ) -> bool:
        return source_type in self._mapping.get(parser_key, set())
