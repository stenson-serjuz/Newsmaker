from __future__ import annotations

from typing import Sequence, Protocol
from uuid import UUID, uuid4

from parsers.base.models import NormalizedItem

from infrastructure.queue.interfaces import (
    ProducerProtocol,
)

from contracts.events.envelope import EventEnvelope
from contracts.events.retry import RetryMetadata
from contracts.events.delivery import DeliveryMetadata


class DedupService(Protocol):
    async def is_duplicate(
        self,
        item: NormalizedItem,
    ) -> bool:
        ...


class EventDispatcher:
    """
    Dedup -> envelope -> publish
    """

    def __init__(
        self,
        producer: ProducerProtocol,
        dedup: DedupService,
        logger,
    ) -> None:
        self._producer = producer
        self._dedup = dedup
        self._logger = logger.bind(
            component="event_dispatcher",
        )

    async def dispatch(
        self,
        source_id: UUID,
        items: Sequence[NormalizedItem],
    ) -> None:
        published = 0

        for item in items:
            if await self._dedup.is_duplicate(item):
                continue

            event = self._build_event(item)

            await self._producer.publish(
                "events_stream",
                event,
            )

            published += 1

        self._logger.info(
            "dispatch_complete",
            source_id=str(source_id),
            count=published,
        )

    def _build_event(
        self,
        item: NormalizedItem,
    ) -> EventEnvelope:
        return EventEnvelope(
            schema_version=1,
            event_id=str(uuid4()),
            trace_id=None,
            payload={
                "source_id": str(item.source_id),
                "external_id": item.external_id,
                "title": item.title,
                "content": item.content,
                "url": item.url,
                "content_hash": item.content_hash,
            },
            metadata={
                "published_at": (
                    item.published_at.isoformat()
                    if item.published_at
                    else None
                ),
                "fetched_at": (
                    item.fetched_at.isoformat()
                    if item.fetched_at
                    else None
                ),
                "media_url": item.media_url,
            },
            retry=RetryMetadata(
                retry_count=0,
                max_retries=3,
            ),
            delivery=DeliveryMetadata(
                status="pending",
            ),
        )
