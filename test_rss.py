from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx

from parsers.base.context import ParserContext, ParserConfig
from parsers.normalizer import Normalizer
from parsers.rss.advanced_rss_parser import AdvancedRSSParser


async def main() -> None:
    client = httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
    )

    parser = AdvancedRSSParser(
        normalizer=Normalizer(),
        client=client,
        config=ParserConfig(
            timeout=20.0,
            max_items=10,
        ),
    )

    ctx = ParserContext(
        source_id=uuid4(),
        url="https://russian.korea.net/koreanet/rss/news/2",
    )

    items = await parser.parse(ctx)

    print(f"\nParsed items: {len(items)}\n")

    for idx, item in enumerate(items, start=1):
        print("=" * 80)
        print(f"ITEM #{idx}")
        print("=" * 80)

        print("TITLE:")
        print(item.title)
        print()

        print("URL:")
        print(item.url)
        print()

        print("CONTENT:")
        print(item.content[:500])
        print()

        print("HASH:")
        print(item.content_hash)
        print()

    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
