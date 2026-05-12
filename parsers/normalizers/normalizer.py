from __future__ import annotations

import hashlib
import re
import unicodedata

from datetime import (
    datetime,
    timezone,
)

from typing import Sequence
from uuid import UUID

from parsers.base.models import (
    RawItem,
    NormalizedItem,
)

from parsers.media.fetcher import (
    fetch_html,
)

from parsers.media.extractor import (
    extract_og_image,
)


MAX_CONTENT_SIZE = 50_000


class Normalizer:
    def _clean_html(
        self,
        text: str,
    ) -> str:
        text = re.sub(
            r"<[^>]+>",
            "",
            text,
        )

        return text

    def _normalize(
        self,
        text: str,
    ) -> str:
        text = unicodedata.normalize(
            "NFKC",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        return text

    def _hash(
        self,
        text: str,
    ) -> str:
        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    async def normalize(
        self,
        items: Sequence[RawItem],
        source_id: UUID,
    ) -> Sequence[NormalizedItem]:
        result: list[
            NormalizedItem
        ] = []

        for item in items:
            content = self._clean_html(
                item.content,
            )

            content = self._normalize(
                content,
            )

            if (
                len(content)
                > MAX_CONTENT_SIZE
            ):
                content = content[
                    :MAX_CONTENT_SIZE
                ]

            media_url = item.media_url

            if (
                not media_url
                and item.url
            ):
                html = await fetch_html(
                    item.url,
                )

                if html:
                    media_url = (
                        extract_og_image(
                            html,
                        )
                    )

            result.append(
                NormalizedItem(
                    source_id=source_id,
                    external_id=item.external_id,
                    title=self._normalize(
                        item.title,
                    ),
                    content=content,
                    url=item.url,
                    content_hash=self._hash(
                        content,
                    ),
                    published_at=item.published_at,
                    fetched_at=datetime.now(
                        timezone.utc,
                    ),
                    media_url=media_url,
                )
            )

        return result
