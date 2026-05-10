from __future__ import annotations

from typing import Sequence, Protocol
from uuid import UUID

from parsers.base.models import NormalizedItem
from infrastructure.queue.interfaces import ProducerProtocol

class DedupService(Protocol):
    async def is_duplicate(self, item: NormalizedItem) -> bool: ...


class EventDispatcher:
    """
    Dedup → enrich → publish
    """

    def __init__(
        self,
        producer: ProducerProtocol,
        dedup: DedupService,
        logger,
    ) -> None:
        self._producer = producer
        self._dedup = dedup
        self._logger = logger.bind(component="event_dispatcher")

    async def dispatch(
        self,
        source_id: UUID,
        items: Sequence[NormalizedItem],
    ) -> None:
        for item in items:
            if await self._dedup.is_duplicate(item):
                continue

            event = self._build_event(item)

            await self._producer.publish("events_stream", event)

        self._logger.info(
            "dispatch_complete",
            source_id=str(source_id),
            count=len(items),
        )

    def _build_event(self, item: NormalizedItem):
        return {
            "source_id": str(item.source_id),
            "external_id": item.external_id,
            "content": item.content,
            "hash": item.content_hash,
        }
