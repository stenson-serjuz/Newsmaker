from __future__ import annotations

import httpx

from parsers.base.context import ParserConfig
from parsers.normalizers.normalizer import Normalizer

from parsers.registry.registry import ParserRegistry

from parsers.rss.advanced_rss_parser import AdvancedRSSParser

from sources.registry.parser_compatibility import (
    ParserCompatibilityRegistry,
)


def build_parser_registry() -> ParserRegistry:
    registry = ParserRegistry()

    client = httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
    )

    registry.register(
        "advanced_rss",
        lambda: AdvancedRSSParser(
            normalizer=Normalizer(),
            client=client,
            config=ParserConfig(
                timeout=20.0,
                max_items=50,
            ),
        ),
    )

    return registry


def build_parser_compatibility() -> ParserCompatibilityRegistry:
    compatibility = ParserCompatibilityRegistry()

    compatibility.register(
        parser_key="advanced_rss",
        source_type="rss",
    )

    return compatibility
