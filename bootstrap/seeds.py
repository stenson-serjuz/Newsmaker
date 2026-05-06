from __future__ import annotations

import asyncio
from uuid import uuid4

from database.models.enums import SourceTypeEnum
from sources.models.source import SourceModel


RSS_SOURCE_ID = uuid4()
ANSAN_SOURCE_ID = uuid4()


async def seed_sources(service):
    """
    One RSS + one Ansan source
    """

    rss = SourceModel(
        id=RSS_SOURCE_ID,
        tenant_id=None,
        name="RSS Test",
        type=SourceTypeEnum.RSS,
        url="https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        parser_key="rss",
        is_active=True,
    )

    ansan = SourceModel(
        id=ANSAN_SOURCE_ID,
        tenant_id=None,
        name="Ansan",
        type=SourceTypeEnum.CITY,
        url="https://www.ansan.go.kr/www/boardList.do",
        parser_key="ansan",
        is_active=True,
    )

    await service.create(rss)
    await service.create(ansan)
