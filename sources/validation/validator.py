from __future__ import annotations

import re
from urllib.parse import urlparse

from typing import Protocol, Sequence

from sources.models.source import SourceModel


class SourceRepository(Protocol):
    async def exists_by_url(self, url: str, tenant_id) -> bool: ...


class ParserCompatibility(Protocol):
    async def supports(self, parser_key: str, source_type: str) -> bool: ...


class SourceValidator:
    def __init__(
        self,
        repo: SourceRepository,
        compatibility: ParserCompatibility,
    ) -> None:
        self._repo = repo
        self._compat = compatibility

    def validate_url(self, url: str) -> None:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            raise ValueError("invalid_scheme")

        if not parsed.netloc:
            raise ValueError("invalid_host")

    async def validate_duplicate(self, url: str, tenant_id) -> None:
        exists = await self._repo.exists_by_url(url, tenant_id)
        if exists:
            raise ValueError("duplicate_source")

    async def validate_parser(self, parser_key: str, source_type: str) -> None:
        supported = await self._compat.supports(parser_key, source_type)
        if not supported:
            raise ValueError("parser_not_supported")
