from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Sequence

from parsers.base.models import RawItem, NormalizedItem


class Normalizer:
    async def normalize(
        self,
        items: Sequence[RawItem],
        source_id: str,
    ) -> Sequence[NormalizedItem]:
        result: list[NormalizedItem] = []

        for item in items:
            content_hash = hashlib.sha256(item.content.encode()).hexdigest()

            result.append(
                NormalizedItem(
                    source_id=source_id,
                    external_id=item.external_id,
                    title=item.title,
                    content=item.content,
                    url=item.url,
                    content_hash=content_hash,
                    published_at=item.published_at,
                    fetched_at=datetime.utcnow(),
                    media_url=item.media_url,
                )
            )

        return result
